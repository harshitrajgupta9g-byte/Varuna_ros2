#!/usr/bin/env python3
"""Mock sensor publisher to simulate live oceanographic data."""
import random
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class MockSensorPublisher(Node):
    def __init__(self):
        super().__init__('mock_sensor_publisher')
        self.publisher_ = self.create_publisher(Float64MultiArray, '/ocean/sensors', 10)
        timer_period = 1.0  # Publish data every 1 second
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info("Mock Sensor Publisher started. Transmitting ocean data...")

    def timer_callback(self):
        msg = Float64MultiArray()
        
        # Simulated sensor readings:
        # [water_temp_c, salinity_ppt, ph, dissolved_oxygen_mg_L, depth_m, battery_pct]
        water_temp = random.uniform(-1.5, 2.0)
        salinity = random.uniform(33.0, 35.0)
        ph = random.uniform(7.8, 8.2)
        do = random.uniform(7.0, 9.0)
        depth = random.uniform(0.1, 0.5)
        battery = random.uniform(85.0, 100.0)
        
        msg.data = [water_temp, salinity, ph, do, depth, battery]
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = MockSensorPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
