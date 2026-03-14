#!/bin/bash

# AssetGuard package builder
# Copyright (C) 2015, AssetGuard Inc.
#
# This program is a free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.
set -e

build_directories() {
  local build_folder=$1
  local assetguard_dir="$2"
  local future="$3"

  mkdir -p "${build_folder}"
  assetguard_version=$(awk -F'"' '/"version"[ \t]*:/ {print $4}' assetguard*/VERSION.json)

  if [[ "$future" == "yes" ]]; then
    assetguard_version="$(future_version "$build_folder" "$assetguard_dir" $assetguard_version)"
    source_dir="${build_folder}/assetguard-${BUILD_TARGET}-${assetguard_version}"
  else
    package_name="assetguard-${BUILD_TARGET}-${assetguard_version}"
    source_dir="${build_folder}/${package_name}"
    cp -R $assetguard_dir "$source_dir"
  fi
  echo "$source_dir"
}

# Function to handle future version
future_version() {
  local build_folder="$1"
  local assetguard_dir="$2"
  local base_version="$3"

  specs_path="$(find $assetguard_dir/packages -name SPECS|grep $SYSTEM)"

  local major=$(echo "$base_version" | cut -dv -f2 | cut -d. -f1)
  local minor=$(echo "$base_version" | cut -d. -f2)
  local version="${major}.30.0"
  local old_name="assetguard-${BUILD_TARGET}-${base_version}"
  local new_name=assetguard-${BUILD_TARGET}-${version}

  local new_assetguard_dir="${build_folder}/${new_name}"
  cp -R ${assetguard_dir} "$new_assetguard_dir"
  find "$new_assetguard_dir" "${specs_path}" \( -name "*VERSION*" -o -name "*changelog*" \
        -o -name "*.spec" \) -exec sed -i "s/${base_version}/${version}/g" {} \;
  sed -i "s/\$(VERSION)/${major}.${minor}/g" "$new_assetguard_dir/src/Makefile"
  sed -i "s/${base_version}/${version}/g" $new_assetguard_dir/src/init/assetguard-{server,client,local}.sh
  echo "$version"
}

# Function to generate checksum and move files
post_process() {
  local file_path="$1"
  local checksum_flag="$2"
  local source_flag="$3"

  if [[ "$checksum_flag" == "yes" ]]; then
    sha512sum "$file_path" > /var/local/checksum/$(basename "$file_path").sha512
  fi

  if [[ "$source_flag" == "yes" ]]; then
    mv "$file_path" /var/local/assetguard
  fi
}

# Main script body

# Script parameters
export REVISION="$1"
export JOBS="$2"
debug="$3"
checksum="$4"
future="$5"
src="$6"

build_dir="/build_assetguard"

source helper_function.sh

if [ -n "${ASSETGUARD_VERBOSE}" ]; then
  set -x
fi

# Download source code if it is not shared from the local host
if [ ! -d "/assetguard-local-src" ] ; then
    curl -sL https://github.com/assetguard/assetguard/tarball/${ASSETGUARD_BRANCH} | tar zx
    short_commit_hash="$(curl -s https://api.github.com/repos/assetguard/assetguard/commits/${ASSETGUARD_BRANCH} \
                          | grep '"sha"' | head -n 1| cut -d '"' -f 4 | cut -c 1-7)"
else
      short_commit_hash="$(cd /assetguard-local-src && git rev-parse --short=7 HEAD)"
fi

# Build directories
source_dir=$(build_directories "$build_dir/${BUILD_TARGET}" "assetguard*" $future)

assetguard_version=$(awk -F'"' '/"version"[ \t]*:/ {print $4}' $source_dir/VERSION.json)
# TODO: Improve how we handle package_name
# Changing the "-" to "_" between target and version breaks the convention for RPM or DEB packages.
# For now, I added extra code that fixes it.
package_name="assetguard-${BUILD_TARGET}-${assetguard_version}"
specs_path="$(find $source_dir/packages -name SPECS|grep $SYSTEM)"

setup_build "$source_dir" "$specs_path" "$build_dir" "$package_name" "$debug"

set_debug $debug $source_dir

# Installing build dependencies
cd $source_dir
build_deps
build_package $package_name $debug "$short_commit_hash" "$assetguard_version"

# Post-processing
get_package_and_checksum $assetguard_version $short_commit_hash $src
