#!/bin/bash

# Copyright (C) 2015, AssetGuard Inc.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

# Global variables
INSTALLDIR=${1}
CONF_FILE="${INSTALLDIR}/etc/ossec.conf"
TMP_ENROLLMENT="${INSTALLDIR}/tmp/enrollment-configuration"
TMP_SERVER="${INSTALLDIR}/tmp/server-configuration"
ASSETGUARD_REGISTRATION_PASSWORD_PATH="etc/authd.pass"
ASSETGUARD_MACOS_AGENT_DEPLOYMENT_VARS="/tmp/assetguard_envs"


# Set default sed alias
sed="sed -ri"

# Update the value of a XML tag inside the assetguard configuration file
edit_value_tag() {

    file=""

    if [ -z "$3" ]; then
        file="${CONF_FILE}"
    else
        file="${TMP_ENROLLMENT}"
    fi

    if [ -n "$1" ] && [ -n "$2" ]; then
        start_config="$(grep -n "<$1>" "${file}" | cut -d':' -f 1)"
        end_config="$(grep -n "</$1>" "${file}" | cut -d':' -f 1)"
        if [ -z "${start_config}" ] && [ -z "${end_config}" ] && [ "${file}" = "${TMP_ENROLLMENT}" ]; then
            echo "      <$1>$2</$1>" >> "${file}"
        else
            ${sed} "s#<$1>.*</$1>#<$1>$2</$1>#g" "${file}"
        fi
    fi

    if [ "$?" != "0" ]; then
        echo "$(date '+%Y/%m/%d %H:%M:%S') Error updating $2 with variable $1." >> "${INSTALLDIR}/logs/ossec.log"
    fi

}

delete_blank_lines() {

    file=$1
    ${sed} '/^$/d' "${file}"

}

delete_auto_enrollment_tag() {

    # Delete the configuration tag if its value is empty
    # This will allow using the default value
    ${sed} "s#.*<$1>.*</$1>.*##g" "${TMP_ENROLLMENT}"

    cat -s "${TMP_ENROLLMENT}" > "${TMP_ENROLLMENT}.tmp"
    mv "${TMP_ENROLLMENT}.tmp" "${TMP_ENROLLMENT}"

}

# Change address block of the assetguard configuration file
add_adress_block() {

    # Remove both manager and legacy server configuration blocks
    ${sed} "/<manager>/,/\/manager>/d; /<server>/,/\/server>/d" "${CONF_FILE}"

    # Write the client configuration block
    for i in "${!ADDRESSES[@]}";
    do
        {
            echo "    <manager>"
            echo "      <address>${ADDRESSES[i]}</address>"
            echo "      <port>1514</port>"
            echo "    </manager>"
        } >> "${TMP_SERVER}"
    done

    ${sed} "/<client>/r ${TMP_SERVER}" "${CONF_FILE}"

    rm -f "${TMP_SERVER}"

}

add_parameter () {

    if [ -n "$3" ]; then
        OPTIONS="$1 $2 $3"
    fi
    echo "${OPTIONS}"

}

get_deprecated_vars () {

    if [ -n "${ASSETGUARD_MANAGER_IP}" ] && [ -z "${ASSETGUARD_MANAGER}" ]; then
        ASSETGUARD_MANAGER=${ASSETGUARD_MANAGER_IP}
    fi
    if [ -n "${ASSETGUARD_AUTHD_SERVER}" ] && [ -z "${ASSETGUARD_REGISTRATION_SERVER}" ]; then
        ASSETGUARD_REGISTRATION_SERVER=${ASSETGUARD_AUTHD_SERVER}
    fi
    if [ -n "${ASSETGUARD_AUTHD_PORT}" ] && [ -z "${ASSETGUARD_REGISTRATION_PORT}" ]; then
        ASSETGUARD_REGISTRATION_PORT=${ASSETGUARD_AUTHD_PORT}
    fi
    if [ -n "${ASSETGUARD_PASSWORD}" ] && [ -z "${ASSETGUARD_REGISTRATION_PASSWORD}" ]; then
        ASSETGUARD_REGISTRATION_PASSWORD=${ASSETGUARD_PASSWORD}
    fi
    if [ -n "${ASSETGUARD_NOTIFY_TIME}" ] && [ -z "${ASSETGUARD_KEEP_ALIVE_INTERVAL}" ]; then
        ASSETGUARD_KEEP_ALIVE_INTERVAL=${ASSETGUARD_NOTIFY_TIME}
    fi
    if [ -n "${ASSETGUARD_CERTIFICATE}" ] && [ -z "${ASSETGUARD_REGISTRATION_CA}" ]; then
        ASSETGUARD_REGISTRATION_CA=${ASSETGUARD_CERTIFICATE}
    fi
    if [ -n "${ASSETGUARD_PEM}" ] && [ -z "${ASSETGUARD_REGISTRATION_CERTIFICATE}" ]; then
        ASSETGUARD_REGISTRATION_CERTIFICATE=${ASSETGUARD_PEM}
    fi
    if [ -n "${ASSETGUARD_KEY}" ] && [ -z "${ASSETGUARD_REGISTRATION_KEY}" ]; then
        ASSETGUARD_REGISTRATION_KEY=${ASSETGUARD_KEY}
    fi
    if [ -n "${ASSETGUARD_GROUP}" ] && [ -z "${ASSETGUARD_AGENT_GROUP}" ]; then
        ASSETGUARD_AGENT_GROUP=${ASSETGUARD_GROUP}
    fi

}

set_vars () {

    export ASSETGUARD_MANAGER
    export ASSETGUARD_MANAGER_PORT
    export ASSETGUARD_REGISTRATION_SERVER
    export ASSETGUARD_REGISTRATION_PORT
    export ASSETGUARD_REGISTRATION_PASSWORD
    export ASSETGUARD_KEEP_ALIVE_INTERVAL
    export ASSETGUARD_TIME_RECONNECT
    export ASSETGUARD_REGISTRATION_CA
    export ASSETGUARD_REGISTRATION_CERTIFICATE
    export ASSETGUARD_REGISTRATION_KEY
    export ASSETGUARD_AGENT_NAME
    export ASSETGUARD_AGENT_GROUP
    export ENROLLMENT_DELAY
    # The following variables are yet supported but all of them are deprecated
    export ASSETGUARD_MANAGER_IP
    export ASSETGUARD_NOTIFY_TIME
    export ASSETGUARD_AUTHD_SERVER
    export ASSETGUARD_AUTHD_PORT
    export ASSETGUARD_PASSWORD
    export ASSETGUARD_GROUP
    export ASSETGUARD_CERTIFICATE
    export ASSETGUARD_KEY
    export ASSETGUARD_PEM

    if [ -r "${ASSETGUARD_MACOS_AGENT_DEPLOYMENT_VARS}" ]; then
        . ${ASSETGUARD_MACOS_AGENT_DEPLOYMENT_VARS}
        rm -rf "${ASSETGUARD_MACOS_AGENT_DEPLOYMENT_VARS}"
    fi

}

unset_vars() {

    vars=(ASSETGUARD_MANAGER_IP ASSETGUARD_MANAGER_PORT ASSETGUARD_NOTIFY_TIME \
          ASSETGUARD_TIME_RECONNECT ASSETGUARD_AUTHD_SERVER ASSETGUARD_AUTHD_PORT ASSETGUARD_PASSWORD \
          ASSETGUARD_AGENT_NAME ASSETGUARD_GROUP ASSETGUARD_CERTIFICATE ASSETGUARD_KEY ASSETGUARD_PEM \
          ASSETGUARD_MANAGER ASSETGUARD_REGISTRATION_SERVER ASSETGUARD_REGISTRATION_PORT \
          ASSETGUARD_REGISTRATION_PASSWORD ASSETGUARD_KEEP_ALIVE_INTERVAL ASSETGUARD_REGISTRATION_CA \
          ASSETGUARD_REGISTRATION_CERTIFICATE ASSETGUARD_REGISTRATION_KEY ASSETGUARD_AGENT_GROUP \
          ENROLLMENT_DELAY)

    for var in "${vars[@]}"; do
        unset "${var}"
    done

}

# Function to convert strings to lower version
tolower () {

    echo "$1" | tr '[:upper:]' '[:lower:]'

}


# Add auto-enrollment configuration block
add_auto_enrollment () {

    start_config="$(grep -n "<enrollment>" "${CONF_FILE}" | cut -d':' -f 1)"
    end_config="$(grep -n "</enrollment>" "${CONF_FILE}" | cut -d':' -f 1)"
    if [ -n "${start_config}" ] && [ -n "${end_config}" ]; then
        start_config=$(( start_config + 1 ))
        end_config=$(( end_config - 1 ))
        sed -n "${start_config},${end_config}p" "${INSTALLDIR}/etc/ossec.conf" >> "${TMP_ENROLLMENT}"
    else
        # Write the client configuration block
        {
            echo "    <enrollment>"
            echo "      <enabled>yes</enabled>"
            echo "      <manager_address>MANAGER_IP</manager_address>"
            echo "      <port>1515</port>"
            echo "      <agent_name>agent</agent_name>"
            echo "      <groups>Group1</groups>"
            echo "      <server_ca_path>/path/to/server_ca</server_ca_path>"
            echo "      <agent_certificate_path>/path/to/agent.cert</agent_certificate_path>"
            echo "      <agent_key_path>/path/to/agent.key</agent_key_path>"
            echo "      <authorization_pass_path>/path/to/authd.pass</authorization_pass_path>"
            echo "      <delay_after_enrollment>20</delay_after_enrollment>"
            echo "    </enrollment>"
        } >> "${TMP_ENROLLMENT}"
    fi

}

# Add the auto_enrollment block to the configuration file
concat_conf() {

    ${sed} "/<\/auto_restart>/r ${TMP_ENROLLMENT}" "${CONF_FILE}"

    rm -f "${TMP_ENROLLMENT}"

}

# Set autoenrollment configuration
set_auto_enrollment_tag_value () {

    tag="$1"
    value="$2"

    if [ -n "${value}" ]; then
        edit_value_tag "${tag}" "${value}" "auto_enrollment"
    else
        delete_auto_enrollment_tag "${tag}" "auto_enrollment"
    fi

}

# Main function the script begin here
main () {

    uname_s=$(uname -s)

    # Check what kind of system we are working with
    if [ "${uname_s}" = "Darwin" ]; then
        sed="sed -ire"
        set_vars
    fi

    get_deprecated_vars

    if [ -n "${ASSETGUARD_MANAGER}" ]; then
        if [ ! -f "${INSTALLDIR}/logs/ossec.log" ]; then
            touch -f "${INSTALLDIR}/logs/ossec.log"
            chmod 660 "${INSTALLDIR}/logs/ossec.log"
            chown root:assetguard "${INSTALLDIR}/logs/ossec.log"
        fi

        # Check if multiples IPs are defined in variable ASSETGUARD_MANAGER
        ADDRESSES=( ${ASSETGUARD_MANAGER//,/ } )

        add_adress_block
    fi

    edit_value_tag "port" "${ASSETGUARD_MANAGER_PORT}"

    if [ -n "${ASSETGUARD_REGISTRATION_SERVER}" ] || [ -n "${ASSETGUARD_REGISTRATION_PORT}" ] || [ -n "${ASSETGUARD_REGISTRATION_CA}" ] || [ -n "${ASSETGUARD_REGISTRATION_CERTIFICATE}" ] || [ -n "${ASSETGUARD_REGISTRATION_KEY}" ] || [ -n "${ASSETGUARD_AGENT_NAME}" ] || [ -n "${ASSETGUARD_AGENT_GROUP}" ] || [ -n "${ENROLLMENT_DELAY}" ] || [ -n "${ASSETGUARD_REGISTRATION_PASSWORD}" ]; then
        add_auto_enrollment
        set_auto_enrollment_tag_value "manager_address" "${ASSETGUARD_REGISTRATION_SERVER}"
        set_auto_enrollment_tag_value "port" "${ASSETGUARD_REGISTRATION_PORT}"
        set_auto_enrollment_tag_value "server_ca_path" "${ASSETGUARD_REGISTRATION_CA}"
        set_auto_enrollment_tag_value "agent_certificate_path" "${ASSETGUARD_REGISTRATION_CERTIFICATE}"
        set_auto_enrollment_tag_value "agent_key_path" "${ASSETGUARD_REGISTRATION_KEY}"
        set_auto_enrollment_tag_value "authorization_pass_path" "${ASSETGUARD_REGISTRATION_PASSWORD_PATH}"
        set_auto_enrollment_tag_value "agent_name" "${ASSETGUARD_AGENT_NAME}"
        set_auto_enrollment_tag_value "groups" "${ASSETGUARD_AGENT_GROUP}"
        set_auto_enrollment_tag_value "delay_after_enrollment" "${ENROLLMENT_DELAY}"
        delete_blank_lines "${TMP_ENROLLMENT}"
        concat_conf
    fi


    if [ -n "${ASSETGUARD_REGISTRATION_PASSWORD}" ]; then
        echo "${ASSETGUARD_REGISTRATION_PASSWORD}" > "${INSTALLDIR}/${ASSETGUARD_REGISTRATION_PASSWORD_PATH}"
        chmod 640 "${INSTALLDIR}"/"${ASSETGUARD_REGISTRATION_PASSWORD_PATH}"
        chown root:assetguard "${INSTALLDIR}"/"${ASSETGUARD_REGISTRATION_PASSWORD_PATH}"
    fi

    # Options to be modified in assetguard configuration file
    edit_value_tag "notify_time" "${ASSETGUARD_KEEP_ALIVE_INTERVAL}"
    edit_value_tag "time-reconnect" "${ASSETGUARD_TIME_RECONNECT}"

    unset_vars

}

# Start script execution
main "$@"
