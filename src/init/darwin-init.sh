#!/bin/sh

# Darwin init script.
# by Lorenzo Costanzia di Costigliole <mummie@tin.it>
# Modified by AssetGuard, Inc. <info@assetguard.com>.
# Copyright (C) 2015, AssetGuard Inc.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

INSTALLATION_PATH=${1}
SERVICE=/Library/LaunchDaemons/com.assetguard.agent.plist
STARTUP=/Library/StartupItems/ASSETGUARD/StartupParameters.plist
LAUNCHER_SCRIPT=/Library/StartupItems/ASSETGUARD/AssetGuard-launcher
STARTUP_SCRIPT=/Library/StartupItems/ASSETGUARD/ASSETGUARD

launchctl unload /Library/LaunchDaemons/com.assetguard.agent.plist 2> /dev/null
mkdir -p /Library/StartupItems/ASSETGUARD
chown root:wheel /Library/StartupItems/ASSETGUARD
rm -f $STARTUP $STARTUP_SCRIPT $SERVICE
echo > $LAUNCHER_SCRIPT
chown root:wheel $LAUNCHER_SCRIPT
chmod u=rxw-,g=rx-,o=r-- $LAUNCHER_SCRIPT

echo '<?xml version="1.0" encoding="UTF-8"?>
 <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
 <plist version="1.0">
     <dict>
         <key>Label</key>
         <string>com.assetguard.agent</string>
         <key>ProgramArguments</key>
         <array>
             <string>'$LAUNCHER_SCRIPT'</string>
         </array>
         <key>RunAtLoad</key>
         <true/>
     </dict>
 </plist>' > $SERVICE

chown root:wheel $SERVICE
chmod u=rw-,go=r-- $SERVICE

echo '
#!/bin/sh
. /etc/rc.common

StartService ()
{
        '${INSTALLATION_PATH}'/bin/assetguard-control start
}
StopService ()
{
        '${INSTALLATION_PATH}'/bin/assetguard-control stop
}
RestartService ()
{
        '${INSTALLATION_PATH}'/bin/assetguard-control restart
}
RunService "$1"
' > $STARTUP_SCRIPT

chown root:wheel $STARTUP_SCRIPT
chmod u=rwx,go=r-x $STARTUP_SCRIPT

echo '
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://
www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
       <key>Description</key>
       <string>ASSETGUARD Security agent</string>
       <key>Messages</key>
       <dict>
               <key>start</key>
               <string>Starting AssetGuard agent</string>
               <key>stop</key>
               <string>Stopping AssetGuard agent</string>
       </dict>
       <key>Provides</key>
       <array>
               <string>ASSETGUARD</string>
       </array>
       <key>Requires</key>
       <array>
               <string>IPFilter</string>
       </array>
</dict>
</plist>
' > $STARTUP

chown root:wheel $STARTUP
chmod u=rw-,go=r-- $STARTUP

echo '#!/bin/sh

capture_sigterm() {
    '${INSTALLATION_PATH}'/bin/assetguard-control stop
    exit $?
}

if ! '${INSTALLATION_PATH}'/bin/assetguard-control start; then
    '${INSTALLATION_PATH}'/bin/assetguard-control stop
fi

while : ; do
    trap capture_sigterm SIGTERM
    sleep 3
done
' > $LAUNCHER_SCRIPT
