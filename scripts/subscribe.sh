#!/bin/bash

sudo subscription-manager register \
                     --username ${RHUSERNAME} \
                     --password ${RHPASSWORD}
sudo subscription-manager attach --pool ${RHPOOL}
sudo subscription-manager repos --disable=*

DIRECTOR_REPOS=(
    rhel-7-server-rpms
    rhel-7-server-extras-rpms
    rhel-7-server-rh-common-rpms
    rhel-ha-for-rhel-7-server-rpms
    rhel-7-server-openstack-14-rpms
)

REPO_ARG=""
for REPO in ${DIRECTOR_REPOS[@]} ; do
    REPO_ARG="${REPO_ARG} --enable=${REPO}"
done
sudo subscription-manager repos ${REPO_ARG}

sudo yum -y update
