#!/usr/bin/env python3
"""Autonomous control with proper obstacle-avoidance state machine.
"""
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist

# ---- Tunable parameters ----
FORWARD_SPEED       = 0.6
TURN_SPEED          = 0.7

# Distances (m) — LiDAR range is 25 m, so use it!
DETECT_RANGE        = 10.0   # start slowing down
SLOW_RANGE          = 6.0    # begin choosing turn direction
CRITICAL_RANGE      = 3.0    # stop forward, turn in place
CLEAR_RANGE         = 8.0    # resume CRUISE only when truly clear ahead

# Geographic safety bounds (from your world)
LAND_X_LIMIT        = 30.0
PACK_ICE_Y_LIMIT    = 22.0

# Hysteresis for turn direction
TURN_COMMIT_TIME    = 1.5    # seconds to keep turning the same way


def valid_ranges(ranges):
    return [r for r in ranges if not math.isinf(r) and not math.isnan(r) and r > 0.05]


class AutonomousNode(Node):
    def __init__(self):
        super().__init__('autonomous_node')

        # --- State ---
        self.state = 'CRUISE'
        self.turn_dir = 0          # -1 left, +1 right, 0 undecided
        self.commit_timer = 0.0    # seconds remaining in current turn commitment
        self.recover_timer = 0.0

        # --- Sensor data ---
        self.latest_scan = None
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.yaw = 0.0

        # --- ROS interface ---
        self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.create_subscription(
            Odometry, '/model/observation_platform/odometry', self.on_odom, 10)
        self.cmd_pub = self.create_publisher(
            Twist, '/model/observation_platform/cmd_vel', 10)

        self.create_timer(0.1, self.control_loop)
        self.get_logger().info('Autonomous control active (FSM).')

    # ---------------- callbacks ----------------
    def on_scan(self, msg):
        self.latest_scan = msg

    def on_odom(self, msg):
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        siny = 2.0 * (q.w * q.z + q.x * q.y)
        cosy = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.yaw = math.atan2(siny, cosy)

    # ---------------- helpers ----------------
    def sector_analysis(self, scan):
        """Split 180-sample scan into 5 sectors and return (mins, min_overall)."""
        if scan is None or not scan.ranges:
            return None, float('inf')
        n = len(scan.ranges)
        s = n // 5
        sectors = {
            'far_left':  scan.ranges[0:s],
            'left':      scan.ranges[s:2*s],
            'center':    scan.ranges[2*s:3*s],
            'right':     scan.ranges[3*s:4*s],
            'far_right': scan.ranges[4*s:],
        }
        mins = {}
        for k, v in sectors.items():
            vv = valid_ranges(v)
            mins[k] = min(vv) if vv else float('inf')
        all_v = valid_ranges(scan.ranges)
        overall = min(all_v) if all_v else float('inf')
        return mins, overall

    def pick_turn_direction(self, mins):
        """Choose which side has more clearance."""
        left_clearance  = min(mins['far_left'],  mins['left'])
        right_clearance = min(mins['far_right'], mins['right'])
        return 1 if left_clearance >= right_clearance else -1

    # ---------------- main loop ----------------
    def control_loop(self):
        cmd = Twist()
        dt = 0.1

        # ---- Geographic safety: coastline / pack-ice ----
        if self.pos_x > LAND_X_LIMIT or self.pos_y > PACK_ICE_Y_LIMIT:
            self.get_logger().info(
                f'Geographic boundary reached (x={self.pos_x:.1f}, y={self.pos_y:.1f}) — turning back')
            cmd.linear.x = 0.0
            cmd.angular.z = TURN_SPEED
            self.cmd_pub.publish(cmd)
            self.state = 'CRUISE'
            return

        # ---- LiDAR-based avoidance ----
        mins, overall = self.sector_analysis(self.latest_scan)

        if mins is None:
            # No scan yet — slow idle
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.cmd_pub.publish(cmd)
            return

        front_min = mins['center']

        # --- State transitions with hysteresis ---
        if self.state == 'CRUISE':
            if front_min < DETECT_RANGE:
                self.state = 'CAUTION'
                self.get_logger().info(
                    f'Obstacle detected at {front_min:.1f} m — entering CAUTION')

        elif self.state == 'CAUTION':
            if front_min < SLOW_RANGE:
                self.state = 'AVOID'
                self.turn_dir = self.pick_turn_direction(mins)
                self.commit_timer = TURN_COMMIT_TIME
                self.get_logger().info(
                    f'Obstacle at {front_min:.1f} m — AVOID (turn '
                    f'{"left" if self.turn_dir>0 else "right"})')
            elif front_min > CLEAR_RANGE:
                self.state = 'CRUISE'

        elif self.state == 'AVOID':
            self.commit_timer -= dt
            if front_min > CLEAR_RANGE and self.commit_timer <= 0:
                self.state = 'RECOVER'
                self.recover_timer = 1.0
                self.get_logger().info('Path clearing — RECOVER')

        elif self.state == 'RECOVER':
            self.recover_timer -= dt
            if self.recover_timer <= 0:
                self.state = 'CRUISE'
                self.turn_dir = 0

        # --- Output commands per state ---
        if self.state == 'CRUISE':
            cmd.linear.x = FORWARD_SPEED
            cmd.angular.z = 0.0

        elif self.state == 'CAUTION':
            # Proportional slow-down between DETECT_RANGE and SLOW_RANGE
            ratio = (front_min - SLOW_RANGE) / (DETECT_RANGE - SLOW_RANGE)
            ratio = max(0.25, min(1.0, ratio))
            cmd.linear.x = FORWARD_SPEED * ratio
            # Gentle steer toward open side if one side is clearly closer
            if mins['left'] < mins['right'] * 0.7:
                cmd.angular.z = -0.25
            elif mins['right'] < mins['left'] * 0.7:
                cmd.angular.z = 0.25
            else:
                cmd.angular.z = 0.0

        elif self.state == 'AVOID':
            # Stop forward motion, turn hard
            cmd.linear.x = 0.05
            cmd.angular.z = self.turn_dir * TURN_SPEED

        elif self.state == 'RECOVER':
            # Move forward slowly to commit to avoidance path
            cmd.linear.x = FORWARD_SPEED * 0.5
            cmd.angular.z = self.turn_dir * 0.2

        self.cmd_pub.publish(cmd)

        # Log every ~3 seconds
        if int(self.get_clock().now().nanoseconds * 1e-9) % 3 == 0:
            self.get_logger().info(
                f'state={self.state} front={front_min:.1f} '
                f'overall={overall:.1f} pos=({self.pos_x:.1f},{self.pos_y:.1f})')


def main(args=None):
    rclpy.init(args=args)
    node = AutonomousNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
