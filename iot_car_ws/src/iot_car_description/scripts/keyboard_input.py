#!/usr/bin/env python3

import pygame
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Joy


class KeyboardInput(Node):

    def __init__(self):
        super().__init__("keyboard_input")

        # Eingabegerät
        self.control_frequency = 50.0
        self.control_period = 1.0 / self.control_frequency

        self.running = True

        self.publisher = self.create_publisher(
            Joy,
            "/control/input",
            10,
        )

        self.timer = self.create_timer(
            self.control_period,
            self.update,
        )

        pygame.init()

        self.screen = pygame.display.set_mode(
            (520, 245)
        )

        pygame.display.set_caption(
            "IoT-Car PC-Steuerung"
        )

        self.font_large = pygame.font.SysFont(
            None,
            34,
        )

        self.font_small = pygame.font.SysFont(
            None,
            25,
        )

        self.get_logger().info(
            "Keyboard-Eingabe gestartet"
        )


    def publish_input(
        self,
        steering,
        throttle,
        brake,
        emergency_stop,
    ):
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


    def draw_interface(
        self,
        steering,
        throttle,
        brake,
    ):
        self.screen.fill(
            (28, 28, 32)
        )

        title = self.font_large.render(
            "IoT-Car PC-Steuerung",
            True,
            (235, 235, 235),
        )

        self.screen.blit(
            title,
            (20, 18),
        )

        lines = [
            "W = Gas",
            "S = Bremse / Rückwärts",
            "A / D = Lenken",
            "LEERTASTE = Sofort stoppen",
            "ESC = Beenden",
            "",
            f"Lenkung: {steering:+.0f}",
            f"Gas:     {throttle:.0f}",
            f"Bremse:  {brake:.0f}",
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

            y += 20

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

        steering = 0.0

        if keys[pygame.K_a]:
            steering += 1.0

        if keys[pygame.K_d]:
            steering -= 1.0

        throttle = (
            1.0 if keys[pygame.K_w] else 0.0
        )

        brake = (
            1.0 if keys[pygame.K_s] else 0.0
        )

        emergency_stop = bool(
            keys[pygame.K_SPACE]
        )

        self.publish_input(
            steering,
            throttle,
            brake,
            emergency_stop,
        )

        self.draw_interface(
            steering,
            throttle,
            brake,
        )


    def destroy_node(self):
        self.publish_input(
            0.0,
            0.0,
            0.0,
            True,
        )

        pygame.quit()

        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = KeyboardInput()

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
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
