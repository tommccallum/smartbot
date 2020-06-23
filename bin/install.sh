#!/bin/bash

# This will install the different bits to
# cron and logrotate and /opt/smartbot etc
# it is the equivalent of docker
#!/bin/bash

IS_DOCKER=$( cat /proc/1/cgroup | grep docker | wc -l | awk '{print $1}' )
IS_BLUETOOTH=$( ps aux | grep bluetoothd | wc -l )

# get directory that this script is in
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"
# check for python3
PYTHON=$( which python3 )
LOCAL_CONFIG="$HOME/.config/smartbot"
INSTALL_LOG="${DIR}/log/install.log"
FORCE_INSTALL=0
DEFAULT_CONF="default"

function usage() {
  echo "./install.sh [-c|--config file] [-r|--reset]"
  exit 1
}

while [ "$1" != "" ]
do
  case $1 in
    -r | --reset ) shift
                    FORCE_INSTALL=1
    ;;
    -c | --config ) shift
                    DEFAULT_CONF=$1
                    ;;
    * )             usage
                    exit 1
    esac
    shift
done

if [ -e "${LOCAL_CONFIG}" -a $FORCE_INSTALL -eq 0 ]
then
  echo "Installation already found, to reinstall type './smartbot reset' argument"
  exit 1
fi

if [ ! -e "$DIR/log" ]
then
  echo "Creating log directory in '$DIR/log'"
  mkdir $DIR/log
else
  echo "Log directory found at '$DIR/log'"
fi

if [ -e "${INSTALL_LOG}" ]
then
  rm -f "${INSTALL_LOG}"
  touch "${INSTALL_LOG}"
fi

echo "Installing dependencies"
${DIR}/bin/install_deps.sh  "${LOCAL_CONFIG}" "${DEFAULT_CONF}" 2>&1 | tee -a ${INSTALL_LOG}