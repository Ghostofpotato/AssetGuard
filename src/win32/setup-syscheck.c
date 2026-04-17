/* Copyright (C) 2015, AssetGuard Inc.
 * Copyright (C) 2009 Trend Micro Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General Public
 * License (version 2) as published by the FSF - Free Software
 * Foundation
 */

#include "setup-shared.h"
#include "os_xml.h"
#include "error_messages.h"
#include <errno.h>
#define ASSETGUARD_CONFIG_TMP  ".tmp.assetguard.conf"


/* Enable Syscheck */
int main(int argc, char **argv)
{
    char *status;
    const char *(xml_syscheck_status[]) = {"assetguard_config", "syscheck", "disabled", NULL};

    if (argc < 3) {
        printf("%s: Invalid syntax.\n", argv[0]);
        printf("Try: '%s <dir> [enable|disable]'\n\n", argv[0]);
        return (0);
    }

    /* Check for directory */
    if (chdir(argv[1]) != 0) {
        printf("%s: Invalid directory: '%s'.\n", argv[0], argv[1]);
        return (0);
    }

    /* Check if AssetGuard was installed already */
    if (!fileexist(ASSETGUARDCONF)) {
        printf("%s: AssetGuard not installed yet. Exiting.\n", argv[0]);
        return (0);
    }

    /* Check status */
    if (strcmp(argv[2], "enable") == 0) {
        status = "no";
    } else {
        status = "yes";
    }

    /* Write to the config file */
    if (OS_WriteXML(ASSETGUARDCONF, ASSETGUARD_CONFIG_TMP, xml_syscheck_status,
                    "no", status) != 0) {
        printf("%s: Error writing to the Config file. Exiting.\n", argv[0]);
        return (0);
    }

    /* Rename config files */
    unlink(ASSETGUARDLAST);
    if (rename(ASSETGUARDCONF, ASSETGUARDLAST)) {
        printf(RENAME_ERROR, ASSETGUARDCONF, ASSETGUARDLAST, errno, strerror(errno));
    }
    if (rename(ASSETGUARD_CONFIG_TMP, ASSETGUARDCONF)) {
        printf(RENAME_ERROR, ASSETGUARD_CONFIG_TMP, ASSETGUARDCONF, errno, strerror(errno));
    }

    return (0);
}
