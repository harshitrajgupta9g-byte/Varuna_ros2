from setuptools import setup

package_name = 'auv_navigation'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='team',
    maintainer_email='team@example.com',
    description='Obstacle avoidance, land detection, and manual control',
    license='MIT',
    entry_points={
        'console_scripts': [
            'autonomous_node = auv_navigation.autonomous_node:main',
            'manual_control_node = auv_navigation.manual_control_node:main',
        ],
    },
)
