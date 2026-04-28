import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2, PointField, Image
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header

import numpy as np
import wlsonar
import wlsonar.range_image_protocol as rip

_XYZI_FIELDS = [
    PointField(name='x',         offset=0,  datatype=PointField.FLOAT32, count=1),
    PointField(name='y',         offset=4,  datatype=PointField.FLOAT32, count=1),
    PointField(name='z',         offset=8,  datatype=PointField.FLOAT32, count=1),
    PointField(name='intensity', offset=12, datatype=PointField.FLOAT32, count=1),
]

_MAX_CACHE = 5  # unpaired messages to hold before dropping


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
        self.range_image_publisher_ = self.create_publisher(Image, 'sonar_range_image', 10)
        self.signal_image_publisher_ = self.create_publisher(Image, 'sonar_signal_image', 10)

        sonar = wlsonar.Sonar3D(self.sonar_ip)
        # sonar.set_acoustics_enabled(True)  # Don't default on
        sonar.set_udp_multicast()
        self.get_logger().info('UDP multicast enabled')

        self.sock = wlsonar.open_sonar_udp_multicast_socket()
        self.get_logger().info(
            f'Listening for RIP2 packets on '
            f'{wlsonar.DEFAULT_MCAST_GRP}:{wlsonar.DEFAULT_MCAST_PORT}...'
        )
        if self.sonar_ip:
            self.get_logger().info(f'Filtering packets from IP: {self.sonar_ip}')

        self._range_cache: dict[int, rip.RangeImage] = {}
        self._bitmap_cache: dict[int, rip.BitmapImageGreyscale8] = {}

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

        seq_id = msg.header.sequence_id

        if isinstance(msg, rip.RangeImage):
            self._range_cache[seq_id] = msg
        elif isinstance(msg, rip.BitmapImageGreyscale8):
            if msg.type == rip.BitmapImageType.SIGNAL_STRENGTH_IMAGE:
                self._bitmap_cache[seq_id] = msg
        else:
            return

        self._try_publish_pair(seq_id)
        self._evict_old_entries()

    def _try_publish_pair(self, seq_id: int):
        range_msg = self._range_cache.get(seq_id)
        bitmap_msg = self._bitmap_cache.get(seq_id)

        if range_msg is None or bitmap_msg is None:
            return

        del self._range_cache[seq_id]
        del self._bitmap_cache[seq_id]

        header = Header()
        header.stamp.sec = range_msg.header.timestamp.seconds
        header.stamp.nanosec = range_msg.header.timestamp.nanos
        header.frame_id = 'sonar_frame'

        voxels = wlsonar.range_image_to_xyz(range_msg)
        strengths = wlsonar.bitmap_image_to_strength_log(bitmap_msg)

        pts = []
        for i, v in enumerate(voxels):
            if v is not None:
                x, y, z = v
                pts.append((x, y, z, float(strengths[i])))

        self.pointcloud_publisher_.publish(
            point_cloud2.create_cloud(header, _XYZI_FIELDS, pts)
        )

        distances = wlsonar.range_image_to_distance(range_msg)
        range_img = Image()
        range_img.header = header
        range_img.height = range_msg.height
        range_img.width = range_msg.width
        range_img.encoding = '32FC1'
        range_img.is_bigendian = False
        range_img.step = range_msg.width * 4
        range_img.data = np.array(distances, dtype=np.float32).tobytes()
        self.range_image_publisher_.publish(range_img)

        signal_img = Image()
        signal_img.header = header
        signal_img.height = bitmap_msg.height
        signal_img.width = bitmap_msg.width
        signal_img.encoding = '32FC1'
        signal_img.is_bigendian = False
        signal_img.step = bitmap_msg.width * 4
        signal_img.data = np.array(strengths, dtype=np.float32).tobytes()
        self.signal_image_publisher_.publish(signal_img)

    def _evict_old_entries(self):
        for cache in (self._range_cache, self._bitmap_cache):
            if len(cache) > _MAX_CACHE:
                oldest = min(cache)
                self.get_logger().warning(
                    f'Dropping unpaired sequence_id {oldest} — no matching message arrived.'
                )
                del cache[oldest]


def main(args=None):
    rclpy.init(args=args)
    node = TimerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
