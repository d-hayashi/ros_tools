#!/usr/bin/env python
"""
Split rosbag file based on csv file
"""

import os
import sys
import argparse
import logging
import csv
import datetime
import time
import rosbag
import subprocess

args = None


class FilterJob(object):
    def __init__(self, input_file, output_file, start, end, input_dir="./", output_dir="./"):
        self.logger = logging.getLogger(name=type(self).__name__)
        self.input_file = os.path.join(input_dir, input_file)
        self.output_file = os.path.join(output_dir, output_file)
        if start is None:
            self.start = None
        if ":" in start:
            if "." in start:
                if len(start.split(".")[1]) > 6:
                    start = "{0}.{1}".format(start.split(".")[0], start.split(".")[1][0:6])
                self.start = datetime.datetime.strptime(start, "%H:%M:%S.%f")
            else:
                self.start = datetime.datetime.strptime(start, "%H:%M:%S")
        else:
            microsec = "0"
            if "." in start:
                start = start.split(".")[0]
                microsec = start.split(".")[1][0:6] if len(start.split(".")[1]) > 6 else start.split(".")[1]
            start = int(start)
            start = "{0:02d}:{1:02d}:{2:02d}.{3}".format((start % (60*60*24)) // 3600, (start % (60*60)) // 60, (start % 60), microsec)
            self.start = datetime.datetime.strptime(start, "%H:%M:%S.%f") - datetime.datetime(1900,1,1)
        #self.start = datetime.datetime.strptime(start, "%H:%M:%S") if start is not None else None
  	self.start_time = None
        if end is None:
            self.end = None
        if ":" in end:
            if "." in end:
                if len(end.split(".")[1]) > 6:
                    end = "{0}.{1}".format(end.split(".")[0], end.split(".")[1][0:6])
                self.end = datetime.datetime.strptime(end, "%H:%M:%S.%f")
            else:
                self.end = datetime.datetime.strptime(end, "%H:%M:%S")
        else:
            microsec = "0"
            if "." in end:
                end = end.split(".")[0]
                microsec = end.split(".")[1][0:6] if len(end.split(".")[1]) > 6 else end.split(".")[1]
            end = int(end)
            end = "{0:02d}:{1:02d}:{2:02d}.{3}".format((end % (60*60*24)) // 3600, (end % (60*60)) // 60, (end % 60), microsec)
            self.end = datetime.datetime.strptime(end, "%H:%M:%S.%f") - datetime.datetime(1900,1,1)
        #self.end = datetime.datetime.strptime(end, "%H:%M:%S") if end is not None else None
        self.end_time = None
        super(FilterJob, self).__init__()

    def check(self):
        if not os.path.exists(self.input_file):
            raise IOError("file does not exist: {}".format(self.input_file))
        if self.output_file == "":
            raise ValueError("output path is not specified")
        if self.start > self.end:
            raise ValueError("start time must be before end time")
        return

    def pre_process(self):
        """Convert start and end to start_time and end_time"""
        bag = rosbag.Bag(self.input_file)
        bag_start_time = datetime.datetime.fromtimestamp(bag.get_start_time())
        if self.start is not None:
            if type(self.start).__name__ == 'timedelta':
                self.start = bag_start_time + self.start
            start_datetime = datetime.datetime.combine(bag_start_time.date(), self.start.time())
            self.start_time = int(time.mktime(start_datetime.timetuple()))
        if self.end is not None:
            if type(self.end).__name__ == 'timedelta':
                self.end = bag_start_time + self.end
            end_datetime = datetime.datetime.combine(bag_start_time.date(), self.end.time())
            self.end_time = int(time.mktime(end_datetime.timetuple()))

    def run(self):
        self.check()
        self.pre_process()

        # expression
        if self.start is None:
            expression = "t.secs >= {}".format(self.start_time)
        elif self.end is None:
            expression = "t.secs <= {}".format(self.end_time)
        elif (self.start is None) and (self.end is None):
            raise ValueError("both start and end are not specified")
        else:
            expression = "{0} <= t.secs <= {1}".format(self.start_time, self.end_time)

        command = 'rosbag filter {0} {1} "{2}"'.format(self.input_file, self.output_file, expression)
        self.logger.debug("command: {}".format(command))
        if args.dry_run:
            return 0
        return subprocess.call(command, shell=True)


class JobHandler(object):
    def __init__(self):
        self.logger = logging.getLogger(name=type(self).__name__)
        self.queue = []
        super(JobHandler, self).__init__()

    def append_job(self, job):
        self.queue.append(job)

    def run(self):
        return_values = []
        for queue in self.queue:
            try:
                return_values.append(queue.run())
            except IOError as e:
                self.logger.error(str(e))
                self.logger.warn("skipped a job")
                return_values.append(1)
            except ValueError as e:
                self.logger.error(str(e))
                self.logger.warn("skipped a job")
                return_values.append(1)
        if any(return_values):
            self.logger.error("Could not process the following bag files correctly.")
            for index, return_value in enumerate(return_values):
                if return_value != 0:
                    self.logger.info("[{0}] input: {1} -> output: {2}".format(index,
                                                                              self.queue[index].input_file,
                                                                              self.queue[index].output_file))
            return 1
        return 0


def csv_reader(path_to_csv):
    with open(path_to_csv, "r") as f:
        reader = csv.reader(f)
        _ = next(reader)    # skip header

        # start reading lines
        original_file = ""
        for row in reader:
            if row[0] != "":
                original_file = row[0]
            splitted_file = row[1]
            if splitted_file == "":
                continue
            start = row[4] if row[4] != '' else None
            end = row[5] if row[5] != '' else None
            yield original_file, splitted_file, start, end

    raise EOFError()


def create_parser():
    parser = argparse.ArgumentParser(description="Split rosbag file based on csv file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug mode")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("-i", "--input-dir", type=str, default="./",
                        help="input directory to search rosbag (original) file")
    parser.add_argument("-o", "--output-dir", type=str, default="./",
                        help="output directory to save splitted rosbag files")
    parser.add_argument("csv_file", help="csv file")
    return parser


def main():
    if not os.path.exists(args.input_dir):
        raise IOError("directory {} does not exist".format(args.input_dir))

    if not os.path.exists(args.output_dir):
        raise IOError("directory {} does not exist".format(args.output_dir))

    reader = csv_reader(args.csv_file)
    job_handler = JobHandler()

    while True:
        try:
            input_file, output_file, start, end = next(reader)
            job = FilterJob(input_file, output_file, start, end, input_dir=args.input_dir, output_dir=args.output_dir)
            job_handler.append_job(job)
        except EOFError:
            break

    logging.info("{} jobs queued.".format(len(job_handler.queue)))
    logging.info("Processing...")
    if job_handler.run() == 1:
        sys.exit(1)
    logging.info("Done.")
    sys.exit(0)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    main()
