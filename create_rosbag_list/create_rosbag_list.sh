#!/usr/bin/env bash

#
# Remove omron related topics from rosbag
#

function usage() {
        echo "Usage:"
        echo "create_rosbag_list.sh <original directory> <splitted directory>"
        echo "--- arguments ---"
        echo "<original directory>: path of the directory where original rosbag files exist"
        echo "<splitted directory>: path of the directory where splitted rosbag files (or sub-directories) exist"
        echo "-----------------"
	echo "If <splitted directory> is not specified, rosbag files in original directory will be analyzed."
        echo "-----------------"
}
export -f usage


function header() {
	echo "元bagファイル名,作成したファイル名,開始フレーム,終了フレーム,開始時間,終了時間,時間,メモ(トンネル、橋など),size"
}
export -f header

function header2() {
	echo "ファイル名,開始フレーム,終了フレーム,開始時間,終了時間,時間,メモ(トンネル、橋など),size"
}
export -f header2

function get_rosbag_info() {
	#echo -n ${1##*/}
	echo -n ",,,"
	echo -n `python get_rosbag_info.py $1`
	echo -n ","
	echo -n ","
	echo -n `du -h $1 | awk '{print $1}'`
}
export -f get_rosbag_info

function didFindOriginalBagFile() {
	# echo "found $1"
	filename=${1##*/}
	temp=${filename%.*}
	candidate_name=${temp#*__}
	# echo "candidate name: ${candidate_name}"
	#find ${splittedDirectory} -mindepth 1 -maxdepth 3 -name "*${candidate_name}*" | xargs -I{} -P1 bash -c "export index=0; didFindSplittedBagFile {}"

	index=0
	splittedFiles=`find ${splittedDirectory} -mindepth 1 -maxdepth 3 -name "*${candidate_name}*" | sort`
	#if [ "${splittedFiles}" == "" ]; then
	#	echo "${filename},,,,,,,"
	#fi

	echo -n "${filename},"
	get_rosbag_info ${1}
	echo ""

	for file in ${splittedFiles};
	do
		echo -n ","
		echo -n ${file##*/}
		get_rosbag_info $file
		echo ""
		index=$(( index + 1 ))
	done

}
export -f didFindOriginalBagFile

originalDirectory=$1
splittedDirectory=$2

# debug
#originalDirectory=/media/d_hayashi/128GB/omron
#splittedDirectory=/media/d_hayashi/128GB/omron/Road1

# check args
if [ "${originalDirectory}" == "" ]; then
	echo "Please specify original directory"
	usage
	exit 1
fi

# check directory
if [ ! -d ${originalDirectory} ]; then
	echo "Directory ${originalDirectory} does not exist, please check it."
	exit 1
fi

# single directory mode
if [ "${splittedDirectory}" == "" ]; then
	header2
	for file in `find ${originalDirectory} -mindepth 1 -maxdepth 3 -name "*.bag" | sort`;
	do
		echo -n "${file##*/}"
		get_rosbag_info ${file}
		echo ""
	done
	exit 0
fi

## check directory
if [ ! -d ${splittedDirectory} ]; then
	echo "Directory ${splittedDirectory} does not exist, please check it."
	exit 1
fi

# find rosbag files
# echo "Searching rosbag files..."

header

export originalDirectory=${originalDirectory}
export splittedDirectory=${splittedDirectory}
find ${originalDirectory} -mindepth 1 -maxdepth 1 -name "*.bag" | sort | xargs -I{} -P1 bash -c "didFindOriginalBagFile {}"
