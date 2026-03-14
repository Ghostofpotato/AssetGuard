#!/bin/sh

## Stop and remove application
sudo /Library/Ossec/bin/assetguard-control stop
sudo /bin/rm -r /Library/Ossec*

# remove launchdaemons
/bin/rm -f /Library/LaunchDaemons/com.assetguard.agent.plist

## remove StartupItems
/bin/rm -rf /Library/StartupItems/ASSETGUARD

## Remove User and Groups
/usr/bin/dscl . -delete "/Users/assetguard"
/usr/bin/dscl . -delete "/Groups/assetguard"

/usr/sbin/pkgutil --forget com.assetguard.pkg.assetguard-agent
/usr/sbin/pkgutil --forget com.assetguard.pkg.assetguard-agent-etc

# In case it was installed via Puppet pkgdmg provider

if [ -e /var/db/.puppet_pkgdmg_installed_assetguard-agent ]; then
    rm -f /var/db/.puppet_pkgdmg_installed_assetguard-agent
fi

echo
echo "AssetGuard agent correctly removed from the system."
echo

exit 0
