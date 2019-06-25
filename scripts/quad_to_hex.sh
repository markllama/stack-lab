#!/bin/sh
#
# Convert an input dotted quad into hex format for PXELINUX
#
function quad_to_hex() {
    local DQUAD=$1

    # Split on dots
    IFS='.' read -r -a PARTS <<< ${DQUAD}

    local HEXADDR=""
    for OCTET in "${PARTS[@]}" ; do
        HEXADDR="${HEXADDR}"$(echo -n $(printf "%02x" ${OCTET}))
    done 
    echo ${HEXADDR^^}
}

quad_to_hex $1

