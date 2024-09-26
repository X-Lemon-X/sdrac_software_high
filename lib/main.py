import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from sensor_msgs.msg import Joy
import time
import can
import cantools

###
# dead mean switch


class SimpleSDRAC_control(Node):
  def __init__(self):
    super().__init__(node_name="robot_rc_controler")
    # self.publisher_ = self.create_publisher(Joy, "joy", 10)
    self.reciver = self.create_subscription(Joy, "joy", self.reciver_callback, 10)
    self.connction_timeout = Duration(seconds=1)
    self.last_connection = self.get_clock().now() - self.connction_timeout - Duration(seconds=1)
    self.rc_connection_chenge = True
    self.conncected = False


    timer_period = 1/50  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.axes = [0, 0, 0, 0, 0, 0]
    self.buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    
    self.can_bus = can.interface.Bus('can0', bustype='socketcan', bitrate=100000)
    self.can_bus.flush_tx_buffer()
    self.can_db = cantools.database.load_file('lib/ariadna_constants/can_messages/output/can.dbc')


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
      'konarm_4_status': self.can_db.get_message_by_name('konarm_4_status'),
      'konarm_4_set_pos': self.can_db.get_message_by_name('konarm_4_set_pos'),
      'konarm_4_get_pos': self.can_db.get_message_by_name('konarm_4_get_pos'),
      'konarm_5_status': self.can_db.get_message_by_name('konarm_5_status'),
      'konarm_5_set_pos': self.can_db.get_message_by_name('konarm_5_set_pos'),
      'konarm_5_get_pos': self.can_db.get_message_by_name('konarm_5_get_pos'),
      'konarm_6_status': self.can_db.get_message_by_name('konarm_6_status'),
      'konarm_6_set_pos': self.can_db.get_message_by_name('konarm_6_set_pos'),
      'konarm_6_get_pos': self.can_db.get_message_by_name('konarm_6_get_pos'),
    }


    self.konarms_id_to_name = {}
    self.konarms_msg_to_id = {}
    for key, value in self.konarms_can_messages.items():
      self.konarms_id_to_name[value.frame_id] = key
      self.konarms_msg_to_id[key] = value.frame_id

    self.konarms_can_id_messages_decode = {}
    for key, value in self.konarms_can_messages.items():
      self.konarms_can_id_messages_decode[value.frame_id] = value.decode

    self.msg_status = self.can_db.get_message_by_name('konarm_1_status')
    self.msg_set_pos = self.can_db.get_message_by_name('konarm_1_set_pos')
    self.msg_get_pos = self.can_db.get_message_by_name('konarm_1_get_pos')

  def __del__(self):
    self.can_bus.shutdown()

  def reciver_callback(self, msg):
    self.axes = msg.axes
    self.buttons = msg.buttons
    self.last_connection = self.get_clock().now()

  def send_data_to_can(self):
    can_msges = []
    ## joint 1
    sp_1 = self.konarms_can_messages['konarm_1_set_pos']
    data = sp_1.encode({"position": 0, "velocity": self.axes[0]})
    can_msges.append(can.Message(arbitration_id=sp_1.frame_id, data=data, is_extended_id=True))
    
    ## joint 2
    sp_2 = self.konarms_can_messages['konarm_2_set_pos']
    data = sp_2.encode({"position": 0, "velocity": self.axes[1]})
    can_msges.append(can.Message(arbitration_id=sp_2.frame_id, data=data, is_extended_id=True))
    
    ## joint 3
    sp_3 = self.konarms_can_messages['konarm_3_set_pos']
    data = sp_3.encode({"position": 0, "velocity": self.axes[2]})
    can_msges.append(can.Message(arbitration_id=sp_3.frame_id, data=data, is_extended_id=True))
    
    ## joint 4
    sp_4 = self.konarms_can_messages['konarm_4_set_pos']
    data = sp_4.encode({"position": 0, "velocity": self.axes[3]})
    can_msges.append(can.Message(arbitration_id=sp_4.frame_id, data=data, is_extended_id=True))
    ## joint 5
    sp_5 = self.konarms_can_messages['konarm_5_set_pos']
    data = sp_5.encode({"position": 0, "velocity": self.axes[4]})
    can_msges.append(can.Message(arbitration_id=sp_5.frame_id, data=data, is_extended_id=True))
    ## joint 6
    # sp_6 = self.konarms_can_messages['konarm_6_set_pos']
    # data = sp_6.encode({"position": 0, "velocity": self.axes[5]})
    # can_msges.append(can.Message(arbitration_id=sp_6.frame_id, data=data, is_extended_id=True))

    ## get pos
    ## joint 1
    sp_1g = self.konarms_can_messages['konarm_1_get_pos']
    can_msges.append(can.Message(arbitration_id=sp_1g.frame_id,is_remote_frame=True,is_extended_id=True))

    ## joint 2
    sp_1g = self.konarms_can_messages['konarm_2_get_pos']
    can_msges.append(can.Message(arbitration_id=sp_1g.frame_id,is_remote_frame=True,is_extended_id=True))

    ## joint 3
    sp_1g = self.konarms_can_messages['konarm_3_get_pos']
    can_msges.append(can.Message(arbitration_id=sp_1g.frame_id,is_remote_frame=True,is_extended_id=True))

    ## joint 4
    sp_1g = self.konarms_can_messages['konarm_4_get_pos']
    can_msges.append(can.Message(arbitration_id=sp_1g.frame_id,is_remote_frame=True,is_extended_id=True))

    ## joint 5
    sp_1g = self.konarms_can_messages['konarm_5_get_pos']
    can_msges.append(can.Message(arbitration_id=sp_1g.frame_id,is_remote_frame=True,is_extended_id=True))

    ## joint 6
    sp_1g = self.konarms_can_messages['konarm_6_get_pos']
    can_msges.append(can.Message(arbitration_id=sp_1g.frame_id,is_remote_frame=True,is_extended_id=True))

    for msg in can_msges:
      self.send_can(msg)

  def read_data_from_can(self):
    try:
      messages=  self.can_bus.recv(0.01)
      if messages is not None:
        if(messages.arbitration_id in self.konarms_id_to_name):
          decode_func = self.konarms_can_id_messages_decode[messages.arbitration_id]
          data = decode_func(messages.data)
          self.get_logger().info(f"id: {self.konarms_id_to_name[messages.arbitration_id]}  data: {data}")
        else:
          self.get_logger().info(f"UNNOWN id: {messages.arbitration_id}")

    except can.exceptions.CanOperationError as e:
      self.get_logger().error(f"Timout RX")

  def send_can(self, can_msg:can.Message):
    max_send_tries = 5
    while max_send_tries > 0:
      try:
        self.can_bus.send(can_msg)
        self.read_data_from_can()
        break
      except can.exceptions.CanOperationError as e:
        self.get_logger().error(f"Error: {e}")
        self.can_bus.flush_tx_buffer()
        max_send_tries -= 1
        time.sleep(0.1) 

  def set_pos_konarm(self, pos, vel, id):
    data = self.msg_set_pos.encode({"position": pos, "velocity": vel})
    msg = can.Message(arbitration_id=id, data=data, is_extended_id=True)
    self.send_can(msg)
    # self.get_logger().info(f"ID SET POS: {id}")

  def get_pos_konarm(self, id):
    # data = self.msg_get_pos.encode({'position': 0, 'velocity': 0})
    msg = can.Message(arbitration_id=id, is_extended_id=False, is_remote_frame=True,check=True)
    self.send_can(msg)
  
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
        self.fixed_axis = []
        for axis in self.axes:
          if abs(axis) < 0.06:
            self.fixed_axis.append(0)
          else:
            self.fixed_axis.append(axis)

        # self.set_pos_konarm(0, self.fixed_axis[0], self.konarms_msg_to_id['konarm_1_set_pos'])
        # self.read_data_from_can()
        # self.set_pos_konarm(0, self.fixed_axis[1], self.konarms_msg_to_id['konarm_2_set_pos'])
        # self.read_data_from_can()
        # self.set_pos_konarm(0, self.fixed_axis[2], self.konarms_msg_to_id['konarm_3_set_pos'])
        # self.read_data_from_can()
        # self.set_pos_konarm(0, self.fixed_axis[3], self.konarms_msg_to_id['konarm_4_set_pos'])
        # self.read_data_from_can()
        # self.set_pos_konarm(0, self.fixed_axis[4], self.konarms_msg_to_id['konarm_5_set_pos'])
        # self.read_data_from_can()
        # self.set_pos_konarm(0, self.fixed_axis[5], self.konarms_msg_to_id['konarm_6_set_pos'])
        # self.read_data_from_can()
        # sp_1g = self.konarms_msg_to_id['konarm_5_get_pos']
        # msg = can.Message(arbitration_id=sp_1g,is_remote_frame=True)
        # self.can_bus.send(msg,timeout=0.1)

        # velocity = self.fixed_axis[4]
        # self.set_pos_konarm(0, velocity, self.konarms_msg_to_id['konarm_5_set_pos'])
        # self.get_pos_konarm(self.konarms_msg_to_id['konarm_5_get_pos'])
        # print(self.fixed_axis)
        # self.read_data_from_can()
        
        self.send_data_to_can()
        # self.get_pos_konarm(self.konarms_msg_to_id['konarm_2_get_pos'])
        # self.get_pos_konarm(self.konarms_msg_to_id['konarm_3_get_pos'])
        # self.read_data_from_can()
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
