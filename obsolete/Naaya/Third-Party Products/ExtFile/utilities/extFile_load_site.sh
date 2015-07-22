#!/bin/sh
#
# Created January 19, 2004
# Bjorn Nelson o_sleep@babbleheaven.com
#

# Editable variables
CURL="/usr/local/bin/curl"
DIRNAME="/usr/bin/dirname"
BASENAME="/usr/bin/basename"
ZOPEHOST="scutils.babbleheaven.com"
USERNAME="admin"
PASSWORD="password"
#

if  [ ! $1 ] || [ ! $2 ] || [ $1 = "-h" ] || [ $1 = "--help" ]; then
	echo "Usage: `$BASENAME $0` [-dfi] file"
	echo "  -h --help	this help"
	echo "  -d --dir	upload a directory"
	echo "  -f --file	upload a file"
	echo "  -i --image	upload an image"
	echo "  file		file to be uploaded"
	echo
	exit 1
fi
FILENAME="$2"
if [ ! -e $FILENAME ]; then
	echo "$FILENAME: file/directory not found"
	echo
	exit 1
fi


DIR=`$DIRNAME $2`
SUBDIR=`$DIRNAME $DIR`
BASE=`$BASENAME $2`

case $1 in
	-d | --dir )
		if [ ! -d $FILENAME ]; then
			echo "$FILENAME: not a directory"
			echo
			exit 1
		fi
		`$CURL -u $USERNAME:$PASSWORD -F "id=$BASE" -F "title=$BASE" http://$ZOPEHOST/Zope/$DIR/manage_addProduct/OFSP/manage_addFolder >> $0.err`
	;;
	
	-f | --file )
		if [ ! -f $FILENAME ]; then
			echo "$FILENAME: not a regular file"
			echo
			exit 1
		fi
		`$CURL -u $USERNAME:$PASSWORD -F "id=$BASE" -F "title=$BASE" -F "desc=batch-upload" -F "file=@$FILENAME" -F "permission_check:int=0" http://$ZOPEHOST/Zope/$DIR/manage_addProduct/ExtFile/manage_addExtFile >> $0.err`
	;;

	-i | --image )
		if [ ! -f $FILENAME ]; then
			echo "$FILENAME: not a regular file"
			echo
			exit 1
		fi
		`$CURL -u $USERNAME:$PASSWORD -F "id=$BASE" -F "title=$BASE" -F "desc=batch-upload" -F "file=@$FILENAME" -F "create_prev:int=1" -F "maxx=256" -F "maxy=256" -F "ratio:int=1" -F "permission_check:int=0" http://$ZOPEHOST/Zope/$DIR/manage_addProduct/ExtFile/manage_addExtImage >> $0.err`
	;;

	* )
		echo "specify a valid upload type (-d, -f, or -i)"
		echo
		exit 1
	;;
esac
echo "check $0.err for any zope errors"
