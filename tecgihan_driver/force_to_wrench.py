#!/usr/bin/env python

from geometry_msgs.msg import Vector3Stamped, WrenchStamped

import rclpy

from rclpy.node import Node


class ForceToWrench(Node):
    """ROS Node for converting Vector3Stamped to WrenchStamped ROS Topic."""

    def __init__(self):
        """Construct ForceToWrench."""
        super().__init__('force_to_wrench_node')

        input_topic = '/dma03_publisher/force'
        output_topic = '/dma03_publisher/wrench'

        # Subscribe to Vector3Stamped messages
        self.subscription = self.create_subscription(
            Vector3Stamped,
            input_topic,
            self.listener_callback,
            10
        )

        # Publisher for WrenchStamped messages
        self.publisher = self.create_publisher(
            WrenchStamped,
            output_topic,
            10
        )

        self.get_logger().info('Force to Wrench Node has been started.')

    def listener_callback(self, msg: Vector3Stamped):
        """Be called when ROS Topic `/dma03_publisher/force` is published.

        Args:
            msg (Vector3Stamped): ROS Topic Data
        """
        # Create a WrenchStamped message and copy the vector to the force field
        wrench_msg = WrenchStamped()
        wrench_msg.header = msg.header  # Copy the header from the input message
        wrench_msg.wrench.force = msg.vector

        # Set torque to zero
        wrench_msg.wrench.torque.x = 0.0
        wrench_msg.wrench.torque.y = 0.0
        wrench_msg.wrench.torque.z = 0.0

        self.publisher.publish(wrench_msg)
        self.get_logger().debug(
            f'Published WrenchStamped: force=({msg.vector.x}, {msg.vector.y}, {msg.vector.z})')


def main(args=None):
    """Execute ROS Node with ForceToWrench."""
    rclpy.init(args=args)
    node = ForceToWrench()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
