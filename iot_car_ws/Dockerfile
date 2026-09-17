FROM ros:lyrical-ros-base-resolute

ENV DEBIAN_FRONTEND=noninteractive

# ROS-, Gazebo- und Web-Abhängigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    python3-aiohttp \
    python3-opencv \
    python3-qrcode \
    python3-pil \
    ros-lyrical-ros-gz \
    ros-lyrical-gz-ros2-control \
    ros-lyrical-ros2-control \
    ros-lyrical-ros2-controllers \
    ros-lyrical-robot-state-publisher \
    ros-lyrical-xacro \
    ros-lyrical-cv-bridge \
    libgl1 \
    libegl1 \
    mesa-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /iot_car_ws

COPY src /iot_car_ws/src

RUN bash -lc \
    "source /opt/ros/lyrical/setup.bash && \
    colcon build --symlink-install"

COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]

CMD ["ros2", "launch", "iot_car_description", "docker_stack.launch.py"]
