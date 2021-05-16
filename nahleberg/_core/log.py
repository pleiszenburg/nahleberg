# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    nahleberg/_core/log.py: Logging wrapper for QGIS

    Copyright (C) 2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU General Public License
Version 2 ("GPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
https://github.com/pleiszenburg/nahleberg/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from logging import getLogger, Logger
from typing import Any, Callable

from qgis.core import QgsMessageLog, Qgis

from typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
def _log(name: str, level: int) -> Callable:

    @typechecked
    def wrapper(message: str, *args: Any):
        QgsMessageLog.logMessage(
            message = message % args,
            tag = name,
            level = level,
        )

    return wrapper


@typechecked
def get_logger(name: str) -> Logger:

    log = getLogger(name)

    log.info = _log(name, Qgis.Info)
    log.warning = _log(name, Qgis.Warning)
    log.warn = log.warning
    log.error = _log(name, Qgis.Critical) # HACK
    log.exception = _log(name, Qgis.Critical) # HACK
    log.critical = _log(name, Qgis.Critical)

    return log
