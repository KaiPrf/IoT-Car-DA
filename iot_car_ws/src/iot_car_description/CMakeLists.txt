cmake_minimum_required(VERSION 3.8)
project(iot_car_description)

find_package(ament_cmake REQUIRED)

install(
	DIRECTORY
	urdf
	launch
	worlds
	meshes
	config
	web
	DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/distance_sensor.py
    scripts/speed_sensor.py
    scripts/web_control.py
    scripts/keyboard_drive.py
    scripts/game_control.py
    scripts/keyboard_input.py
    scripts/front_distance_sensor.py
    scripts/web_server.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
