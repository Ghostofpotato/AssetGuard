# Copyright (C) 2015-2024, AssetGuard Inc.
# Created by AssetGuard, Inc. <info@assetguard.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
import sys
import time
import pytest

from pathlib import Path

from assetguard_testing.constants.paths.logs import ASSETGUARD_LOG_PATH
from assetguard_testing.constants.platforms import WINDOWS
from assetguard_testing.modules.fim.patterns import EVENT_TYPE_ADDED, PATH_MONITORED_REALTIME
from assetguard_testing.tools.monitors.file_monitor import FileMonitor
from assetguard_testing.utils import file
from assetguard_testing.utils.callbacks import generate_callback


@pytest.fixture()
def path_to_edit(test_metadata: dict) -> str:
    to_edit = test_metadata.get('path_to_edit')
    is_directory = test_metadata.get('is_directory')

    fim_mode = test_metadata.get('fim_mode', '')
    if sys.platform == WINDOWS and fim_mode == 'realtime':
        FileMonitor(ASSETGUARD_LOG_PATH).start(
            callback=generate_callback(PATH_MONITORED_REALTIME),
            timeout=60
        )

    if is_directory:
        file.recursive_directory_creation(to_edit)
        if sys.platform == WINDOWS:
            time.sleep(5)
        file.write_file(Path(to_edit, 'newfile'), 'test')
    else:
        file.write_file(to_edit, 'test')

    FileMonitor(ASSETGUARD_LOG_PATH).start(generate_callback(EVENT_TYPE_ADDED))

    yield to_edit

    file.delete_path_recursively(to_edit)
