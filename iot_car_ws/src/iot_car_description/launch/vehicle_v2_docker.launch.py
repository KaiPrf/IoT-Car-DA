from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Fahrzeug, Strecke und Controller
    package_share = FindPackageShare("iot_car_description")

    robot_file = PathJoinSubstitution(
        [
            package_share,
            "urdf",
            "vehicle_v2.urdf.xacro",
        ]
    )

    world_file = PathJoinSubstitution(
        [
            package_share,
            "worlds",
            "test_track_v2.sdf",
        ]
    )

    controller_config = PathJoinSubstitution(
        [
            package_share,
            "config",
            "vehicle_v2_controllers.yaml",
        ]
    )

    robot_description = {
        "robot_description": Command(
            [
                FindExecutable(name="xacro"),
                " ",
                robot_file,
            ]
        )
    }

    # ROS und Gazebo
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            robot_description,
            {"use_sim_time": True},
        ],
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("ros_gz_sim"),
                    "launch",
                    "gz_sim.launch.py",
                ]
            )
        ),
        launch_arguments={
            "gz_args": [
                " -s -r --headless-rendering -v 1 ",
                world_file,
            ]
        }.items(),
    )

    spawn_vehicle = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-topic",
            "robot_description",
            "-name",
            "iot_car_v2",
            "-x",
            "-4.2",
            "-y",
            "-1.3",
            "-z",
            "0.06",
            "-Y",
            "0.0",
        ],
    )

    gazebo_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/car/camera/image@sensor_msgs/msg/Image[gz.msgs.Image",
            "/car/camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
            "/car/front_scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
        ],
    )

    # Controller
    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "joint_state_broadcaster",
        ],
    )

    ackermann_controller = Node(
        package="controller_manager",
        executable="spawner",
        output="screen",
        arguments=[
            "ackermann_steering_controller",
            "--param-file",
            controller_config,
            "--controller-ros-args",
            "-r /ackermann_steering_controller/tf_odometry:=/tf",
            "--controller-ros-args",
            "-r /ackermann_steering_controller/reference:=/cmd_vel",
        ],
    )

    start_joint_states = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_vehicle,
            on_exit=[
                joint_state_broadcaster,
            ],
        )
    )

    start_ackermann = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster,
            on_exit=[
                ackermann_controller,
            ],
        )
    )

    return LaunchDescription(
        [
            gazebo_bridge,
            gazebo,
            robot_state_publisher,
            start_joint_states,
            start_ackermann,
            spawn_vehicle,
        ]
    )
