import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2, Image
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

import numpy as np
import wlsonar
import wlsonar.range_image_protocol as rip


class TimerNode(Node):

    def __init__(self):
        super().__init__('timer_node')

        self.declare_parameter('IP', wlsonar.FALLBACK_IP)
        self.declare_parameter('speed_of_sound', 1491)  # setting this takes ~20s

        self.sonar_ip = self.get_parameter('IP').get_parameter_value().string_value
        self.sonar_speed_of_sound = self.get_parameter('speed_of_sound').get_parameter_value().integer_value

        sample_time = 0.01
        self.create_timer(sample_time, self.timer_callback)
        self.get_logger().info(f'Timer Node initialized at {1/sample_time:.0f} Hz')

        self.pointcloud_publisher_ = self.create_publisher(PointCloud2, 'sonar_point_cloud', 10)
        self.image_publisher_ = self.create_publisher(Image, 'sonar_range_image', 10)

        sonar = wlsonar.Sonar3D(self.sonar_ip)
        # sonar.set_acoustics_enabled(True) # Don't default on
        # self.get_logger().info('Acoustics enabled')
        sonar.set_udp_multicast()
        self.get_logger().info('UDP multicast enabled')

        self.sock = wlsonar.open_sonar_udp_multicast_socket()
        self.get_logger().info(
            f'Listening for RIP2 packets on '
            f'{wlsonar.DEFAULT_MCAST_GRP}:{wlsonar.DEFAULT_MCAST_PORT}...'
        )
        if self.sonar_ip:
            self.get_logger().info(f'Filtering packets from IP: {self.sonar_ip}')

    def timer_callback(self):
        data, addr = self.sock.recvfrom(wlsonar.UDP_MAX_DATAGRAM_SIZE)

        if addr[0] != self.sonar_ip and addr[0] != wlsonar.FALLBACK_IP:
            self.get_logger().info(
                f'Received packet from {addr[0]}, expected {self.sonar_ip} — skipping.'
            )
            return

        try:
            msg = rip.unpackb(data)
        except rip.UnknownProtobufTypeError:
            return
        except (rip.CRCMismatchError, rip.BadIDError) as e:
            self.get_logger().warning(f'Packet error: {e}')
            return

        if not isinstance(msg, rip.RangeImage):
            return

        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'sonar_frame'

        voxels = wlsonar.range_image_to_xyz(msg)
        pts = [v for v in voxels if v is not None]
        cloud_msg = point_cloud2.create_cloud_xyz32(header, pts)
        self.pointcloud_publisher_.publish(cloud_msg)

        distances = wlsonar.range_image_to_distance(msg)
        img_msg = Image()
        img_msg.header = header
        img_msg.height = msg.height
        img_msg.width = msg.width
        img_msg.encoding = '32FC1'
        img_msg.is_bigendian = False
        img_msg.step = msg.width * 4
        img_msg.data = np.array(distances, dtype=np.float32).tobytes()
        self.image_publisher_.publish(img_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TimerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
