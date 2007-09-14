#!/bin/sh
genextdoc=`which genextdoc.py 2>/dev/null`
if test "x$genextdoc" = x; then
    cat <<EOF
Need genextdoc.py to generate the documentation.
Fetch it at http://trific.ath.cx/Ftp/python/genextdoc.py
EOF
else
    genextdoc.py Levenshtein NEWS
fi
