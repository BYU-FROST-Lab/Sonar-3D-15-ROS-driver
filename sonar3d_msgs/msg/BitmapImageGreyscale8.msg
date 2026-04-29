# Maps to waterlinked.sonar.protocol.BitmapImageGreyscale8
# BitmapImageType constants
uint8 SIGNAL_STRENGTH_IMAGE=0
uint8 SHADED_IMAGE=1

sonar3d_msgs/SonarHeader header
float32 speed_of_sound
float32 range
uint32 frequency
uint8 type
uint32 width
uint32 height
float32 fov_horizontal
float32 fov_vertical
# Row-major, width*height bytes, 8-bit greyscale (0-255)
uint8[] image_pixel_data
