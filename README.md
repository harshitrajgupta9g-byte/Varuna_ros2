🌊 Varuna_ros2 — Autonomous Ocean Observation Platform

  ROS 2  Gazebo  SIH 2026
📌 Problem Statement

Autonomous Low-Cost Ocean Observation Platform for Polar and Southern Oceans. Design and develop an indigenous, low-cost, autonomous ocean observation platform capable of long-term deployment in harsh polar environments for measuring key oceanographic and atmospheric parameters.
🚀 Project Overview

Varuna_ros2 is a ROS 2-based digital twin and simulation environment for an autonomous underwater/surface vehicle (AUV/ROV). The project simulates a 4-thruster space-capsule-shaped observation platform deployed in the polar oceans. It features real-time mock sensor telemetry, autonomous obstacle avoidance (icebergs/rocks), and a mock Iridium satellite communication pipeline.
✨ Key Features

    Space Capsule Frame: 4-thruster symmetric CAD model simulated in Gazebo Garden.
    Autonomous Obstacle Avoidance: LiDAR/Sonar-based algorithm that detects icebergs and rocks, stopping and turning 90 degrees to avoid collisions.
    Manual Control Override: Standard teleop_twist_keyboard integration for manual pilot control.
    Mock Telemetry Pipeline: Simulates CTD (Conductivity, Temp, Depth), Dissolved Oxygen, pH, Turbidity, and Atmospheric sensors (Wind, Solar, Pressure).
    Iridium SBD Comms: Simulates low-bandwidth satellite data transmission by packing data into 340-byte UDP packets.
    AI/ML Pipeline: TFLite models for sensor anomaly detection (LSTM Autoencoder) and ice/perception detection (YOLOv8).

🛠 Tech Stack

    Middleware: ROS 2 Humble
    Simulation: Gazebo Garden
    Programming: Python 3
    AI/ML: TensorFlow, TFLite, OpenCV
    Message Types: sensor_msgs, geometry_msgs, vision_msgs, diagnostic_msgs

📦 System Architecture

    Simulation Node: Gazebo renders the polar ocean environment, obstacles, and the Varuna robot.
    Sensor Nodes: Publish mock polar ocean data (e.g., Water Temp: -1.8°C, Salinity: 34.2 PSU) to ROS topics.
    Perception Node: Processes Sonar/LiDAR data to detect obstacles in a 60-degree front cone.
    Navigation Node: Subscribes to perception data and publishes cmd_vel (Twist) for autonomous movement.
    Comms Node: Aggregates all sensor data and transmits a mock Iridium SBD payload over UDP port 5005.

⚙️ Installation & Setup
1. Prerequisites

    Ubuntu 22.04 LTS
    ROS 2 Humble
    Gazebo Garden

2. Clone the Repository

git clone https://github.com/harshitrajgupta9g-byte/Varuna_ros2.gitcd Varuna_ros2

3. Build the Workspace
colcon build --symlink-install
source install/setup.bash

(The Varuna capsule will spawn in the polar ocean and begin autonomously dodging icebergs and rocks).

2. Manual Control (Override)

Open a second terminal to manually drive the capsule:
source ~/Varuna_ros2/install/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard

3. View Mock Sensor Data
source ~/Varuna_ros2/install/setup.bash
ros2 run ocean_mock dashboard

| Topic | Message Type | Description |
|-------|--------------|-------------|
| `/cmd_vel` | `geometry_msgs/Twist` | Velocity commands for the capsule |
| `/sonar/scan` | `sensor_msgs/LaserScan` | Obstacle detection data |
| `/ocean/water_temp` | `sensor_msgs/Temperature` | Mock polar water temperature |
| `/ocean/salinity` | `std_msgs/Float64` | Mock salinity (PSU) |
| `/atmos/wind` | `geometry_msgs/TwistStamped` | Mock wind speed/direction |
| `/gnss/fix` | `sensor_msgs/NavSatFix` | Mock GPS coordinates |

👥 Team

Team Name: VVARUNAA
SIH 2026
