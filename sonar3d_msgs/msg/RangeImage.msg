# Maps to waterlinked.sonar.protocol.RangeImage
sonar3d_msgs/SonarHeader header
float32 speed_of_sound
float32 range
uint32 frequency
uint32 width
uint32 height
float32 fov_horizontal
float32 fov_vertical
float32 image_pixel_scale
# Each pixel * image_pixel_scale gives distance in meters; 0 means no return
uint32[] image_pixel_data
