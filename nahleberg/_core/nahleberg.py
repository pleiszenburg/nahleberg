# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    nahleberg/_core/nahleberg.py: Plugin core class

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

import os
from sys import platform

from qgis.gui import QgisInterface

from typeguard import typechecked

from .i18n import translate as tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Nahleberg:

    def __init__(self, iface: QgisInterface, plugin_root_fld: str):

        if not os.path.exists(plugin_root_fld):
            raise ValueError(tr('plugin_root_fld must exists'))
        if not os.path.isdir(plugin_root_fld):
            raise ValueError(tr('plugin_root_fld must be a directory'))

        self._iface = iface
        self._plugin_root_fld = plugin_root_fld

        self._mainwindow = self._iface.mainWindow()
        self._system = platform.system()
