#!/usr/bin/env python3

import math

import pygame
import rclpy

from geometry_msgs.msg import TwistStamped
from rclpy.node import Node


class KeyboardDrive(Node):

    def __init__(self):
        super().__init__("keyboard_drive")

        # Fahrzeugparameter
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

        self.current_speed = 0.0
        self.current_steering = 0.0

        self.running = True

        self.publisher = self.create_publisher(
            TwistStamped,
            "/cmd_vel",
            10,
        )

        self.timer = self.create_timer(
            self.control_period,
            self.update,
        )

        self.setup_pygame()

        self.get_logger().info(
            "Keyboard-Steuerung gestartet"
        )


    def setup_pygame(self):
        pygame.init()

        self.screen = pygame.display.set_mode(
            (520, 260)
        )

        pygame.display.set_caption(
            "IoT-Car Keyboard Control"
        )

        self.font_large = pygame.font.SysFont(
            None,
            34,
        )

        self.font_small = pygame.font.SysFont(
            None,
            25,
        )


    def move_towards(self, current, target, rate):
        difference = target - current
        maximum_change = rate * self.control_period

        if abs(difference) <= maximum_change:
            return target

        return current + math.copysign(
            maximum_change,
            difference,
        )


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


    def process_speed(self, gas_pressed, brake_pressed):
        if gas_pressed and not brake_pressed:

            if self.current_speed < 0.0:
                self.current_speed = self.move_towards(
                    self.current_speed,
                    0.0,
                    self.brake_deceleration,
                )

            else:
                self.current_speed = self.move_towards(
                    self.current_speed,
                    self.max_forward_speed,
                    self.acceleration,
                )

        elif brake_pressed and not gas_pressed:

            if self.current_speed > 0.05:
                self.current_speed = self.move_towards(
                    self.current_speed,
                    0.0,
                    self.brake_deceleration,
                )

            else:
                self.current_speed = self.move_towards(
                    self.current_speed,
                    -self.max_reverse_speed,
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


    def process_steering(self, left_pressed, right_pressed):
        if left_pressed and not right_pressed:
            target_steering = 1.0

        elif right_pressed and not left_pressed:
            target_steering = -1.0

        else:
            target_steering = 0.0

        if target_steering == 0.0:
            rate = self.steering_return_rate
        else:
            rate = self.steering_rate

        self.current_steering = self.move_towards(
            self.current_steering,
            target_steering,
            rate,
        )


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

        self.publisher.publish(message)


    def stop_vehicle(self):
        self.current_speed = 0.0
        self.current_steering = 0.0

        for _ in range(5):
            self.publish_command()


    def draw_interface(self):
        self.screen.fill(
            (28, 28, 32)
        )

        title = self.font_large.render(
            "IoT-Car Steuerung",
            True,
            (235, 235, 235),
        )

        self.screen.blit(
            title,
            (20, 18),
        )

        speed_kmh = (
            self.current_speed * 3.6
        )

        max_steering_deg = math.degrees(
            self.get_max_steering_angle()
        )

        steering_deg = (
            self.current_steering
            * max_steering_deg
        )

        lines = [
            "W = Gas",
            "S = Bremse / Rückwärts",
            "A / D = Lenken",
            "LEERTASTE = Sofort stoppen",
            "ESC = Beenden",
            "",
            f"Geschwindigkeit: {speed_kmh:5.2f} km/h",
            f"Lenkung:          {steering_deg:5.1f}°",
        ]

        y = 65

        for line in lines:
            text = self.font_small.render(
                line,
                True,
                (220, 220, 220),
            )

            self.screen.blit(
                text,
                (25, y),
            )

            y += 23

        pygame.display.flip()


    def update(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False
                rclpy.shutdown()
                return

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
            ):
                self.running = False
                rclpy.shutdown()
                return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            self.stop_vehicle()
            self.draw_interface()
            return

        gas_pressed = keys[pygame.K_w]
        brake_pressed = keys[pygame.K_s]

        left_pressed = keys[pygame.K_a]
        right_pressed = keys[pygame.K_d]

        self.process_speed(
            gas_pressed,
            brake_pressed,
        )

        self.process_steering(
            left_pressed,
            right_pressed,
        )

        self.publish_command()
        self.draw_interface()


    def destroy_node(self):
        self.stop_vehicle()
        pygame.quit()

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = KeyboardDrive()

    try:
        while (
            rclpy.ok()
            and node.running
        ):
            rclpy.spin_once(
                node,
                timeout_sec=0.02,
            )

    except KeyboardInterrupt:
        pass

    finally:
        if rclpy.ok():
            node.stop_vehicle()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
