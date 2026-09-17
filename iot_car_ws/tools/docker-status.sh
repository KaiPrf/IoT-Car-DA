#!/usr/bin/env bash

CONTAINER="iot-car-sim"

echo
echo "=============================================="
echo " IoT-Car Docker Status"
echo "=============================================="
echo


# Container
if ! docker inspect "$CONTAINER" >/dev/null 2>&1; then
    echo "Container: NICHT VORHANDEN"
    exit 1
fi

RUNNING=$(docker inspect -f '{{.State.Running}}' "$CONTAINER")

if [ "$RUNNING" != "true" ]; then
    echo "Container: GESTOPPT"
    exit 1
fi

echo "Container: LAEUFT"
echo


# Controller
echo "----------------------------------------------"
echo " Controller"
echo "----------------------------------------------"

docker exec "$CONTAINER" bash -lc '
    source /opt/ros/lyrical/setup.bash
    source /iot_car_ws/install/setup.bash
    ros2 control list_controllers
'

echo


# Kamera
echo "----------------------------------------------"
echo " Kamera"
echo "----------------------------------------------"

docker exec "$CONTAINER" bash -lc '
    source /opt/ros/lyrical/setup.bash
    source /iot_car_ws/install/setup.bash
    timeout 5s ros2 topic hz /car/camera/image
' 2>/dev/null | tail -n 4

echo


# Gazebo RTF
echo "----------------------------------------------"
echo " Gazebo Real Time Factor"
echo "----------------------------------------------"

docker exec "$CONTAINER" bash -lc '
    timeout 4s gz topic \
        --echo \
        --topic /world/iot_car_test_track/stats \
        -n 1
' 2>/dev/null | grep -E 'real_time_factor|paused'

echo


# GPU
echo "----------------------------------------------"
echo " GPU"
echo "----------------------------------------------"

docker exec "$CONTAINER" nvidia-smi \
    --query-gpu=name,utilization.gpu,memory.used,memory.total \
    --format=csv,noheader

echo


# Ressourcen
echo "----------------------------------------------"
echo " Container Ressourcen"
echo "----------------------------------------------"

docker stats \
    "$CONTAINER" \
    --no-stream \
    --format "CPU: {{.CPUPerc}} | RAM: {{.MemUsage}} | Netzwerk: {{.NetIO}}"

echo


# Webserver
echo "----------------------------------------------"
echo " Webserver"
echo "----------------------------------------------"

if curl -fsS http://localhost:8080/api/info >/dev/null 2>&1; then
    echo "Webserver: OK"
    echo "http://localhost:8080/info"
else
    echo "Webserver: NICHT ERREICHBAR"
fi

echo
echo "=============================================="
echo
