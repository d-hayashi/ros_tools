#!/usr/bin/env bash

bag_file=${1}
ros_port=11315

if [ "${bag_file}" == "" ]; then
	echo "please specify bag file"
	sleep 10
	exit 1
fi

# check file existance
if [ ! -f "${bag_file}" ]; then
	echo "bag file does not exist: ${bag_file}"
	sleep 10
	exit 1
fi

# environment variables
export ROS_HOSTNAME=$(hostname)
export ROS_MASTER_URI=http://$(hostname):${ros_port}

# check if roscore is already running using the ros_port
rosout=$(rostopic list 2> /dev/null | grep "/rosout")
if [ "${rosout}" != "" ]; then
	echo "port ${ros_port} is already used by another server"
	sleep 10
	exit 1
fi

# start roscore server
roscore -p ${ros_port} &
sleep 1

# start rqt_bag
rqt_bag ${bag_file} &
rqt_image_view
