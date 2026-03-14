#! /bin/bash
# By Spransy, Derek" <DSPRANS () emory ! edu> and Charlie Scott
# Modified by AssetGuard, Inc. <info@assetguard.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

#####
# This checks for an error and exits with a custom message
# Returns zero on success
# $1 is the message
# $2 is the error code

DIR="/Library/Ossec"
ARCH="PACKAGE_ARCH"

function check_errm
{
    if  [[ ${?} != "0" ]]
        then
        echo "${1}";
        exit ${2};
        fi
}

function check_arch
{
    local system_arch=$(uname -m)

    if [ "$ARCH" = "intel64" ] && [ "$system_arch" = "arm64" ]; then
        if ! arch -x86_64 zsh -c '' &> /dev/null; then
            >&2 echo "ERROR: Rosetta is not installed. Please install it and try again."
            exit 1
        fi
    elif [ "$ARCH" = "arm64" ] && [ "$system_arch" = "x86_64" ]; then
        >&2 echo "ERROR: Incompatible architecture. Please use the Intel package on this system."
        exit 1
    fi
}

check_arch

if [ -d "${DIR}" ]; then
    echo "A AssetGuard agent installation was found in ${DIR}. Will perform an upgrade."
    upgrade="true"
    touch "${DIR}/ASSETGUARD_PKG_UPGRADE"

    if [ -f "${DIR}/ASSETGUARD_RESTART" ]; then
        rm -f "${DIR}/ASSETGUARD_RESTART"
    fi

    # Get version information
    if [ -f "${DIR}/bin/assetguard-control" ]; then
        OLD_VERSION=`${DIR}/bin/assetguard-control info -v 2>/dev/null`
        MAJOR=$(echo $OLD_VERSION | cut -dv -f2 | cut -d. -f1)
        MINOR=$(echo $OLD_VERSION | cut -dv -f2 | cut -d. -f2)
    elif [ -f ${DIR}/VERSION.json ]; then
        OLD_VERSION=$(awk -F'"' '/"version"[[:space:]]*:/ {print $4; exit}' "${DIR}/VERSION.json" 2>/dev/null)
        MAJOR=$(echo $OLD_VERSION | cut -d. -f1)
        MINOR=$(echo $OLD_VERSION | cut -d. -f2)
    fi

    # Validate upgrade constraints for Agent
    ERROR_TYPE=""

    # Determine if upgrade should be blocked
    if [ -z "$MAJOR" ] || [ -z "$MINOR" ]; then
        ERROR_TYPE="no_version"
        ERROR_TITLE="Cannot detect current version"
        ERROR_MESSAGE="Unable to detect the currently installed AssetGuard version."
    elif [ "$MAJOR" -lt 4 ] || ([ "$MAJOR" -eq 4 ] && [ "$MINOR" -lt 14 ]); then
        ERROR_TYPE="unsupported"
        ERROR_TITLE="Incompatible version detected"
        ERROR_MESSAGE="Current version: $OLD_VERSION
Target version:  5.0.0

Upgrade to AssetGuard 5.0.0 is only supported from version 4.14.0 or later."
    fi

    # If any error was detected, show message and block
    if [ -n "$ERROR_TYPE" ]; then
        echo "═════════════════════════════════════════════════════════════════"
        echo "  UPGRADE BLOCKED: $ERROR_TITLE"
        echo "═════════════════════════════════════════════════════════════════"
        echo ""
        echo "$ERROR_MESSAGE"
        echo ""
        echo "Required action:"
        echo "  1. Upgrade to version 4.14.0 or later first"
        echo "  2. Then upgrade to 5.0.0"
        echo ""
        echo "For more information, visit:"
        echo "  https://documentation.assetguard.com/current/upgrade-guide/"
        echo "═════════════════════════════════════════════════════════════════"
        echo -n "1" > ${DIR}/var/upgrade/upgrade_result
        exit 1
    fi

    # Stops the agent before upgrading it
    if ${DIR}/bin/assetguard-control status | grep "is running" > /dev/null 2>&1; then
        touch "${DIR}/ASSETGUARD_RESTART"
        ${DIR}/bin/assetguard-control stop
        restart="true"
    elif ${DIR}/bin/ossec-control status | grep "is running" > /dev/null 2>&1; then
        touch "${DIR}/ASSETGUARD_RESTART"
        ${DIR}/bin/ossec-control stop
        restart="true"
    fi

    # Remove old databases if upgrading from pre 5.X to 5.X
    if [ $MAJOR -lt 5 ]; then
        if [ -f ${DIR}/queue/syscollector/db/local.db ]; then
          rm -f ${DIR}/queue/syscollector/db/local.db
        fi
        if [ -f ${DIR}/queue/fim/db/fim.db ]; then
          rm -f ${DIR}/queue/fim/db/fim.db
        fi
    fi

    echo "Backing up configuration files to ${DIR}/config_files/"
    mkdir -p ${DIR}/config_files/
    cp -r ${DIR}/etc/{ossec.conf,client.keys,local_internal_options.conf,shared} ${DIR}/config_files/

    if [ -d ${DIR}/logs/ossec ]; then
        echo "Renaming ${DIR}/logs/ossec to ${DIR}/logs/assetguard"
        mv ${DIR}/logs/ossec ${DIR}/logs/assetguard
    fi

    if [ -d ${DIR}/queue/ossec ]; then
        echo "Renaming ${DIR}/queue/ossec to ${DIR}/queue/sockets"
        mv ${DIR}/queue/ossec ${DIR}/queue/sockets
    fi

    if pkgutil --pkgs | grep -i assetguard-agent-etc > /dev/null 2>&1 ; then
        echo "Removing previous package receipt for assetguard-agent-etc"
        pkgutil --forget com.assetguard.pkg.assetguard-agent-etc
    fi
fi

DSCL="/usr/bin/dscl";
if [[ ! -f "$DSCL" ]]
    then
    echo "Error: I couldn't find dscl, dying here";
    exit
fi


# get unique id numbers (uid, gid) that are greater than 100
echo "Getting unique id numbers (uid, gid)"
unset -v i new_uid new_gid idvar;
declare -i new_uid=0 new_gid=0 i=100 idvar=0;
while [[ $idvar -eq 0 ]]; do
    i=$[i+1]
    if [[ -z "$(${DSCL} . -search /Users uid ${i})" ]] && [[ -z "$(${DSCL} . -search /Groups gid ${i})" ]];
        then
        echo "Found available UID and GID: $i"
        new_uid=$i
        new_gid=$i
        idvar=1
   fi
done

echo "UID available for assetguard user is:";
echo ${new_uid}

# Verify that the uid and gid exist and match
if [[ $new_uid -eq 0 ]] || [[ $new_gid -eq 0 ]];
    then
    echo "Getting unique id numbers (uid, gid) failed!";
    exit 1;
fi
if [[ ${new_uid} != ${new_gid} ]]
    then
    echo "I failed to find matching free uid and gid!";
    exit 5;
fi

# Creating the group
echo "Checking group..."
if [[ $(dscl . -read /Groups/assetguard) ]]
    then
    echo "assetguard group already exists.";
else
    sudo ${DSCL} localhost -create /Local/Default/Groups/assetguard
    check_errm "Error creating group assetguard" "67"
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/assetguard PrimaryGroupID ${new_gid}
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/assetguard RealName assetguard
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/assetguard RecordName assetguard
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/assetguard RecordType: dsRecTypeStandard:Groups
    sudo ${DSCL} localhost -createprop /Local/Default/Groups/assetguard Password "*"
fi

# Creating the user
echo "Checking user..."
if [[ $(dscl . -read /Users/assetguard) ]]
    then
    echo "assetguard user already exists.";
else
    sudo ${DSCL} localhost -create /Local/Default/Users/assetguard
    check_errm "Error creating user assetguard" "77"
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard RecordName assetguard
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard RealName assetguard
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard UserShell /usr/bin/false
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard NFSHomeDirectory /var/assetguard
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard UniqueID ${new_uid}
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard PrimaryGroupID ${new_gid}
    sudo ${DSCL} localhost -append /Local/Default/Groups/assetguard GroupMembership assetguard
    sudo ${DSCL} localhost -createprop /Local/Default/Users/assetguard Password "*"
fi

#Hide the fixed users
echo "Hiding the fixed assetguard user"
dscl . create /Users/assetguard IsHidden 1
