FROM ubuntu:18.04

RUN apt-get update && apt-get install -y curl apt-transport-https lsb-release gnupg2
RUN curl -s https://packages.assetguard.com/key/GPG-KEY-ASSETGUARD | apt-key add - && \
    echo "deb https://packages.assetguard.com/4.x/apt/ stable main" | tee /etc/apt/sources.list.d/assetguard.list && \
    apt-get update && apt-get install assetguard-agent=4.14.1-1 -y
