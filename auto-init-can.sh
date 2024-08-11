vendor_id="16d0"
product_id="117e"
vendor_enc="Openlight\x20Labs"

bitrate="1000000"
name_of_can_interface="can0"


RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

function check_if_program_is_installed () {
  if ! [ -x "$(command -v $1)" ]; then
    echo -e "${RED}Error: $1 is not installed.${NC}"
    sudo apt-get install $2 -y
  else
    echo -e "${BLUE}$1 is installed${NC}"
  fi
}

## check if can interface is UP

if sudo ip addr show $name_of_can_interface 2>/dev/null | grep -q "UP"; then
echo -e "${ORANGE}Can is already UP!${NC}"
exit 0
fi

check_if_program_is_installed "slcand" "can-utils"
check_if_program_is_installed "ifconfig" "net-tools"

# get all fiels in /dev that contain the bus number
devs=$(ls /dev | grep tty)
device_path=""
#iterate over all devices
for dev in $devs; do
  # get the bus number of the device
  device_info=$(udevadm info /dev/$dev)
  venid=$(echo $device_info | grep -o -E "ID_VENDOR_ID=$vendor_id" | grep -o $vendor_id)
  prodid=$(echo $device_info | grep -o -E "ID_MODEL_ID=$product_id"  | grep -o $product_id)
  if [ -z $venid ] || [ -z $prodid ] ; then
    continue
  fi
  echo -e "${GREEN}Can-hat found on: /dev/$dev${NC}"
  device_path="/dev/$dev"
  break
done

if [ -z $device_path ]; then
  echo -e "${RED}No can-hat found${NC}"
  exit 1
fi

echo -e "${BLUE}Seting up Can: $device_path${NC}"

architecture=$(uname -m)
arch_x86=$(echo $architecture | grep -o "x86")
arch_arm=$(echo $architecture | grep -o "ar")

if [[ $arch_x86 == 'x86' ]]; then
  echo -e "${ORANGE}Architecture x86 ${NC}"
  sudo slcand -o -c -s8 $device_path $name_of_can_interface
  sudo ip link set dev $name_of_can_interface up type can bitrate $bitrate
elif [[ $arch_arm == 'ar' ]]; then
  echo -e "${ORANGE}Architecture ARM ${NC}"
  sudo slcand -o -c -s8 $device_path $name_of_can_interface
  sudo ip link set up $name_of_can_interface
else
  echo -e "${RED}Error: unnknown architecture${NC}"
  echo -e "${ORANGE}Trying to start can anyway${NC}"
  sudo slcand -o -c -s8 $device_path $name_of_can_interface
  sudo ip link set up $name_of_can_interface
fi  

sudo ifconfig $name_of_can_interface txqueuelen 1000

if [ $? -ne 0 ]; then
  echo -e "${RED}Error starting can ${NC}"
  exit 1
else
  echo -e "${ORANGE}Can started successfully!${NC}"
fi
exit 0








