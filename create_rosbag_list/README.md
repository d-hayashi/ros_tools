# creaete_rosbag_list

Create csv file that lists rosbag files in specified directory.
The output csv contains the following information.
- filename of original file (if exist)
- filename of splitted file
- start frame
- end frame
- start time (HH:MM:SS)
- end time (HH:MM:SS)
- file size

## How to use
```bash
$ cd creaete_rosbag_list

# case 1
$ ./create_rosbag_list.sh <directory> > ./list.csv
# This will output information about all the rosbag files inside <directory>

# case 2
$ ./create_rosbag_list.sh <original directory> <splitted directory>
# This will output information about all the rosbag files inside <splitted directory>
# and also the filename of the original rosbag files which correspond to the splitted one
```
