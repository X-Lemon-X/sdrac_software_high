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
    super().__init__("robot_rc_controler")
    # self.publisher_ = self.create_publisher(Joy, "joy", 10)
    self.reciver = self.create_subscription(Joy, "joy", self.reciver_callback, 10)
    self.connction_timeout = Duration(seconds=1)
    self.last_connection = self.get_clock().now() - self.connction_timeout - Duration(seconds=1)
    self.rc_connection_chenge = True
    self.conncected = False


    timer_period = 1/10  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.axes = [0, 0, 0, 0, 0, 0]
    self.buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    
    self.can_bus = can_bus = can.interface.Bus('can0', bustype='socketcan', bitrate=100000)
    self.can_db = cantools.database.load_file('can/can.dbc')


    self.konarms_can_messages = {
      'konarm_1_status': self.can_db.get_message_by_name('konarm_1_status'),
      'konarm_1_set_pos': self.can_db.get_message_by_name('konarm_1_set_pos'),
      'konarm_1_get_pos': self.can_db.get_message_by_name('konarm_1_get_pos'),
      'konarm_2_status': self.can_db.get_message_by_name('konarm_2_status'),
      'konarm_2_set_pos': self.can_db.get_message_by_name('konarm_2_set_pos'),
      'konarm_2_get_pos': self.can_db.get_message_by_name('konarm_2_get_pos'),
      'konarm_3_status': self.can_db.get_message_by_name('konarm_3_status'),
      'konarm_3_set_pos': self.can_db.get_message_by_name('konarm_3_set_pos'),
      'konarm_3_get_pos': self.can_db.get_message_by_name('konarm_3_get_pos'),
    }

    self.msg_status = self.can_db.get_message_by_name('konarm_1_status')
    self.msg_set_pos = self.can_db.get_message_by_name('konarm_1_set_pos')
    self.msg_get_pos = self.can_db.get_message_by_name('konarm_1_get_pos')

  def reciver_callback(self, msg):
    self.axes = msg.axes
    self.buttons = msg.buttons
    self.last_connection = self.get_clock().now()


  def send_data_to_can(self):
    # joint 1
    can_msges = []
    sp_1 = self.konarms_can_messages['konarm_1_set_pos']
    data = sp_1.encode({"position": 0, "velocity": self.axes[0]})
    can_msges.append(can.Message(arbitration_id=sp_1.frame_id, data=data, is_extended_id=False))
    
    # joint 2
    sp_2 = self.konarms_can_messages['konarm_2_set_pos']
    data = sp_2.encode({"position": 0, "velocity": self.axes[1]})
    can_msges.append(can.Message(arbitration_id=sp_2.frame_id, data=data, is_extended_id=False))
    # joint 3
    sp_3 = self.konarms_can_messages['konarm_3_set_pos']
    data = sp_3.encode({"position": 0, "velocity": self.axes[2]})
    can_msges.append(can.Message(arbitration_id=sp_3.frame_id, data=data, is_extended_id=False))
    # joint 4
    sp_4 = self.konarms_can_messages['konarm_4_set_pos']
    data = sp_4.encode({"position": 0, "velocity": self.axes[3]})
    can_msges.append(can.Message(arbitration_id=sp_4.frame_id, data=data, is_extended_id=False))
    # joint 5
    sp_5 = self.konarms_can_messages['konarm_5_set_pos']
    data = sp_5.encode({"position": 0, "velocity": self.axes[4]})
    can_msges.append(can.Message(arbitration_id=sp_5.frame_id, data=data, is_extended_id=False))
    # joint 6
    sp_6 = self.konarms_can_messages['konarm_6_set_pos']
    data = sp_6.encode({"position": 0, "velocity": self.axes[5]})
    can_msges.append(can.Message(arbitration_id=sp_6.frame_id, data=data, is_extended_id=False))
    
    for msg in can_msges:
      self.can_bus.send(msg)

  def read_data_from_can(self):
    try:
      pass
    except can.exceptions.CanOperationError as e:
      self.get_logger().error(f"Timout RX")

  def timer_callback(self):
    try:
      if self.get_clock().now() - self.last_connection > self.connction_timeout:
        if self.conncected:
          self.rc_connection_chenge = True
        self.conncected = False
        self.axes = [0, 0, 0, 0, 0, 0]
        self.buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      else:
        if not self.conncected:
          self.rc_connection_chenge = True
        self.conncected = True

      if self.conncected and self.rc_connection_chenge:
        self.get_logger().info("Control node connected")
        self.rc_connection_chenge = False
      elif not self.conncected and self.rc_connection_chenge:
        self.get_logger().info("Control node disconnected")
        self.rc_connection_chenge = False

      if self.conncected:
        velocity = self.axes[1]*2
        data = self.msg_set_pos.encode({"position": 0, "velocity": velocity})
        msg = can.Message(arbitration_id=self.msg_set_pos.frame_id, data=data, is_extended_id=False)
        self.can_bus.send(msg)
        # self.get_logger().info(f"velocity: {velocity}")


        data = self.msg_get_pos.encode({'position': 0, 'velocity': 0})
        msg = can.Message(arbitration_id=self.msg_get_pos.frame_id, is_extended_id=False, is_remote_frame=True)
        self.can_bus.send(msg)

        messages=  self.can_bus.recv(0.05)
        if messages is not None:
          
          if(messages.arbitration_id == self.msg_get_pos.frame_id):
            data = self.msg_get_pos.decode(messages.data)
            pos = data['position']
            vel = data['velocity']
            self.get_logger().info(f"id: {messages.arbitration_id}  pos: {pos} vel: {vel}")
          else:
            self.get_logger().info(f"UNNOWN id: {messages.arbitration_id}")
          
      
    except can.exceptions.CanOperationError as e:
      self.get_logger().error(f"Error: {e}")

def main(args=None):
  rclpy.init(args=args)
  minimal_publisher = SimpleSDRAC_control()
  rclpy.spin(minimal_publisher)
  minimal_publisher.destroy_node()
  rclpy.shutdown()


if __name__ == "__main__":

  main()
