from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    RegisterEventHandler,
    SetEnvironmentVariable,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    Command,
    FindExecutable,
    PathJoinSubstitution,
)

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_share = FindPackageShare(
        "iot_car_description"
    )

    xacro_file = PathJoinSubstitution([
        pkg_share,
        "urdf",
        "iot_car.urdf.xacro",
    ])

    world_file = PathJoinSubstitution([
        pkg_share,
        "worlds",
        "iot_car_world.sdf",
    ])

    controller_config = PathJoinSubstitution([
        pkg_share,
        "config",
        "iot_car_controllers.yaml",
    ])


    robot_description = ParameterValue(
        Command([
            FindExecutable(
                name="xacro"
            ),
            " ",
            xacro_file,
        ]),
        value_type=str,
    )


    gazebo_plugin_path = SetEnvironmentVariable(
        name="GZ_SIM_SYSTEM_PLUGIN_PATH",
        value="/opt/ros/lyrical/lib",
    )


    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare(
                    "ros_gz_sim"
                ),
                "launch",
                "gz_sim.launch.py",
            ])
        ),
        launch_arguments={
            "gz_args": [
                " -r --render-engine ogre ",
                world_file,
            ]
        }.items(),
    )


    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "robot_description":
                    robot_description,

                "use_sim_time":
                    True,
            }
        ],
    )


    spawn_car = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_iot_car",
        output="screen",
        arguments=[
            "-topic",
            "robot_description",
            "-name",
            "iot_car",
            "-z",
            "0.09",
        ],
    )


    gazebo_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="gazebo_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",

            "/car/ground_truth_pose"
            "@geometry_msgs/msg/PoseStamped"
            "[gz.msgs.Pose",

            "/car/camera/image"
            "@sensor_msgs/msg/Image"
            "[gz.msgs.Image",

            "/car/camera/camera_info"
            "@sensor_msgs/msg/CameraInfo"
            "[gz.msgs.CameraInfo",
        ],
    )


    distance_sensor = Node(
        package="iot_car_description",
        executable="distance_sensor.py",
        name="distance_sensor",
        output="screen",
        parameters=[
            {
                "use_sim_time":
                    True,
            }
        ],
    )


    speed_sensor = Node(
        package="iot_car_description",
        executable="speed_sensor.py",
        name="speed_sensor",
        output="screen",
        parameters=[
            {
                "use_sim_time":
                    True,
            }
        ],
    )


    web_control = Node(
        package="iot_car_description",
        executable="web_control.py",
        name="web_control",
        output="screen",
        parameters=[
            {
                "use_sim_time":
                    True,
            }
        ],
    )


    joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_spawner",
        output="screen",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )


    ackermann_controller = Node(
        package="controller_manager",
        executable="spawner",
        name="ackermann_controller_spawner",
        output="screen",
        arguments=[
            "ackermann_steering_controller",
            "--controller-manager",
            "/controller_manager",
            "--param-file",
            controller_config,
        ],
    )


    start_joint_state_after_spawn = (
        RegisterEventHandler(
            OnProcessExit(
                target_action=spawn_car,
                on_exit=[
                    joint_state_broadcaster,
                ],
            )
        )
    )


    start_ackermann_after_joint_state = (
        RegisterEventHandler(
            OnProcessExit(
                target_action=
                    joint_state_broadcaster,

                on_exit=[
                    ackermann_controller,
                ],
            )
        )
    )


    return LaunchDescription([
        gazebo_plugin_path,
        gazebo,
        robot_state_publisher,
        gazebo_bridge,
        spawn_car,
        distance_sensor,
        speed_sensor,
        web_control,
        start_joint_state_after_spawn,
        start_ackermann_after_joint_state,
    ])
