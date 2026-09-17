#!/usr/bin/env python3

import math

import rclpy

from geometry_msgs.msg import TwistStamped
from rclpy.node import Node
from sensor_msgs.msg import Joy


class GameControl(Node):

    def __init__(self):
        super().__init__("game_control")

        # Fahrzeug- und Fahrparameter
        self.wheelbase = 0.26

        self.max_forward_speed = 2.78
        self.max_reverse_speed = 1.39

        self.acceleration = 2.2
        self.reverse_acceleration = 1.8
        self.brake_deceleration = 4.5
        self.coast_deceleration = 1.2

        self.max_steering_low_speed = 0.50
        self.max_steering_high_speed = 0.18

        self.steering_rate = 4.5
        self.steering_return_rate = 6.0

        self.control_frequency = 50.0
        self.control_period = 1.0 / self.control_frequency

        self.input_timeout = 0.40

        self.current_speed = 0.0
        self.current_steering = 0.0

        self.target_steering = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.emergency_stop = False

        self.last_input_time = self.get_clock().now()

        self.cmd_publisher = self.create_publisher(
            TwistStamped,
            "/cmd_vel",
            10,
        )

        self.input_subscription = self.create_subscription(
            Joy,
            "/control/input",
            self.input_callback,
            10,
        )

        self.timer = self.create_timer(
            self.control_period,
            self.update,
        )

        self.get_logger().info(
            "Zentrale Fahrzeugsteuerung gestartet"
        )


    def input_callback(self, message):
        if len(message.axes) >= 3:
            self.target_steering = max(
                -1.0,
                min(1.0, float(message.axes[0])),
            )

            self.throttle = max(
                0.0,
                min(1.0, float(message.axes[1])),
            )

            self.brake = max(
                0.0,
                min(1.0, float(message.axes[2])),
            )

        if len(message.buttons) >= 1:
            self.emergency_stop = bool(
                message.buttons[0]
            )
        else:
            self.emergency_stop = False

        self.last_input_time = self.get_clock().now()


    def move_towards(self, current, target, rate):
        difference = target - current
        maximum_change = rate * self.control_period

        if abs(difference) <= maximum_change:
            return target

        return current + math.copysign(
            maximum_change,
            difference,
        )


    def input_is_active(self):
        elapsed = (
            self.get_clock().now()
            - self.last_input_time
        ).nanoseconds / 1_000_000_000.0

        return elapsed <= self.input_timeout


    def get_max_steering_angle(self):
        speed_ratio = min(
            abs(self.current_speed)
            / self.max_forward_speed,
            1.0,
        )

        steering_range = (
            self.max_steering_low_speed
            - self.max_steering_high_speed
        )

        return (
            self.max_steering_high_speed
            + steering_range
            * (1.0 - speed_ratio ** 0.7)
        )


    def process_speed(self):
        if self.throttle > 0.0 and self.brake <= 0.0:

            if self.current_speed < 0.0:
                self.current_speed = self.move_towards(
                    self.current_speed,
                    0.0,
                    self.brake_deceleration,
                )

            else:
                target_speed = (
                    self.max_forward_speed
                    * self.throttle
                )

                self.current_speed = self.move_towards(
                    self.current_speed,
                    target_speed,
                    self.acceleration,
                )

        elif self.brake > 0.0 and self.throttle <= 0.0:

            if self.current_speed > 0.05:
                self.current_speed = self.move_towards(
                    self.current_speed,
                    0.0,
                    self.brake_deceleration
                    * self.brake,
                )

            else:
                target_speed = (
                    -self.max_reverse_speed
                    * self.brake
                )

                self.current_speed = self.move_towards(
                    self.current_speed,
                    target_speed,
                    self.reverse_acceleration,
                )

        else:
            self.current_speed = self.move_towards(
                self.current_speed,
                0.0,
                self.coast_deceleration,
            )

        if abs(self.current_speed) < 0.005:
            self.current_speed = 0.0


    def process_steering(self):
        if abs(self.target_steering) < 0.01:
            steering_target = 0.0
            steering_rate = self.steering_return_rate

        else:
            steering_target = self.target_steering
            steering_rate = self.steering_rate

        self.current_steering = self.move_towards(
            self.current_steering,
            steering_target,
            steering_rate,
        )


    def reset_input(self):
        self.target_steering = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.emergency_stop = False


    def stop_immediately(self):
        self.current_speed = 0.0
        self.current_steering = 0.0


    def publish_command(self):
        max_steering_angle = (
            self.get_max_steering_angle()
        )

        steering_angle = (
            self.current_steering
            * max_steering_angle
        )

        if abs(self.current_speed) > 0.001:
            yaw_rate = (
                self.current_speed
                * math.tan(steering_angle)
                / self.wheelbase
            )
        else:
            yaw_rate = 0.0

        message = TwistStamped()

        message.header.stamp = (
            self.get_clock().now().to_msg()
        )

        message.header.frame_id = "base_link"

        message.twist.linear.x = float(
            self.current_speed
        )

        message.twist.angular.z = float(
            yaw_rate
        )

        self.cmd_publisher.publish(message)


    def update(self):
        if not self.input_is_active():
            self.reset_input()

        if self.emergency_stop:
            self.stop_immediately()
            self.publish_command()
            return

        self.process_speed()
        self.process_steering()

        self.publish_command()


def main(args=None):
    rclpy.init(args=args)

    node = GameControl()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.stop_immediately()
        node.publish_command()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
