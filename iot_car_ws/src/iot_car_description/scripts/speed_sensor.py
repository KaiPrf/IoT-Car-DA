#!/usr/bin/env python3

import rclpy

from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64


class SpeedSensor(Node):

    def __init__(self):
        super().__init__("speed_sensor")

        # Fahrzeugparameter
        self.wheel_radius = 0.055
        self.deadzone = 0.005

        self.speed_publisher = self.create_publisher(
            Float64,
            "/car/speed",
            10,
        )

        self.speed_kmh_publisher = self.create_publisher(
            Float64,
            "/car/speed_kmh",
            10,
        )

        self.subscription = self.create_subscription(
            JointState,
            "/joint_states",
            self.joint_state_callback,
            10,
        )

        self.get_logger().info(
            "Geschwindigkeitssensor gestartet"
        )


    def joint_state_callback(self, message):
        velocities = {}

        for index, name in enumerate(message.name):
            if index < len(message.velocity):
                velocities[name] = message.velocity[index]

        left_velocity = velocities.get(
            "rear_left_wheel_joint"
        )

        right_velocity = velocities.get(
            "rear_right_wheel_joint"
        )

        if (
            left_velocity is None
            or right_velocity is None
        ):
            return

        average_velocity = (
            left_velocity
            + right_velocity
        ) / 2.0

        speed = (
            average_velocity
            * self.wheel_radius
        )

        if abs(speed) < self.deadzone:
            speed = 0.0

        speed_kmh = speed * 3.6

        speed_message = Float64()
        speed_message.data = round(
            speed,
            3,
        )

        speed_kmh_message = Float64()
        speed_kmh_message.data = round(
            speed_kmh,
            2,
        )

        self.speed_publisher.publish(
            speed_message
        )

        self.speed_kmh_publisher.publish(
            speed_kmh_message
        )


def main(args=None):
    rclpy.init(args=args)

    node = SpeedSensor()

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
