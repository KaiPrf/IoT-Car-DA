#!/usr/bin/env bash

set -e

source /opt/ros/lyrical/setup.bash
source /iot_car_ws/install/setup.bash

export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"

exec "$@"
