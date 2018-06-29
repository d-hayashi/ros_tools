# rosbag_remove_omron

Split rosbag file according to what's written in the specified csv file

## How to use
```bash
$ cd rosbag_split
$ python rosbag_split.py -i <input dir> -o <output dir> <csv file>
```
- <input dir>: path of the directory where rosbag files
- <output dir>: path of the directory where splitted rosbag files will be saved
- <csv file>: path of the csv file which is written in the format of what's used in "create_rosbag_list"
