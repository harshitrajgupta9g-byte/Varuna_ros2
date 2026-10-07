from setuptools import setup

package_name = 'auv_perception'

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
    description='Mock sensors for the demo',
    license='MIT',
    entry_points={
        'console_scripts': [
            'mock_sensor_publisher = auv_perception.mock_sensor_publisher:main',
            'data_receiver_node = auv_perception.data_receiver_node:main',
        ],
    },
)
