#!/usr/bin/env bash

set -e

source /opt/ros/lyrical/setup.bash
source "$HOME/iot_car_ws/install/setup.bash"

echo
echo "=============================================="
echo " IoT-Car Simulation"
echo "=============================================="
echo
echo "Netzwerk: ${IOT_CAR_NETWORK_NAME:-unbekannt}"
echo "Host-IP:  ${IOT_CAR_HOST_IP:-nicht gesetzt}"
echo "Web-Port: 8080"
echo


# Simulation
ros2 launch iot_car_description vehicle_v2_track.launch.py &
SIM_PID=$!

sleep 3


# Fahrzeugsteuerung
ros2 run iot_car_description game_control.py &
CONTROL_PID=$!


# Sensoren
ros2 run iot_car_description speed_sensor.py &
SPEED_PID=$!

ros2 run iot_car_description front_distance_sensor.py &
DISTANCE_PID=$!


sleep 1


# Webserver
ros2 run iot_car_description web_server.py &
WEB_PID=$!


cleanup() {
    echo
    echo "Beende IoT-Car Simulation ..."

    kill "$WEB_PID" 2>/dev/null || true
    kill "$DISTANCE_PID" 2>/dev/null || true
    kill "$SPEED_PID" 2>/dev/null || true
    kill "$CONTROL_PID" 2>/dev/null || true
    kill "$SIM_PID" 2>/dev/null || true

    wait 2>/dev/null || true
}

trap cleanup EXIT INT TERM


echo
echo "Simulation gestartet."
echo
echo "PC:"
echo "  http://localhost:8080"
echo
echo "Handy:"
echo "  http://${IOT_CAR_HOST_IP}:8080"
echo
echo "Mit Ctrl+C beenden."
echo

wait
