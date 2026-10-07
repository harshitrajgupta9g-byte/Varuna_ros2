#!/usr/bin/env python3
"""Data receiver node - displays a live dashboard and logs to CSV."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
from nav_msgs.msg import Odometry
import sys
import math
import csv
import os

class DataReceiverNode(Node):
    def __init__(self):
        super().__init__('data_receiver_node')
        
        # Data state
        self.sensor_data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # temp, sal, ph, do, depth, batt
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.yaw = 0.0
        self.speed = 0.0

        # Subscriptions
        self.create_subscription(Float64MultiArray, '/ocean/sensors', self.sensor_callback, 10)
        self.create_subscription(Odometry, '/model/observation_platform/odometry', self.odom_callback, 10)
        
        # CSV setup
        self.csv_file = os.path.expanduser('~/ocean_platform_data.csv')
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'x', 'y', 'heading', 'speed', 'temp', 'salinity', 'ph', 'do', 'depth', 'battery'])

        # Dashboard update timer (2 Hz)
        self.timer = self.create_timer(0.5, self.update_dashboard)
        self.get_logger().info("Data Receiver Dashboard started.")

    def sensor_callback(self, msg):
        self.sensor_data = msg.data

    def odom_callback(self, msg):
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y
        self.speed = msg.twist.twist.linear.x
        
        # Calculate heading (yaw) from odometry quaternion
        q = msg.pose.pose.orientation
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        self.yaw = math.degrees(math.atan2(siny_cosp, cosy_cosp))
        
        # Log to CSV quietly in background
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                f"{self.pos_x:.2f}", f"{self.pos_y:.2f}", f"{self.yaw:.1f}", f"{self.speed:.2f}",
                f"{self.sensor_data[0]:.2f}", f"{self.sensor_data[1]:.2f}", f"{self.sensor_data[2]:.2f}",
                f"{self.sensor_data[3]:.2f}", f"{self.sensor_data[4]:.2f}", f"{self.sensor_data[5]:.1f}"
            ])

    def update_dashboard(self):
        # Clear terminal screen using ANSI escape codes
        sys.stdout.write('\033[2J\033[H')
        
        print("=" * 45)
        print("    OCEAN OBSERVATION PLATFORM - LIVE TELEMETRY")
        print("=" * 45)
        
        print("\n[ NAVIGATION ]")
        print(f"  X-Pos   : {self.pos_x:8.2f} m")
        print(f"  Y-Pos   : {self.pos_y:8.2f} m")
        print(f"  Heading : {self.yaw:8.1f} °")
        print(f"  Speed   : {self.speed:8.2f} m/s")

        print("\n[ OCEAN SENSORS ]")
        if len(self.sensor_data) >= 6:
            print(f"  Water Temp    : {self.sensor_data[0]:8.2f} °C")
            print(f"  Salinity      : {self.sensor_data[1]:8.2f} ppt")
            print(f"  pH Level      : {self.sensor_data[2]:8.2f}")
            print(f"  Dissolved O2  : {self.sensor_data[3]:8.2f} mg/L")
            print(f"  Depth         : {self.sensor_data[4]:8.2f} m")

        print("\n[ SYSTEM STATUS ]")
        if len(self.sensor_data) >= 6:
            print(f"  Battery       : {self.sensor_data[5]:8.1f} %")

        print("\n" + "=" * 45)
        print(f" Background logging to: {self.csv_file}")
        print("=" * 45)
        
        # Force output to terminal immediately
        sys.stdout.flush()

def main(args=None):
    rclpy.init(args=args)
    node = DataReceiverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        # Clear screen on exit
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()
        print("Data Receiver stopped.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
