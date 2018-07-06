#!/usr/bin/env python
"""
Get information from rosbag
"""
import os
import sys
import argparse
import rosbag
import datetime
from rospy import Time


def get_info(filepath):
    bag = rosbag.Bag(filepath)

    start_time = datetime.datetime.fromtimestamp(bag.get_start_time())
    end_time = datetime.datetime.fromtimestamp(bag.get_end_time())
    duration = end_time - start_time
    duration_hours = int(duration.total_seconds() // 3600)
    duration_minutes = int(duration.total_seconds() // 60)
    duration_seconds = int(duration.total_seconds() % 60)
    duration_str = "{0:02d}:{1:02d}:{2:02d}".format(duration_hours, duration_minutes, duration_seconds)

    time_format = '%H:%M:%S'
    print("{0},{1},{2}".format(start_time.strftime(time_format),
                               end_time.strftime(time_format),
                               duration_str))
    sys.stdout.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get information from rosbag")
    parser.add_argument("input_file")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        raise IOError("File {} does not exist".format(args.input_file))

    get_info(args.input_file)
