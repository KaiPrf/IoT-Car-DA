#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Bool


class DistanceSensor(Node):

    def __init__(self):
        super().__init__('distance_sensor')

        # ---------------------------------------------------------
        # Testwand in der Gazebo-Welt
        # ---------------------------------------------------------

        self.wall_center_x = 2.0
        self.wall_center_y = 0.0

        self.wall_size_x = 0.10
        self.wall_size_y = 1.00

        # ---------------------------------------------------------
        # Position des Sensors relativ zur Fahrzeugmitte
        # ---------------------------------------------------------

        self.sensor_offset = 0.205

        # ---------------------------------------------------------
        # Sensorbereich
        # ---------------------------------------------------------

        self.min_range = 0.02
        self.max_range = 4.0

        # ungefähr +/- 0.20 rad
        self.half_fov = 0.20

        # 9 virtuelle Messstrahlen
        self.samples = 9

        # ---------------------------------------------------------
        # ROS Publisher
        # ---------------------------------------------------------

        self.distance_pub = self.create_publisher(
            Float32,
            '/car/distance',
            10
        )

        self.distance_valid_pub = self.create_publisher(
            Bool,
            '/car/distance_valid',
            10
        )

        # ---------------------------------------------------------
        # Echte Gazebo-Fahrzeugposition
        # ---------------------------------------------------------

        self.pose_sub = self.create_subscription(
            PoseStamped,
            '/car/ground_truth_pose',
            self.pose_callback,
            10
        )

        self.get_logger().info(
            'Distance sensor started using Gazebo ground-truth pose'
        )


    def pose_callback(self, msg):

        # ---------------------------------------------------------
        # Tatsächliche Fahrzeugposition aus Gazebo
        # ---------------------------------------------------------

        x = msg.pose.position.x
        y = msg.pose.position.y

        q = msg.pose.orientation

        # Quaternion -> Yaw
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        # ---------------------------------------------------------
        # Position des Sensors vorne am Auto
        # ---------------------------------------------------------

        sensor_x = (
            x
            + self.sensor_offset * math.cos(yaw)
        )

        sensor_y = (
            y
            + self.sensor_offset * math.sin(yaw)
        )

        # ---------------------------------------------------------
        # Grenzen der Wand
        # ---------------------------------------------------------

        xmin = (
            self.wall_center_x
            - self.wall_size_x / 2.0
        )

        xmax = (
            self.wall_center_x
            + self.wall_size_x / 2.0
        )

        ymin = (
            self.wall_center_y
            - self.wall_size_y / 2.0
        )

        ymax = (
            self.wall_center_y
            + self.wall_size_y / 2.0
        )

        # ---------------------------------------------------------
        # Messung
        # ---------------------------------------------------------

        best_distance = self.max_range

        for i in range(self.samples):

            if self.samples == 1:
                angle_offset = 0.0

            else:
                angle_offset = (
                    -self.half_fov
                    + (
                        2.0
                        * self.half_fov
                        * i
                        / (self.samples - 1)
                    )
                )

            angle = yaw + angle_offset

            direction_x = math.cos(angle)
            direction_y = math.sin(angle)

            distance = self.ray_box_intersection(
                sensor_x,
                sensor_y,
                direction_x,
                direction_y,
                xmin,
                xmax,
                ymin,
                ymax
            )

            if distance is not None:
                best_distance = min(
                    best_distance,
                    distance
                )

        # ---------------------------------------------------------
        # Kein Hindernis innerhalb 4 Meter
        # ---------------------------------------------------------

        if best_distance >= self.max_range:

            self.publish_distance(
                self.max_range,
                False
            )

            return

        # ---------------------------------------------------------
        # Hindernis unmittelbar vor dem Sensor
        #
        # Für die Benutzeranzeige geben wir hier 0.0 m aus.
        # ---------------------------------------------------------

        if best_distance <= self.min_range:

            self.publish_distance(
                0.0,
                True
            )

            return

        # ---------------------------------------------------------
        # Normaler gültiger Messwert
        # ---------------------------------------------------------

        self.publish_distance(
            best_distance,
            True
        )


    def publish_distance(self, distance, is_valid):

        distance_msg = Float32()
        valid_msg = Bool()

        distance_msg.data = float(distance)
        valid_msg.data = bool(is_valid)

        self.distance_pub.publish(
            distance_msg
        )

        self.distance_valid_pub.publish(
            valid_msg
        )


    def ray_box_intersection(
        self,
        origin_x,
        origin_y,
        direction_x,
        direction_y,
        xmin,
        xmax,
        ymin,
        ymax
    ):

        t_min = 0.0
        t_max = self.max_range

        # ---------------------------------------------------------
        # X-Schnitt
        # ---------------------------------------------------------

        if abs(direction_x) < 1e-9:

            if (
                origin_x < xmin
                or
                origin_x > xmax
            ):
                return None

        else:

            tx1 = (
                xmin - origin_x
            ) / direction_x

            tx2 = (
                xmax - origin_x
            ) / direction_x

            t_min = max(
                t_min,
                min(tx1, tx2)
            )

            t_max = min(
                t_max,
                max(tx1, tx2)
            )

            if t_max < t_min:
                return None

        # ---------------------------------------------------------
        # Y-Schnitt
        # ---------------------------------------------------------

        if abs(direction_y) < 1e-9:

            if (
                origin_y < ymin
                or
                origin_y > ymax
            ):
                return None

        else:

            ty1 = (
                ymin - origin_y
            ) / direction_y

            ty2 = (
                ymax - origin_y
            ) / direction_y

            t_min = max(
                t_min,
                min(ty1, ty2)
            )

            t_max = min(
                t_max,
                max(ty1, ty2)
            )

            if t_max < t_min:
                return None

        # ---------------------------------------------------------
        # Wand liegt hinter Sensor
        # ---------------------------------------------------------

        if t_max < 0.0:
            return None

        # Sensor befindet sich bereits unmittelbar an/in der Wand.
        if t_min <= 0.0 <= t_max:
            return 0.0

        if t_min < 0.0:
            return None

        if t_min > self.max_range:
            return None

        return t_min


def main(args=None):

    rclpy.init(args=args)

    node = DistanceSensor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
