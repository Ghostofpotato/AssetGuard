#! /bin/bash

set -ex

JOBS=$1
DEBUG=$2
ZIP_NAME=$3
TRUST_VERIFICATION=$4
CA_NAME=$5

# Compile the assetguard agent for Windows
FLAGS="-j ${JOBS} IMAGE_TRUST_CHECKS=${TRUST_VERIFICATION} CA_NAME=\"${CA_NAME}\" "

if [[ "${DEBUG}" = "yes" ]]; then
    FLAGS+="DEBUG=1 "
fi

if [ -z "${BRANCH}"]; then
    mkdir /assetguard-local-src
    cp -r /local-src/. /assetguard-local-src
else
    git clone --depth=1 https://github.com/assetguard/assetguard.git -b ${BRANCH}
fi

# Add commit hash information to VERSION.json
pushd /assetguard*
SHORT_COMMIT=$(git rev-parse --short=7 HEAD)
if [ -z "$SHORT_COMMIT" ]; then echo "No commit found"; exit 1; fi
echo "Found commit: $SHORT_COMMIT"
sed -i '/"stage":/s/$/,/; /"stage":/a \    "commit": "'"$SHORT_COMMIT"'"' VERSION.json || exit 1
cat VERSION.json
popd

bash -c "make -C /assetguard*/src deps TARGET=winagent ${FLAGS}"
bash -c "make -C /assetguard*/src TARGET=winagent ${FLAGS}"

rm -rf /assetguard*/src/external

zip -r /shared/${ZIP_NAME} /assetguard*
