#!/usr/bin/env python3
"""Manual keyboard control. Run this node to drive by hand - stops when the
autonomous node isn't running, since only one control node moves the
platform at a time by whichever you choose to launch.
"""
import sys
import termios
import tty
import select

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

LINEAR_SPEED = 0.6
ANGULAR_SPEED = 0.5
KEY_TIMEOUT = 0.25

INSTRUCTIONS = """
Manual control - observation platform
  w/s   : forward / backward  (hold to keep moving)
  a/d   : turn left / right   (hold to keep turning)
  space : stop
  q     : quit
  Auto-stops after {timeout}s with no key press.
"""


def get_key(settings, timeout):
    tty.setraw(sys.stdin.fileno())
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    key = sys.stdin.read(1) if ready else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class ManualControlNode(Node):
    def __init__(self):
        super().__init__('manual_control_node')
        self.cmd_pub = self.create_publisher(
            Twist, '/model/observation_platform/cmd_vel', 10)

    def send_cmd(self, linear, angular):
        cmd = Twist()
        cmd.linear.x = linear
        cmd.angular.z = angular
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ManualControlNode()
    settings = termios.tcgetattr(sys.stdin)

    try:
        while rclpy.ok():
            print(INSTRUCTIONS.format(timeout=KEY_TIMEOUT))
            key = get_key(settings, KEY_TIMEOUT)

            if key == '':
                node.send_cmd(0.0, 0.0)
                continue
            if key == 'w':
                node.send_cmd(LINEAR_SPEED, 0.0)
            elif key == 's':
                node.send_cmd(-LINEAR_SPEED, 0.0)
            elif key == 'a':
                node.send_cmd(0.0, ANGULAR_SPEED)
            elif key == 'd':
                node.send_cmd(0.0, -ANGULAR_SPEED)
            elif key == ' ':
                node.send_cmd(0.0, 0.0)
            elif key == 'q':
                break
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
