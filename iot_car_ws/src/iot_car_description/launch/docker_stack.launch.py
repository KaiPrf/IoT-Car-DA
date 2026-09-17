from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Headless-Simulation
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("iot_car_description"),
                    "launch",
                    "vehicle_v2_docker.launch.py",
                ]
            )
        )
    )

    # Fahrzeuglogik und Weboberfläche
    game_control = Node(
        package="iot_car_description",
        executable="game_control.py",
        output="screen",
    )

    speed_sensor = Node(
        package="iot_car_description",
        executable="speed_sensor.py",
        output="screen",
    )

    distance_sensor = Node(
        package="iot_car_description",
        executable="front_distance_sensor.py",
        output="screen",
    )

    web_server = Node(
        package="iot_car_description",
        executable="web_server.py",
        output="screen",
    )

    return LaunchDescription(
        [
            simulation,
            game_control,
            speed_sensor,
            distance_sensor,
            web_server,
        ]
    )
