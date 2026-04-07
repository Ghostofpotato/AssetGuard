%if %{_isstage} == no
  %define _rpmfilename %%{NAME}_%%{VERSION}-%%{RELEASE}_%%{ARCH}_%{_hashcommit}.rpm
%else
  %define _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm
%endif

Summary:     AssetGuard helps you to gain security visibility into your infrastructure by monitoring hosts at an operating system and application level. It provides the following capabilities: log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring
Name:        assetguard-manager
Version:     %{_version}
Release:     %{_release}
License:     GPL
Group:       System Environment/Daemons
Source0:     %{name}-%{version}.tar.gz
URL:         https://www.assetguard.com/
BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor:      AssetGuard <info@assetguard.com>
Packager:    AssetGuard <info@assetguard.com>
Requires(pre):    /usr/sbin/groupadd /usr/sbin/useradd
Requires(postun): /usr/sbin/groupdel /usr/sbin/userdel
Conflicts:   ossec-hids ossec-hids-agent
Obsoletes: assetguard-api < 4.0.0
AutoReqProv: no

Requires: coreutils
BuildRequires: coreutils glibc-devel automake autoconf libtool policycoreutils-python curl perl

ExclusiveOS: linux

%define _source_payload w9.xzdio
%define _binary_payload w9.xzdio

%description
AssetGuard helps you to gain security visibility into your infrastructure by monitoring
hosts at an operating system and application level. It provides the following capabilities:
log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring

# Don't generate build_id links to prevent conflicts with other
# packages.
%global _build_id_links none

# Build debuginfo package
%package -n assetguard-manager-debuginfo
Requires: assetguard-manager = %{_version}-%{_release}
Summary: Debug information for package %{name}.
%description -n assetguard-manager-debuginfo
This package provides debug information for package %{name}.


%prep
%setup -q

./src/init/gen_ossec.sh conf manager centos %rhel %{_localstatedir} > etc/ossec-server.conf

%build
pushd src
# Rebuild for manager
make clean

# Build AssetGuard sources
make deps TARGET=manager
make -j%{_threads} TARGET=manager USE_SELINUX=yes DEBUG=%{_debugenabled}

popd

%install
# Clean BUILDROOT
rm -fr %{buildroot}

echo 'USER_LANGUAGE="en"' > ./etc/preloaded-vars.conf
echo 'USER_INSTALL_TYPE="manager"' >> ./etc/preloaded-vars.conf
echo 'USER_DIR="%{_localstatedir}"' >> ./etc/preloaded-vars.conf
echo 'USER_DELETE_DIR="y"' >> ./etc/preloaded-vars.conf
echo 'USER_UPDATE="n"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_EMAIL="n"' >> ./etc/preloaded-vars.conf
echo 'USER_WHITE_LIST="n"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_AUTHD="y"' >> ./etc/preloaded-vars.conf
echo 'USER_GENERATE_AUTHD_CERT="y"' >> ./etc/preloaded-vars.conf
echo 'USER_AUTO_START="n"' >> ./etc/preloaded-vars.conf
echo 'USER_CREATE_SSL_CERT="n"' >> ./etc/preloaded-vars.conf
echo 'DOWNLOAD_CONTENT="y"' >> ./etc/preloaded-vars.conf
./install.sh || { echo "install.sh failed! Aborting." >&2; exit 1; }

# Create directories
mkdir -p ${RPM_BUILD_ROOT}%{_initrddir}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}

# Copy the installed files into RPM_BUILD_ROOT directory
cp -pr %{_localstatedir}/* ${RPM_BUILD_ROOT}%{_localstatedir}/
sed -i "s:ASSETGUARD_HOME_TMP:%{_localstatedir}:g" src/init/templates/ossec-hids-rh.init
install -m 0755 src/init/templates/ossec-hids-rh.init ${RPM_BUILD_ROOT}%{_initrddir}/assetguard-manager
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
sed -i "s:ASSETGUARD_HOME_TMP:%{_localstatedir}:g" src/init/templates/assetguard-manager.service
install -m 0644 src/init/templates/assetguard-manager.service ${RPM_BUILD_ROOT}/usr/lib/systemd/system/

# Add configuration scripts
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/

# Templates for initscript
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/init
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/suse
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/sles

# Add SUSE initscript
sed -i "s:ASSETGUARD_HOME_TMP:%{_localstatedir}:g" src/init/templates/ossec-hids-suse.init
cp -rp src/init/templates/ossec-hids-suse.init ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/init/

# Copy scap templates
cp -rp  etc/templates/config/generic/* ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic
cp -rp  etc/templates/config/centos/* ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos
cp -rp  etc/templates/config/rhel/* ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel

install -m 0440 VERSION.json ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/
install -m 0640 src/init/*.sh ${RPM_BUILD_ROOT}%{_localstatedir}/packages_files/manager_installation_scripts/src/init

%{_rpmconfigdir}/find-debuginfo.sh

exit 0

%pre

# ============================================================
# HARD BLOCK: Prevent upgrade from 4.X to 5.X
# ============================================================
if [ $1 = 2 ]; then
  # Check if this is an upgrade from 4.X
  if [ -f %{_sysconfdir}/ossec-init.conf ]; then
    . %{_sysconfdir}/ossec-init.conf
    OLD_VERSION="${VERSION}"
  elif [ -x %{_localstatedir}/bin/assetguard-manager-control ]; then
    OLD_VERSION=$(%{_localstatedir}/bin/assetguard-manager-control info -v 2>/dev/null || echo "")
  fi

  if [ -n "${OLD_VERSION}" ]; then
    OLD_MAJOR=$(echo "${OLD_VERSION}" | sed 's/^v//' | cut -d. -f1)
    if [ -n "${OLD_MAJOR}" ] && [ "${OLD_MAJOR}" -le 4 ] 2>/dev/null; then
      cat <<EOF
==============================================================
ERROR: Direct upgrade from AssetGuard Manager 4.X to 5.X is not supported.

Detected installed version: ${OLD_VERSION}
==============================================================
EOF
      exit 1
    fi
  fi
fi

# Create the assetguard-manager group if it doesn't exists
if command -v getent > /dev/null 2>&1 && ! getent group assetguard-manager > /dev/null 2>&1; then
  groupadd -r assetguard-manager
elif ! getent group assetguard-manager > /dev/null 2>&1; then
  groupadd -r assetguard-manager
fi

# Create the assetguard-manager user if it doesn't exists
if ! getent passwd assetguard-manager > /dev/null 2>&1; then
  useradd -g assetguard-manager -G assetguard-manager -d %{_localstatedir} -r -s /sbin/nologin assetguard-manager
fi

# Validate upgrade constraints for Manager (only during upgrade)
if [ $1 = 2 ]; then
  # Get version information
  if [ -f "%{_localstatedir}/bin/assetguard-manager-control" ]; then
    OLD_VERSION=`%{_localstatedir}/bin/assetguard-manager-control info -v 2>/dev/null`
    MAJOR=$(echo $OLD_VERSION | cut -dv -f2 | cut -d. -f1)
  elif [ -f %{_localstatedir}/VERSION.json ]; then
    OLD_VERSION=`grep -oP '(?<="version": ")[^"]*' %{_localstatedir}/VERSION.json 2>/dev/null`
    MAJOR=$(echo $OLD_VERSION | cut -d. -f1)
  fi

  ERROR_TYPE=""

  # Determine if upgrade should be blocked
  if [ -z "$MAJOR" ]; then
    ERROR_TYPE="no_version"
    ERROR_TITLE="Cannot detect current version"
    ERROR_MESSAGE="Unable to detect the currently installed AssetGuard version."
  elif [ "$MAJOR" -lt 5 ]; then
    ERROR_TYPE="old_version"
    ERROR_TITLE="Clean installation required"
    ERROR_MESSAGE="Current version: $OLD_VERSION
Target version:  5.0.0

Direct upgrade from 4.x to 5.0.0 is NOT supported for AssetGuard Manager
due to breaking changes in database schema and architecture."
  fi

  # If any error was detected, show message and block
  if [ -n "$ERROR_TYPE" ]; then
    cat <<EOF >&2
═════════════════════════════════════════════════════════════════
  UPGRADE BLOCKED: $ERROR_TITLE
═════════════════════════════════════════════════════════════════

$ERROR_MESSAGE

Required action:
  1. Backup your configuration and data
  2. Perform a clean installation of AssetGuard 5.0.0
  3. Restore configuration as needed

For migration guide, visit:
  https://documentation.assetguard.com/current/migration-guide/
═════════════════════════════════════════════════════════════════
EOF
    exit 1
  fi
fi

# Stop the services to upgrade the package
if [ $1 = 2 ]; then
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 && systemctl is-active --quiet assetguard-manager > /dev/null 2>&1; then
    systemctl stop assetguard-manager.service > /dev/null 2>&1
    touch %{_localstatedir}/tmp/assetguard.restart
  # Check for SysV
  elif command -v service > /dev/null 2>&1 && service assetguard-manager status 2>/dev/null | grep "is running" > /dev/null 2>&1; then
    service assetguard-manager stop > /dev/null 2>&1
    touch %{_localstatedir}/tmp/assetguard.restart
  elif %{_localstatedir}/bin/assetguard-manager-control status 2>/dev/null | grep "is running" > /dev/null 2>&1; then
    touch %{_localstatedir}/tmp/assetguard.restart
  fi
  if [ -x %{_localstatedir}/bin/assetguard-manager-control ]; then
    %{_localstatedir}/bin/assetguard-manager-control stop > /dev/null 2>&1
  elif [ -x %{_localstatedir}/bin/assetguard-control ]; then
    %{_localstatedir}/bin/assetguard-control stop > /dev/null 2>&1
  elif [ -x %{_localstatedir}/bin/ossec-control ]; then
    %{_localstatedir}/bin/ossec-control stop > /dev/null 2>&1
  fi
fi
if pgrep -f ossec-authd > /dev/null 2>&1; then
    kill -15 $(pgrep -f ossec-authd)
fi

# Remove/relocate existing SQLite databases
rm -f %{_localstatedir}/var/db/cluster.db* || true
rm -f %{_localstatedir}/var/db/.profile.db* || true
rm -rf %{_localstatedir}/var/db/agents || true

if [ -f %{_localstatedir}/var/db/global.db ]; then
  mv %{_localstatedir}/var/db/global.db %{_localstatedir}/queue/db/
  rm -f %{_localstatedir}/var/db/global.db* || true
  rm -f %{_localstatedir}/var/db/.template.db || true
fi

if [ -f %{_localstatedir}/queue/db/global.db ]; then
  chmod 660 %{_localstatedir}/queue/db/global.db*
  chown assetguard-manager:assetguard-manager %{_localstatedir}/queue/db/global.db*
fi

# Remove Vuln-detector database
rm -f %{_localstatedir}/queue/vulnerabilities/cve.db || true

# Remove plain-text agent information if exists
if [ -d %{_localstatedir}/queue/agent-info ]; then
  rm -rf %{_localstatedir}/queue/agent-info/* > /dev/null 2>&1
fi

# Delete old API backups
if [ $1 = 2 ]; then
  if [ -d %{_localstatedir}/~api ]; then
    rm -rf %{_localstatedir}/~api
  fi

  # Ask assetguard-manager-control the version
  VERSION=$(%{_localstatedir}/bin/assetguard-manager-control info -v)

  # Get the major and minor version
  MAJOR=$(echo $VERSION | cut -dv -f2 | cut -d. -f1)
  MINOR=$(echo $VERSION | cut -d. -f2)

  # Delete uncompatible DBs versions
  if [ $MAJOR = 3 ] && [ $MINOR -lt 7 ]; then
    rm -f %{_localstatedir}/queue/db/*.db*
    rm -f %{_localstatedir}/queue/db/.template.db
  fi

  # Delete 3.X AssetGuard API service
  if [ "$MAJOR" = "3" ] && [ -d %{_localstatedir}/api ]; then
    if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 ; then
      systemctl stop assetguard-api.service > /dev/null 2>&1
      systemctl disable assetguard-api.service > /dev/null 2>&1
      rm -f /etc/systemd/system/assetguard-api.service
    elif command -v service > /dev/null 2>&1 && command -v chkconfig > /dev/null 2>&1; then
      service assetguard-api stop > /dev/null 2>&1
      chkconfig assetguard-api off > /dev/null 2>&1
      chkconfig --del assetguard-api > /dev/null 2>&1
      rm -f /etc/rc.d/init.d/assetguard-api || true
    fi
  fi
fi

%post

# Upgrade install code block
if [ $1 = 2 ]; then
  if [ -d %{_localstatedir}/logs/ossec ]; then
    rm -rf %{_localstatedir}/logs/assetguard
    cp -rp %{_localstatedir}/logs/ossec %{_localstatedir}/logs/assetguard
  fi

  if [ -d %{_localstatedir}/queue/ossec ]; then
    rm -rf %{_localstatedir}/queue/sockets
    cp -rp %{_localstatedir}/queue/ossec %{_localstatedir}/queue/sockets
  fi

fi

%define _vdfilename vd_1.0.0_vd_4.13.0.tar.xz

# Fresh install code block
if [ $1 = 1 ]; then

  . %{_localstatedir}/packages_files/manager_installation_scripts/src/init/dist-detect.sh

  # Generating assetguard-manager.conf file
  %{_localstatedir}/packages_files/manager_installation_scripts/src/init/gen_ossec.sh conf manager ${DIST_NAME} ${DIST_VER}.${DIST_SUBVER} %{_localstatedir} > %{_localstatedir}/etc/assetguard-manager.conf
  chown root:assetguard-manager %{_localstatedir}/etc/assetguard-manager.conf
  chmod 0660 %{_localstatedir}/etc/assetguard-manager.conf

  touch %{_localstatedir}/logs/assetguard-manager.log
  chown assetguard-manager:assetguard-manager %{_localstatedir}/logs/assetguard-manager.log
  chmod 0660 %{_localstatedir}/logs/assetguard-manager.log

  touch %{_localstatedir}/logs/assetguard-manager.json
  chown assetguard-manager:assetguard-manager %{_localstatedir}/logs/assetguard-manager.json
  chmod 0660 %{_localstatedir}/logs/assetguard-manager.json
fi

if [[ -d /run/systemd/system ]]; then
  rm -f %{_initrddir}/assetguard-manager
fi

# Generation auto-signed certificate if not exists
if [ ! -f "%{_localstatedir}/etc/sslmanager.key" ] && [ ! -f "%{_localstatedir}/etc/sslmanager.cert" ]; then
  %{_localstatedir}/bin/assetguard-manager-authd -C 365 -B 2048 -S "/C=US/ST=California/CN=AssetGuard/" -K %{_localstatedir}/etc/sslmanager.key -X %{_localstatedir}/etc/sslmanager.cert 2>/dev/null
  chmod 640 %{_localstatedir}/etc/sslmanager.key
  chmod 640 %{_localstatedir}/etc/sslmanager.cert
fi

rm -f %{_localstatedir}/etc/shared/ar.conf  >/dev/null 2>&1
rm -f %{_localstatedir}/etc/shared/merged.mg  >/dev/null 2>&1

# Set merged.mg permissions to new ones
find %{_localstatedir}/etc/shared/ -type f -name 'merged.mg' -exec chmod 644 {} \;

# Add the SELinux policy
if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
  if [ $(getenforce) != "Disabled" ]; then
    semodule -i %{_localstatedir}/var/selinux/assetguard.pp
    semodule -e assetguard
  fi
fi

# Restore assetguard-manager.conf permissions after upgrading
chown root:assetguard-manager %{_localstatedir}/etc/assetguard-manager.conf
chmod 0660 %{_localstatedir}/etc/assetguard-manager.conf

# Delete the installation files used to configure the manager
rm -rf %{_localstatedir}/packages_files

# Remove unnecessary files from default group
rm -f %{_localstatedir}/etc/shared/default/*.rpmnew

# Remove old ossec user and group if exists and change ownwership of files

if getent group ossec > /dev/null 2>&1; then
  find %{_localstatedir}/ -group ossec -user root -print0 | xargs -0 chown root:assetguard-manager > /dev/null 2>&1 || true
  if getent passwd ossec > /dev/null 2>&1; then
    find %{_localstatedir}/ -group ossec -user ossec -print0 | xargs -0 chown assetguard-manager:assetguard-manager > /dev/null 2>&1 || true
    userdel ossec > /dev/null 2>&1
  fi
  if getent passwd ossecm > /dev/null 2>&1; then
    find %{_localstatedir}/ -group ossec -user ossecm -print0 | xargs -0 chown assetguard-manager:assetguard-manager > /dev/null 2>&1 || true
    userdel ossecm > /dev/null 2>&1
  fi
  if getent passwd ossecr > /dev/null 2>&1; then
    find %{_localstatedir}/ -group ossec -user ossecr -print0 | xargs -0 chown assetguard-manager:assetguard-manager > /dev/null 2>&1 || true
    userdel ossecr > /dev/null 2>&1
  fi
  if getent group ossec > /dev/null 2>&1; then
    groupdel ossec > /dev/null 2>&1
  fi
fi

%preun

if [ $1 = 0 ]; then

  # Stop the services before uninstall the package
  # Check for systemd
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 && systemctl is-active --quiet assetguard-manager > /dev/null 2>&1; then
    systemctl stop assetguard-manager.service > /dev/null 2>&1
  # Check for SysV
  elif command -v service > /dev/null 2>&1 && service assetguard-manager status 2>/dev/null | grep "is running" > /dev/null 2>&1; then
    service assetguard-manager stop > /dev/null 2>&1
  fi
  %{_localstatedir}/bin/assetguard-manager-control stop > /dev/null 2>&1

  # Remove the SELinux policy
  if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
    if [ $(getenforce) != "Disabled" ]; then
      if (semodule -l | grep assetguard > /dev/null); then
        semodule -r assetguard > /dev/null
      fi
    fi
  fi

fi

%postun

# If the package is been uninstalled
if [ $1 = 0 ];then
  # Remove the assetguard-manager user if it exists
  if getent passwd assetguard-manager > /dev/null 2>&1; then
    userdel assetguard-manager >/dev/null 2>&1
  fi
  # Remove the assetguard-manager group if it exists
  if command -v getent > /dev/null 2>&1 && getent group assetguard-manager > /dev/null 2>&1; then
    groupdel assetguard-manager >/dev/null 2>&1
  elif getent group assetguard-manager > /dev/null 2>&1; then
    groupdel assetguard-manager >/dev/null 2>&1
  fi

  # Backup agents centralized configuration (etc/shared)
  if [ -d %{_localstatedir}/etc/shared ]; then
    find %{_localstatedir}/etc/ -type f  -name "*save" ! -name "*rpmsave" -exec rm -f {} \;
    find %{_localstatedir}/etc/ -type f ! -name "*shared*" ! -name "*rpmsave" -exec mv {} {}.save \;
  fi

  # Backup registration service certificates (sslmanager.cert,sslmanager.key)
  if [ -f %{_localstatedir}/etc/sslmanager.cert ]; then
      mv %{_localstatedir}/etc/sslmanager.cert %{_localstatedir}/etc/sslmanager.cert.save
  fi
  if [ -f %{_localstatedir}/etc/sslmanager.key ]; then
      mv %{_localstatedir}/etc/sslmanager.key %{_localstatedir}/etc/sslmanager.key.save
  fi

  # Remove lingering folders and files
  rm -rf %{_localstatedir}/queue/
  rm -rf %{_localstatedir}/framework/
  rm -rf %{_localstatedir}/api/
  rm -rf %{_localstatedir}/stats/
  rm -rf %{_localstatedir}/var/
  rm -rf %{_localstatedir}/bin/
  rm -rf %{_localstatedir}/logs/
  rm -rf %{_localstatedir}/tmp
  rm -rf %{_localstatedir}/engine

  # Delete audisp assetguard plugin if exists
  if [ -e /etc/audit/plugins.d/af_assetguard.conf ]; then
    rm -f -- /etc/audit/plugins.d/af_assetguard.conf
  fi
  if [ -e /etc/audisp/plugins.d/af_assetguard.conf ]; then
    rm -f -- /etc/audisp/plugins.d/af_assetguard.conf
  fi
fi

# posttrans code is the last thing executed in a install/upgrade
%posttrans
if [ -f %{_sysconfdir}/systemd/system/assetguard-manager.service ]; then
  rm -rf %{_sysconfdir}/systemd/system/assetguard-manager.service
  systemctl daemon-reload > /dev/null 2>&1
fi

if [ -f %{_localstatedir}/tmp/assetguard.restart ]; then
  rm -f %{_localstatedir}/tmp/assetguard.restart
  if command -v systemctl > /dev/null 2>&1 && systemctl > /dev/null 2>&1 ; then
    systemctl daemon-reload > /dev/null 2>&1
    systemctl restart assetguard-manager.service > /dev/null 2>&1
  elif command -v service > /dev/null 2>&1 ; then
    service assetguard-manager restart > /dev/null 2>&1
  else
    %{_localstatedir}/bin/assetguard-manager-control restart > /dev/null 2>&1
  fi
fi

if [ -d %{_localstatedir}/logs/ossec ]; then
  rm -rf %{_localstatedir}/logs/ossec/
fi

if [ -d %{_localstatedir}/queue/ossec ]; then
  rm -rf %{_localstatedir}/queue/ossec/
fi

# Remove groups backup files
rm -rf %{_localstatedir}/backup/groups

%triggerin -- glibc
[ -r %{_sysconfdir}/localtime ] && cp -fpL %{_sysconfdir}/localtime %{_localstatedir}/etc
 chown root:root %{_localstatedir}/etc/localtime
 chmod 0640 %{_localstatedir}/etc/localtime

%clean
rm -fr %{buildroot}

%files
%defattr(-,root,assetguard-manager)
%config(missingok) %{_initrddir}/assetguard-manager
/usr/lib/systemd/system/assetguard-manager.service
%dir %attr(750, root, assetguard-manager) %{_localstatedir}
%attr(440, root, assetguard-manager) %{_localstatedir}/VERSION.json
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/active-response
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/active-response/bin
%attr(750, root, assetguard-manager) %{_localstatedir}/active-response/bin/kaspersky.py
%attr(750, root, assetguard-manager) %{_localstatedir}/active-response/bin/restart.sh
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/api
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/api/configuration
%attr(660, root, assetguard-manager) %config(noreplace) %{_localstatedir}/api/configuration/api.yaml
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/api/configuration/security
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/api/configuration/ssl
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/api/scripts
%attr(640, root, assetguard-manager) %{_localstatedir}/api/scripts/*.py
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/backup
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/backup/db
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/backup/agents
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/backup/shared
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/bin
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/agent_groups
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/agent_upgrade
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/cluster_control
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-analysisd
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-authd
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-control
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-monitord
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-remoted
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/verify-agent-conf
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/assetguard-manager-apid
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/assetguard-manager-clusterd
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-db
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-modulesd
%attr(750, root, assetguard-manager) %{_localstatedir}/bin/rbac_control
%attr(750, root, root) %{_localstatedir}/bin/assetguard-manager-keystore
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/etc
%attr(660, root, assetguard-manager) %ghost %{_localstatedir}/etc/assetguard-manager.conf
%attr(640, root, root) %ghost %{_localstatedir}/etc/sslmanager.cert
%attr(640, root, root) %ghost %{_localstatedir}/etc/sslmanager.key
%attr(660, assetguard-manager, assetguard-manager) %config(noreplace) %{_localstatedir}/etc/client.keys
%attr(640, root, assetguard-manager) %{_localstatedir}/etc/internal_options*
%attr(640, root, assetguard-manager) %config(noreplace) %{_localstatedir}/etc/local_internal_options.conf
%attr(640, root, root) %{_localstatedir}/etc/localtime
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/etc/shared
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/etc/shared/default
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/etc/shared/agent-template.conf
%attr(660, assetguard-manager, assetguard-manager) %config(noreplace) %{_localstatedir}/etc/shared/default/*
%dir %attr(755, root, root) %{_localstatedir}/engine
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema/allowed-fields
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema/allowed-fields/0
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema/engine-schema
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema/engine-schema/0
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema/assetguard-logpar-overrides
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/schema/assetguard-logpar-overrides/0
%dir %attr(755, root, root) %{_localstatedir}/engine/store/geo
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/engine/store/geo/mmdb
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/geo/mmdb/0
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/engine/mmdb
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/mmdb/*.mmdb
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/enrichment
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/enrichment/geo
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/enrichment/geo/0
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/enrichment/ioc
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/store/enrichment/ioc/0
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/outputs
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/engine/outputs/*.yml
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/python
%{_localstatedir}/framework/python/*
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/scripts
%attr(640, root, assetguard-manager) %{_localstatedir}/framework/scripts/*.py
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/assetguard
%attr(640, root, assetguard-manager) %{_localstatedir}/framework/assetguard/*.py
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster
%attr(640, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster/*.py
%attr(640, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster/*.json
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster/hap_helper
%attr(640, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster/hap_helper/*.py
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster/dapi
%attr(640, root, assetguard-manager) %{_localstatedir}/framework/assetguard/core/cluster/dapi/*.py
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/lib
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libassetguardext.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libassetguardshared.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libschema_validator.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libjemalloc.so.2
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libstdc++.so.6
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libgcc_s.so.1
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libcontent_manager.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libindexer_connector.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libinventory_sync.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/libvulnerability_scanner.so
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/librocksdb.so.8
%attr(750, root, assetguard-manager) %{_localstatedir}/lib/librouter.so
%{_localstatedir}/lib/libpython3.12.so.1.0
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/logs
%attr(660, assetguard-manager, assetguard-manager) %ghost %{_localstatedir}/logs/api.log
%attr(660, assetguard-manager, assetguard-manager) %ghost %{_localstatedir}/logs/assetguard-manager.log
%attr(660, assetguard-manager, assetguard-manager) %ghost %{_localstatedir}/logs/assetguard-manager.json
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/logs/api
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/logs/archives
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/logs/alerts
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/logs/cluster
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/logs/firewall
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/logs/assetguard
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts
%attr(440, assetguard-manager, assetguard-manager) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/VERSION.json
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/init/
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/src/init/*
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/generic/*
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/centos/*
%dir %attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel
%attr(750, root, root) %config(missingok) %{_localstatedir}/packages_files/manager_installation_scripts/etc/templates/config/rhel/*
%attr(640, assetguard-manager, assetguard-manager) %missingok %{_localstatedir}/tmp/%{_vdfilename}
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue
%attr(660, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/agents-timestamp
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/alerts
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/cluster
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/db
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/rids
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/tasks
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/sockets
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/vd
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/indexer
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/router
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/keystore
%dir %attr(750, assetguard-manager, assetguard-manager) %{_localstatedir}/queue/tzdb
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/etc/ruleset
%dir %attr(1770, root, assetguard-manager) %{_localstatedir}/tmp
%dir %attr(750, root, assetguard-manager) %{_localstatedir}/var
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/var/db
%attr(660, root, assetguard-manager) %{_localstatedir}/var/db/mitre.db
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/var/download
%dir %attr(770, assetguard-manager, assetguard-manager) %{_localstatedir}/var/multigroups
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/var/run
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/var/selinux
%attr(640, root, assetguard-manager) %{_localstatedir}/var/selinux/*
%dir %attr(770, root, assetguard-manager) %{_localstatedir}/var/upgrade

%files -n assetguard-manager-debuginfo -f debugfiles.list

%changelog
* Sun Apr 12 2026 support <info@assetguard.com> - 5.0.0
- More info: https://documentation.assetguard.com/current/release-notes/release-5-0-0.html
* Sat Apr 11 2026 support <info@assetguard.com> - 4.14.5
- More info: https://documentation.assetguard.com/current/release-notes/release-4-14-5.html
* Wed Mar 11 2026 support <info@assetguard.com> - 4.14.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-14-4.html
* Wed Feb 11 2026 support <info@assetguard.com> - 4.14.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-14-3.html
* Wed Jan 14 2026 support <info@assetguard.com> - 4.14.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-14-2.html
* Wed Nov 12 2025 support <info@assetguard.com> - 4.14.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-14-1.html
* Wed Oct 22 2025 support <info@assetguard.com> - 4.14.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-14-0.html
* Wed Sep 24 2025 support <info@assetguard.com> - 4.13.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-13-1.html
* Thu Sep 18 2025 support <info@assetguard.com> - 4.13.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-13-0.html
* Wed May 07 2025 support <info@assetguard.com> - 4.12.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-12-0.html
* Tue Apr 01 2025 support <info@assetguard.com> - 4.11.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-11-2.html
* Wed Mar 12 2025 support <info@assetguard.com> - 4.11.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-11-1.html
* Wed Feb 19 2025 support <info@assetguard.com> - 4.11.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-11-0.html
* Thu Jan 16 2025 support <info@assetguard.com> - 4.10.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-10-1.html
* Thu Jan 09 2025 support <info@assetguard.com> - 4.10.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-10-0.html
* Wed Oct 30 2024 support <info@assetguard.com> - 4.9.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-9-2.html
* Thu Oct 17 2024 support <info@assetguard.com> - 4.9.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-9-1.html
* Thu Sep 05 2024 support <info@assetguard.com> - 4.9.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-9-0.html
* Wed Jul 10 2024 support <info@assetguard.com> - 4.8.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-8-1.html
* Wed Jun 12 2024 support <info@assetguard.com> - 4.8.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-8-0.html
* Thu May 30 2024 support <info@assetguard.com> - 4.7.5
- More info: https://documentation.assetguard.com/current/release-notes/release-4-7-5.html
* Thu Apr 25 2024 support <info@assetguard.com> - 4.7.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-7-4.html
* Tue Feb 27 2024 support <info@assetguard.com> - 4.7.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-7-3.html
* Tue Jan 09 2024 support <info@assetguard.com> - 4.7.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-7-2.html
* Wed Dec 13 2023 support <info@assetguard.com> - 4.7.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-7-1.html
* Tue Nov 21 2023 support <info@assetguard.com> - 4.7.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-7-0.html
* Tue Oct 31 2023 support <info@assetguard.com> - 4.6.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-6-0.html
* Tue Oct 24 2023 support <info@assetguard.com> - 4.5.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-5-4.html
* Tue Oct 10 2023 support <info@assetguard.com> - 4.5.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-5-3.html
* Thu Aug 31 2023 support <info@assetguard.com> - 4.5.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-5-2.html
* Thu Aug 24 2023 support <info@assetguard.com> - 4.5.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-5.1.html
* Thu Aug 10 2023 support <info@assetguard.com> - 4.5.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-5-0.html
* Mon Jul 10 2023 support <info@assetguard.com> - 4.4.5
- More info: https://documentation.assetguard.com/current/release-notes/release-4-4-5.html
* Tue Jun 13 2023 support <info@assetguard.com> - 4.4.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-4-4.html
* Thu May 25 2023 support <info@assetguard.com> - 4.4.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-4-3.html
* Mon May 08 2023 support <info@assetguard.com> - 4.4.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-4-2.html
* Mon Apr 24 2023 support <info@assetguard.com> - 4.3.11
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3.11.html
* Mon Apr 17 2023 support <info@assetguard.com> - 4.4.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-4-1.html
* Wed Jan 18 2023 support <info@assetguard.com> - 4.4.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-4-0.html
* Thu Nov 10 2022 support <info@assetguard.com> - 4.3.10
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-10.html
* Mon Oct 03 2022 support <info@assetguard.com> - 4.3.9
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-9.html
* Wed Sep 21 2022 support <info@assetguard.com> - 3.13.6
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-6.html
* Mon Sep 19 2022 support <info@assetguard.com> - 4.3.8
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-8.html
* Wed Aug 24 2022 support <info@assetguard.com> - 3.13.5
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-5.html
* Mon Aug 08 2022 support <info@assetguard.com> - 4.3.7
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-7.html
* Thu Jul 07 2022 support <info@assetguard.com> - 4.3.6
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-6.html
* Wed Jun 29 2022 support <info@assetguard.com> - 4.3.5
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-5.html
* Tue Jun 07 2022 support <info@assetguard.com> - 4.3.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-4.html
* Tue May 31 2022 support <info@assetguard.com> - 4.3.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-3.html
* Mon May 30 2022 support <info@assetguard.com> - 4.3.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-2.html
* Mon May 30 2022 support <info@assetguard.com> - 3.13.4
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-4.html
* Sun May 29 2022 support <info@assetguard.com> - 4.2.7
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-7.html
* Wed May 18 2022 support <info@assetguard.com> - 4.3.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-1.html
* Thu May 05 2022 support <info@assetguard.com> - 4.3.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-3-0.html
* Fri Mar 25 2022 support <info@assetguard.com> - 4.2.6
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-6.html
* Mon Nov 15 2021 support <info@assetguard.com> - 4.2.5
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-5.html
* Thu Oct 21 2021 support <info@assetguard.com> - 4.2.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-4.html
* Wed Oct 06 2021 support <info@assetguard.com> - 4.2.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-3.html
* Tue Sep 28 2021 support <info@assetguard.com> - 4.2.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-2.html
* Sat Sep 25 2021 support <info@assetguard.com> - 4.2.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-1.html
* Mon Apr 26 2021 support <info@assetguard.com> - 4.2.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-2-0.html
* Sat Apr 24 2021 support <info@assetguard.com> - 3.13.3
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-3.html
* Thu Apr 22 2021 support <info@assetguard.com> - 4.1.5
- More info: https://documentation.assetguard.com/current/release-notes/release-4-1-5.html
* Mon Mar 29 2021 support <info@assetguard.com> - 4.1.4
- More info: https://documentation.assetguard.com/current/release-notes/release-4-1-4.html
* Sat Mar 20 2021 support <info@assetguard.com> - 4.1.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-1-3.html
* Mon Mar 08 2021 support <info@assetguard.com> - 4.1.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-1-2.html
* Fri Mar 05 2021 support <info@assetguard.com> - 4.1.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-1-1.html
* Tue Jan 19 2021 support <info@assetguard.com> - 4.1.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-1-0.html
* Mon Nov 30 2020 support <info@assetguard.com> - 4.0.3
- More info: https://documentation.assetguard.com/current/release-notes/release-4-0-3.html
* Mon Nov 23 2020 support <info@assetguard.com> - 4.0.2
- More info: https://documentation.assetguard.com/current/release-notes/release-4-0-2.html
* Sat Oct 31 2020 support <info@assetguard.com> - 4.0.1
- More info: https://documentation.assetguard.com/current/release-notes/release-4-0-1.html
* Mon Oct 19 2020 support <info@assetguard.com> - 4.0.0
- More info: https://documentation.assetguard.com/current/release-notes/release-4-0-0.html
* Fri Aug 21 2020 support <info@assetguard.com> - 3.13.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-2.html
* Tue Jul 14 2020 support <info@assetguard.com> - 3.13.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-1.html
* Mon Jun 29 2020 support <info@assetguard.com> - 3.13.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-13-0.html
* Wed May 13 2020 support <info@assetguard.com> - 3.12.3
- More info: https://documentation.assetguard.com/current/release-notes/release-3-12-3.html
* Thu Apr 9 2020 support <info@assetguard.com> - 3.12.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-12-2.html
* Wed Apr 8 2020 support <info@assetguard.com> - 3.12.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-12-1.html
* Wed Mar 25 2020 support <info@assetguard.com> - 3.12.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-12-0.html
* Mon Feb 24 2020 support <info@assetguard.com> - 3.11.4
- More info: https://documentation.assetguard.com/current/release-notes/release-3-11-4.html
* Wed Jan 22 2020 support <info@assetguard.com> - 3.11.3
- More info: https://documentation.assetguard.com/current/release-notes/release-3-11-3.html
* Tue Jan 7 2020 support <info@assetguard.com> - 3.11.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-11-2.html
* Thu Dec 26 2019 support <info@assetguard.com> - 3.11.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-11-1.html
* Mon Oct 7 2019 support <info@assetguard.com> - 3.11.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-11-0.html
* Mon Sep 23 2019 support <support@assetguard.com> - 3.10.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-10-2.html
* Thu Sep 19 2019 support <support@assetguard.com> - 3.10.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-10-1.html
* Mon Aug 26 2019 support <support@assetguard.com> - 3.10.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-10-0.html
* Thu Aug 8 2019 support <support@assetguard.com> - 3.9.5
- More info: https://documentation.assetguard.com/current/release-notes/release-3-9-5.html
* Fri Jul 12 2019 support <support@assetguard.com> - 3.9.4
- More info: https://documentation.assetguard.com/current/release-notes/release-3-9-4.html
* Tue Jul 02 2019 support <support@assetguard.com> - 3.9.3
- More info: https://documentation.assetguard.com/current/release-notes/release-3-9-3.html
* Tue Jun 11 2019 support <support@assetguard.com> - 3.9.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-9-2.html
* Sat Jun 01 2019 support <support@assetguard.com> - 3.9.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-9-1.html
* Mon Feb 25 2019 support <support@assetguard.com> - 3.9.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-9-0.html
* Wed Jan 30 2019 support <support@assetguard.com> - 3.8.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-8-2.html
* Thu Jan 24 2019 support <support@assetguard.com> - 3.8.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-8-1.html
* Fri Jan 18 2019 support <support@assetguard.com> - 3.8.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-8-0.html
* Wed Nov 7 2018 support <support@assetguard.com> - 3.7.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-7-0.html
* Mon Sep 10 2018 support <info@assetguard.com> - 3.6.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-6-1.html
* Fri Sep 7 2018 support <support@assetguard.com> - 3.6.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-6-0.html
* Wed Jul 25 2018 support <support@assetguard.com> - 3.5.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-5-0.html
* Wed Jul 11 2018 support <support@assetguard.com> - 3.4.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-4-0.html
* Mon Jun 18 2018 support <support@assetguard.com> - 3.3.1
- More info: https://documentation.assetguard.com/current/release-notes/release-3-3-1.html
* Mon Jun 11 2018 support <support@assetguard.com> - 3.3.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-3-0.html
* Wed May 30 2018 support <support@assetguard.com> - 3.2.4
- More info: https://documentation.assetguard.com/current/release-notes/release-3-2-4.html
* Thu May 10 2018 support <support@assetguard.com> - 3.2.3
- More info: https://documentation.assetguard.com/current/release-notes/release-3-2-3.html
* Mon Apr 09 2018 support <support@assetguard.com> - 3.2.2
- More info: https://documentation.assetguard.com/current/release-notes/release-3-2-2.html
* Wed Feb 21 2018 support <support@assetguard.com> - 3.2.1
- More info: https://documentation.assetguard.com/current/release-notes/rerlease-3-2-1.html
* Wed Feb 07 2018 support <support@assetguard.com> - 3.2.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-2-0.html
* Thu Dec 21 2017 support <support@assetguard.com> - 3.1.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-1-0.html
* Mon Nov 06 2017 support <support@assetguard.com> - 3.0.0
- More info: https://documentation.assetguard.com/current/release-notes/release-3-0-0.html
* Tue Jun 06 2017 support <support@assetguard.com> - 2.0.1
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fix permissions in agent-info folder
- Fix permissions in rids folder.
* Fri Apr 21 2017 Jose Luis Ruiz <jose@assetguard.com> - 2.0
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fixed resource leaks at rules configuration parsing.
- Fixed memory leaks at rules parser.
- Fixed memory leaks at XML decoders parser.
- Fixed TOCTOU condition when removing directories recursively.
- Fixed insecure temporary file creation for old POSIX specifications.
- Fixed missing agentless devices identification at JSON alerts.
- Fixed FIM timestamp and file name issue at SQLite database.
- Fixed cryptographic context acquirement on Windows agents.
- Fixed debug mode for Analysisd.
- Fixed bad exclusion of BTRFS filesystem by Rootcheck.
- Fixed compile errors on macOS.
- Fixed option -V for Integrator.
- Exclude symbolic links to directories when sending FIM diffs (by Stephan Joerrens).
- Fixed daemon list for service reloading at ossec-control.
- Fixed socket waiting issue on Windows agents.
- Fixed PCI_DSS definitions grouping issue at Rootcheck controls.
