import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from sensor_msgs.msg import Joy

import can
import cantools

###
# dead mean switch


class SimpleSDRAC_control(Node):
  def __init__(self):
    super().__init__("lemonx_joy_publisher")
    # self.publisher_ = self.create_publisher(Joy, "joy", 10)
    self.reciver = self.create_subscription(Joy, "joy", self.reciver_callback, 10)
    self.last_connection = self.get_clock().now()
    timer_period = 0.1  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.can_bus = can_bus = can.interface.Bus('can0', bustype='socketcan', bitrate=100000)
    self.can_db = cantools.database.load_file('can/can.dbc')
    self.msg_status = self.can_db.get_message_by_name('konarm_1_status')
    self.msg_set_pos = self.can_db.get_message_by_name('konarm_1_set_pos')
    self.msg_get_pos = self.can_db.get_message_by_name('konarm_1_get_pos')
    self.conncected = False

  def reciver_callback(self, msg):
    self.axes = msg.axes
    self.buttons = msg.buttons
    self.last_connection = self.get_clock().now()
    self.conncected = True

  def timer_callback(self):
    if self.get_clock().now() - self.last_connection > Duration(seconds=1):
      self.conncected = False
    
    if self.conncected:
      # self.get_logger().info("axes: %s, buttons: %s" % (self.axes, self.buttons))
      velocity = self.axes[1]
      data = self.msg_set_pos.encode({"position": 0, "velocity": velocity})
      self.get_logger().info(f"data: {velocity}")
      msg = can.Message(arbitration_id=self.msg_set_pos.frame_id, data=data, is_extended_id=False)
      self.can_bus.send(msg)
    else:
      self.get_logger().info("No connection")


def main(args=None):
  rclpy.init(args=args)
  minimal_publisher = SimpleSDRAC_control()
  rclpy.spin(minimal_publisher)
  minimal_publisher.destroy_node()
  rclpy.shutdown()


if __name__ == "__main__":
  main()
