#!/usr/bin/env bash

# resolve path
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
REPOSITORY=${DIR}

# make ~/.local/bin if not exist
if [ ! -d ~/.local/bin/run_rqt_bag ]; then
  echo "Creating directory ~/.local/bin/run_rqt_bag"
  mkdir -p ~/.local/bin/run_rqt_bag
fi

# copy repository into the directory
echo "Copying files..."
cp -f ${REPOSITORY}/run_rqt_bag.* ~/.local/bin/run_rqt_bag/

# create symbolic link
echo "Creating symbolic link..."
ln -s -f ~/.local/bin/run_rqt_bag/run_rqt_bag.desktop ~/.local/share/applications/run_rqt_bag.desktop

echo "Done."
