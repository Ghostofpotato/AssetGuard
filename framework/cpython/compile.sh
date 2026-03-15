#!/bin/bash
# Copyright (C) 2015, AssetGuard Inc.
#
# This program is a free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

set -euo pipefail

ASSETGUARD_HOST_DIR=/assetguard_host
ASSETGUARD_ROOT_DIR=/assetguard #Important: Do not change this path
ASSETGUARD_INSTALLDIR=/var/assetguard-manager
CPYTHON_DIR=$ASSETGUARD_ROOT_DIR/src/external/cpython
OUTPUT_DIR=/output

main() {
    # Parse script arguments
    parse_args "$@" || exit 1
    # Get assetguard repository
    get_assetguard_repo
    # Download assetguard precompiled dependencies
    make -C "$ASSETGUARD_ROOT_DIR/src" PYTHON_SOURCE=y deps -j

    PYTHON_VERSION=$(cat $ASSETGUARD_ROOT_DIR/framework/.python-version)

    if $BUILD_CPYTHON; then
        # Build CPython from sources
        rm -rf "$CPYTHON_DIR"
        download_cpython
        customize_cpython
        build_cpython
    fi

    if $BUILD_DEPS || $BUILD_CPYTHON; then
        download_wheels
    fi

    mimic_full_assetguard_installation
    generate_artifacts
}

get_assetguard_repo() {
    if [ -z "${ASSETGUARD_BRANCH:-}" ]; then
        cp -rf $ASSETGUARD_HOST_DIR $ASSETGUARD_ROOT_DIR
        # Clean previous builds
        rm -rf $ASSETGUARD_ROOT_DIR/src/external/*
        make clean -j -C "$ASSETGUARD_ROOT_DIR/src"
    else
        git clone --branch "$ASSETGUARD_BRANCH" --depth 1 https://github.com/assetguard/assetguard.git  "$ASSETGUARD_ROOT_DIR"
    fi
}

download_cpython() {
    git clone --branch "v$PYTHON_VERSION" --depth 1 https://github.com/python/cpython.git "$CPYTHON_DIR"
}

customize_cpython() {
    cp -f $ASSETGUARD_ROOT_DIR/framework/cpython/custom/Setup.local $CPYTHON_DIR/Modules
    cp -f $ASSETGUARD_ROOT_DIR/framework/cpython/custom/Setup.stdlib.in $CPYTHON_DIR/Modules
}

build_cpython() {
    make -j -C "$ASSETGUARD_ROOT_DIR/src" build_python INSTALLDIR=$ASSETGUARD_INSTALLDIR OPTIMIZE_CPYTHON=yes
}

mimic_full_assetguard_installation() {
    # Force build of libassetguardext
    make -j -C "$ASSETGUARD_ROOT_DIR/src" external INSTALLDIR=$ASSETGUARD_INSTALLDIR
    # Install only libassetguardext to avoid full server compilation & installation
    mkdir -p "$ASSETGUARD_INSTALLDIR/lib"
    install -m 0750 $ASSETGUARD_ROOT_DIR/src/build/lib/libassetguardext.so "$ASSETGUARD_INSTALLDIR/lib"
    # Install python interpreter and its dependencies
    make -j -C "$ASSETGUARD_ROOT_DIR/src" install_dependencies INSTALLDIR=$ASSETGUARD_INSTALLDIR
}

generate_artifacts() {
    # Compress built cpython
    cd $ASSETGUARD_ROOT_DIR/src/external && tar -zcf "$OUTPUT_DIR/cpython_$ARCH.tar.gz" --owner=0 --group=0 cpython
    # Compress ready-to-use CPython
    cd $ASSETGUARD_INSTALLDIR/framework/python && tar -zcf "$OUTPUT_DIR/cpython.tar.gz" --owner=0 --group=0 .
}

download_wheels() {
    # Install Python3 to download wheels
    yum install python3 -y
    python3 -m pip install --upgrade pip
    # Remove existing dependencies
    rm -rf "$CPYTHON_DIR/Dependencies"
    # Create dependencies directory
    mkdir -p "$CPYTHON_DIR/Dependencies"
    # Download wheels
    python3 -m pip download --requirement "$ASSETGUARD_ROOT_DIR/framework/requirements.txt"  --no-deps --dest "$CPYTHON_DIR/Dependencies"  --python-version "$PYTHON_VERSION" --no-cache-dir
    # Create index
    python3 -m pip install piprepo && piprepo build "$CPYTHON_DIR/Dependencies"
}

parse_args() {
    BUILD_CPYTHON=false
    BUILD_DEPS=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --build-cpython)
                BUILD_CPYTHON=true
                ;;
            --build-deps)
                BUILD_DEPS=true
                ;;
            --assetguard-branch)
                ASSETGUARD_BRANCH="$2"
                ;;
            *)
                echo "ERROR: Unrecognized parameter: $1" >&2
                return 1
                ;;
        esac
        shift
    done
}

main "$@"
