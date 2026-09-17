#!/usr/bin/env python3

import asyncio
import io
import json
import os
import threading
import time
from pathlib import Path

import cv2
import qrcode
import rclpy

from aiohttp import web
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image, Joy
from std_msgs.msg import Bool, Float32, Float64


class WebServer(Node):

    def __init__(self):
        super().__init__("web_server")

        # Grundeinstellungen
        self.port = 8080
        self.publish_frequency = 50.0
        self.input_timeout = 0.30
        self.jpeg_quality = 65

        self.public_host = os.environ.get(
            "IOT_CAR_HOST_IP",
            "",
        )

        self.network_name = os.environ.get(
            "IOT_CAR_NETWORK_NAME",
            "Unbekannt",
        )

        self.state_lock = threading.Lock()
        self.camera_lock = threading.Lock()
        self.telemetry_lock = threading.Lock()

        self.steering = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.emergency_stop = False

        self.last_input_time = 0.0
        self.client_connected = False

        self.camera_clients = 0
        self.camera_frame_id = 0
        self.latest_camera_jpeg = None

        self.speed_kmh = None
        self.distance = None
        self.distance_valid = False

        self.cv_bridge = CvBridge()

        self.publisher = self.create_publisher(
            Joy,
            "/control/input",
            10,
        )

        self.camera_subscription = self.create_subscription(
            Image,
            "/car/camera/image",
            self.camera_callback,
            10,
        )

        self.speed_subscription = self.create_subscription(
            Float64,
            "/car/speed_kmh",
            self.speed_callback,
            10,
        )

        self.distance_subscription = self.create_subscription(
            Float32,
            "/car/distance",
            self.distance_callback,
            10,
        )

        self.distance_valid_subscription = self.create_subscription(
            Bool,
            "/car/distance_valid",
            self.distance_valid_callback,
            10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_frequency,
            self.publish_control,
        )

        package_share = Path(
            get_package_share_directory(
                "iot_car_description"
            )
        )

        self.web_root = package_share / "web"

        self.web_thread = threading.Thread(
            target=self.run_web_server,
            daemon=True,
        )

        self.web_thread.start()

        self.get_logger().info(
            f"Webserver läuft auf Port {self.port}"
        )


    def clamp(self, value, minimum, maximum):
        return max(
            minimum,
            min(maximum, value),
        )


    def speed_callback(self, message):
        with self.telemetry_lock:
            self.speed_kmh = float(
                message.data
            )


    def distance_callback(self, message):
        with self.telemetry_lock:
            self.distance = float(
                message.data
            )


    def distance_valid_callback(self, message):
        with self.telemetry_lock:
            self.distance_valid = bool(
                message.data
            )


    def camera_callback(self, message):
        with self.camera_lock:
            if self.camera_clients <= 0:
                return

        try:
            frame = self.cv_bridge.imgmsg_to_cv2(
                message,
                desired_encoding="bgr8",
            )

            success, encoded = cv2.imencode(
                ".jpg",
                frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    self.jpeg_quality,
                ],
            )

            if not success:
                return

            with self.camera_lock:
                self.latest_camera_jpeg = (
                    encoded.tobytes()
                )

                self.camera_frame_id += 1

        except Exception as error:
            self.get_logger().warning(
                f"Kamerabild konnte nicht verarbeitet werden: {error}"
            )


    def get_control_url(self, request=None):
        host = self.public_host

        if not host and request is not None:
            host = request.host.split(":")[0]

        if not host:
            host = "localhost"

        return (
            f"http://{host}:{self.port}/control"
        )


    def set_control_state(
        self,
        steering,
        throttle,
        brake,
        emergency_stop,
    ):
        with self.state_lock:
            self.steering = self.clamp(
                float(steering),
                -1.0,
                1.0,
            )

            self.throttle = self.clamp(
                float(throttle),
                0.0,
                1.0,
            )

            self.brake = self.clamp(
                float(brake),
                0.0,
                1.0,
            )

            self.emergency_stop = bool(
                emergency_stop
            )

            self.last_input_time = (
                time.monotonic()
            )


    def publish_control(self):
        now = time.monotonic()

        with self.state_lock:
            input_is_fresh = (
                self.client_connected
                and (
                    now
                    - self.last_input_time
                    <= self.input_timeout
                )
            )

            if input_is_fresh:
                steering = self.steering
                throttle = self.throttle
                brake = self.brake
                emergency_stop = self.emergency_stop

            else:
                steering = 0.0
                throttle = 0.0
                brake = 0.0
                emergency_stop = False

        message = Joy()

        message.header.stamp = (
            self.get_clock().now().to_msg()
        )

        message.axes = [
            float(steering),
            float(throttle),
            float(brake),
        ]

        message.buttons = [
            int(emergency_stop),
        ]

        self.publisher.publish(message)


    def emergency_stop_vehicle(self):
        self.set_control_state(
            0.0,
            0.0,
            0.0,
            True,
        )

        self.publish_control()


    async def index_handler(self, request):
        raise web.HTTPFound("/info")


    async def info_handler(self, request):
        return web.FileResponse(
            self.web_root
            / "templates"
            / "info.html"
        )


    async def control_handler(self, request):
        return web.FileResponse(
            self.web_root
            / "templates"
            / "control.html"
        )


    async def api_info_handler(self, request):
        control_url = self.get_control_url(
            request
        )

        return web.json_response(
            {
                "port": self.port,
                "public_host": self.public_host,
                "network_name": self.network_name,
                "control_url": control_url,
            }
        )


    async def qr_handler(self, request):
        qr = qrcode.QRCode(
            box_size=8,
            border=3,
        )

        qr.add_data(
            self.get_control_url(request)
        )

        qr.make(
            fit=True
        )

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="PNG",
        )

        return web.Response(
            body=buffer.getvalue(),
            content_type="image/png",
        )


    async def websocket_handler(self, request):
        websocket = web.WebSocketResponse(
            heartbeat=10.0,
            compress=False,
        )

        await websocket.prepare(
            request
        )

        with self.state_lock:
            self.client_connected = True
            self.last_input_time = time.monotonic()

        try:
            async for message in websocket:

                if message.type != web.WSMsgType.TEXT:
                    continue

                try:
                    data = json.loads(
                        message.data
                    )

                    self.set_control_state(
                        data.get("steering", 0.0),
                        data.get("throttle", 0.0),
                        data.get("brake", 0.0),
                        data.get(
                            "emergency_stop",
                            False,
                        ),
                    )

                except (
                    ValueError,
                    TypeError,
                    json.JSONDecodeError,
                ):
                    continue

        finally:
            with self.state_lock:
                self.client_connected = False

            self.emergency_stop_vehicle()

        return websocket


    async def telemetry_websocket_handler(
        self,
        request,
    ):
        websocket = web.WebSocketResponse(
            heartbeat=10.0,
            compress=False,
        )

        await websocket.prepare(
            request
        )

        try:
            while not websocket.closed:

                with self.telemetry_lock:
                    speed_kmh = self.speed_kmh
                    distance = self.distance
                    distance_valid = (
                        self.distance_valid
                    )

                await websocket.send_json(
                    {
                        "speed_kmh":
                            speed_kmh,

                        "distance":
                            distance,

                        "distance_valid":
                            distance_valid,
                    }
                )

                await asyncio.sleep(
                    0.1
                )

        except (
            ConnectionResetError,
            RuntimeError,
            asyncio.CancelledError,
        ):
            pass

        return websocket


    async def camera_websocket_handler(
        self,
        request,
    ):
        websocket = web.WebSocketResponse(
            heartbeat=10.0,
            compress=False,
        )

        await websocket.prepare(
            request
        )

        with self.camera_lock:
            self.camera_clients += 1

        last_frame_id = -1

        try:
            while not websocket.closed:

                frame_data = None
                frame_id = last_frame_id

                with self.camera_lock:
                    if (
                        self.latest_camera_jpeg
                        is not None
                        and self.camera_frame_id
                        != last_frame_id
                    ):
                        frame_data = (
                            self.latest_camera_jpeg
                        )

                        frame_id = (
                            self.camera_frame_id
                        )

                if frame_data is not None:
                    await websocket.send_bytes(
                        frame_data
                    )

                    last_frame_id = frame_id

                await asyncio.sleep(
                    0.005
                )

        except (
            ConnectionResetError,
            RuntimeError,
            asyncio.CancelledError,
        ):
            pass

        finally:
            with self.camera_lock:
                self.camera_clients = max(
                    0,
                    self.camera_clients - 1,
                )

        return websocket


    async def create_app(self):
        app = web.Application()

        app.router.add_get(
            "/",
            self.index_handler,
        )

        app.router.add_get(
            "/info",
            self.info_handler,
        )

        app.router.add_get(
            "/control",
            self.control_handler,
        )

        app.router.add_get(
            "/api/info",
            self.api_info_handler,
        )

        app.router.add_get(
            "/api/qr.png",
            self.qr_handler,
        )

        app.router.add_get(
            "/ws",
            self.websocket_handler,
        )

        app.router.add_get(
            "/telemetry-ws",
            self.telemetry_websocket_handler,
        )

        app.router.add_get(
            "/camera-ws",
            self.camera_websocket_handler,
        )

        app.router.add_static(
            "/static/",
            self.web_root / "static",
            follow_symlinks=True,
        )

        return app


    def run_web_server(self):

        async def start_server():
            app = await self.create_app()

            runner = web.AppRunner(
                app
            )

            await runner.setup()

            site = web.TCPSite(
                runner,
                "0.0.0.0",
                self.port,
            )

            await site.start()

            while rclpy.ok():
                await asyncio.sleep(
                    0.5
                )

            await runner.cleanup()

        asyncio.run(
            start_server()
        )


def main(args=None):
    rclpy.init(args=args)

    node = WebServer()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.emergency_stop_vehicle()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
