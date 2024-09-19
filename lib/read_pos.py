import can
import time
import cantools

can_db = cantools.database.load_file('can/can.dbc')
konarms_can_messages = {
  'konarm_1_status': can_db.get_message_by_name('konarm_1_status'),
  'konarm_1_set_pos': can_db.get_message_by_name('konarm_1_set_pos'),
  'konarm_1_get_pos': can_db.get_message_by_name('konarm_1_get_pos'),
  'konarm_2_status': can_db.get_message_by_name('konarm_2_status'),
  'konarm_2_set_pos': can_db.get_message_by_name('konarm_2_set_pos'),
  'konarm_2_get_pos': can_db.get_message_by_name('konarm_2_get_pos'),
  'konarm_3_status': can_db.get_message_by_name('konarm_3_status'),
  'konarm_3_set_pos': can_db.get_message_by_name('konarm_3_set_pos'),
  'konarm_3_get_pos': can_db.get_message_by_name('konarm_3_get_pos'),
}
msg_status = can_db.get_message_by_name('konarm_1_status')
msg_set_pos = can_db.get_message_by_name('konarm_1_set_pos')
msg_get_pos = can_db.get_message_by_name('konarm_1_get_pos')

bus = can.interface.Bus(channel='can0', bustype='socketcan')

def send_can_request():

  # Create a new request message
  data = msg_get_pos.encode({'position': 0, 'velocity': 0})
  msg = can.Message(arbitration_id=msg_get_pos.frame_id, is_extended_id=False, is_remote_frame=True)

  # Send the request message
  bus.send(msg)

  # Wait for the response message
  response_msg = bus.recv(timeout=1.0)

  # Check if a response was received
  if response_msg is not None:
    # Process the response message
    pos =  msg_get_pos.decode(response_msg.data)
    print("Operating System Information:", pos)
  else:
    print("No response received.")

if __name__ == "__main__":
  try:
    while True:
      send_can_request()
      time.sleep(0.1)
  except KeyboardInterrupt:
    bus.shutdown()
    print("Program terminated by user.")  
