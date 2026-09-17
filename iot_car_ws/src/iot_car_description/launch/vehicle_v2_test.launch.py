from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # Fahrzeugbeschreibung und Controller
    robot_description = {
        "robot_description": Command(
            [
                PathJoinSubstitution([FindExecutable(name="xacro")]),
                " ",
                PathJoinSubstitution(
                    [
                        FindPackageShare("iot_car_description"),
                        "urdf",
                        "vehicle_v2.urdf.xacro",
                    ]
                ),
            ]
        )
    }

    controller_config = PathJoinSubstitution(
        [
            FindPackageShare("iot_car_description"),
            "config",
            "vehicle_v2_controllers.yaml",
        ]
    )

    # ROS-Nodes
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            robot_description,
            {"use_sim_time": True},
        ],
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
            "0.0",
            "-y",
            "0.0",
            "-z",
            "0.06",
        ],
    )

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

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
        ],
    )

    # Startreihenfolge
    return LaunchDescription(
        [
            clock_bridge,

            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [
                        PathJoinSubstitution(
                            [
                                FindPackageShare("ros_gz_sim"),
                                "launch",
                                "gz_sim.launch.py",
                            ]
                        )
                    ]
                ),
                launch_arguments=[
                    (
                        "gz_args",
                        [" -r -v 1 empty.sdf"],
                    )
                ],
            ),

            robot_state_publisher,

            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=spawn_vehicle,
                    on_exit=[
                        joint_state_broadcaster,
                    ],
                )
            ),

            RegisterEventHandler(
                event_handler=OnProcessExit(
                    target_action=joint_state_broadcaster,
                    on_exit=[
                        ackermann_controller,
                    ],
                )
            ),

            spawn_vehicle,
        ]
    )
