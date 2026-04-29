cmake_minimum_required(VERSION 3.5)
project(sonar3d_msgs)

find_package(ament_cmake REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SonarHeader.msg"
  "msg/RangeImage.msg"
  "msg/BitmapImageGreyscale8.msg"
  DEPENDENCIES builtin_interfaces
)

ament_package()
