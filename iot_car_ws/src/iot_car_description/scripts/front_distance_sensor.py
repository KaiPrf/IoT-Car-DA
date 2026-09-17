#!/usr/bin/env python3

import math

import rclpy

from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, Float32


class FrontDistanceSensor(Node):

    def __init__(self):
        super().__init__("front_distance_sensor")

        # Sensorgrenzen
        self.maximum_distance = 4.0
        self.contact_distance = 0.06

        self.last_distance = None

        self.distance_publisher = self.create_publisher(
            Float32,
            "/car/distance",
            10,
        )

        self.valid_publisher = self.create_publisher(
            Bool,
            "/car/distance_valid",
            10,
        )

        self.subscription = self.create_subscription(
            LaserScan,
            "/car/front_scan",
            self.scan_callback,
            10,
        )

        self.get_logger().info(
            "Front-Abstandssensor gestartet"
        )


    def scan_callback(self, message):
        valid_ranges = [
            value
            for value in message.ranges
            if (
                math.isfinite(value)
                and value >= message.range_min
                and value <= message.range_max
            )
        ]

        distance_message = Float32()
        valid_message = Bool()

        if valid_ranges:
            distance = min(valid_ranges)

            if distance <= self.contact_distance:
                distance = 0.0

            # Unplausiblen Sprung direkt nach Wandkontakt unterdrücken
            if (
                self.last_distance is not None
                and self.last_distance <= 0.08
                and distance > 0.40
            ):
                distance = 0.0

            self.last_distance = distance

            distance_message.data = float(
                round(distance, 3)
            )

            valid_message.data = True

        else:
            if (
                self.last_distance is not None
                and self.last_distance <= 0.08
            ):
                distance_message.data = 0.0
                valid_message.data = True

            else:
                distance_message.data = (
                    self.maximum_distance
                )

                valid_message.data = False

                self.last_distance = None

        self.distance_publisher.publish(
            distance_message
        )

        self.valid_publisher.publish(
            valid_message
        )


def main(args=None):
    rclpy.init(args=args)

    node = FrontDistanceSensor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
