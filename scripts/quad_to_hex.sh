#!/bin/sh
#
# Convert an input dotted quad into hex format for PXELINUX
#
DQUAD=$1

# Split on dots
OIFS=$IFS
IFS='.' read -r -a PARTS <<< ${DQUAD}

HEXADDR=""
for OCTET in "${PARTS[@]}" ; do
    HEXADDR="${HEXADDR}"$(echo -n $(printf "%02x" ${OCTET}))
done 
echo ${HEXADDR^^}


