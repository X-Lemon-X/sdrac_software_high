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

function install_program () {
  if ! [ -x "$(command -v $1)" ]; then
  echo -e "${ORANGE}Installing $1${NC}"
  sudo apt-get install $1 -y
else
  echo -e "${BLUE}$1 is installed${NC}"
fi
}

function check_if_program_is_installed () {
  if ! [ -x "$(command -v $1)" ]; then
  echo -e "${RED}Error: $1 is not installed.${NC}"
  #ask user if he wants to install the program
  read -p "Do you want to install $1? (y/n)" -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_program $1
  else
    echo -e "${ORANGE}Exiting...${NC}"
    exit 1
  fi
else
  echo -e "${BLUE}$1 is installed${NC}"
fi
}


#check if required programs are installed
check_if_program_is_installed "cantools"


# get all fiels in /dev that contain the bus number
devs=$(ls /dev | grep tty)

device_path=""
#iterate over all devices
for dev in $devs; do
  # get the bus number of the device
  device_info=$(udevadm info /dev/$dev)
  venid=$(echo $device_info | grep -o -E "ID_VENDOR_ID=$vendor_id" | grep -o $vendor_id)
  prodid=$(echo $device_info | grep -o -E "ID_MODEL_ID=$product_id"  | grep -o $product_id)
  # venenc=$(echo $device_info | grep -o -E "ID_VENDOR_ENC=$vendor_enc"  | grep -o $vendor_enc)

  if [ -z $venid ] || [ -z $prodid ] ; then
    continue
  fi

  echo -e "${GREEN}Can-hat found on: /dev/$dev${NC}"
  # echo -e "${GREEN}ID: $venid:$prodid  ENC: $venenc${NC}"
  device_path="/dev/$dev"
  break
done

if [ -z $device_path ]; then
  echo -e "${RED}No can-hat found${NC}"
  exit 1
fi

echo -e "${BLUE}Seting up Can: $device_path${NC}"

sudo slcand -o -c -s8 $device_path $name_of_can_interface
sudo ip link set dev $name_of_can_interface up type can bitrate $bitrate

if [ $? -ne 0 ]; then
  echo -e "${RED}Error flashing the device${NC}"
  exit 1
else
  echo -e "${ORANGE}Device flashed successfully!${NC}"
fi
exit 0








