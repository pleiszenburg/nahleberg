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

import asyncio
import os
import platform

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
)

from qgis.gui import QgisInterface

from qasync import asyncSlot, QEventLoop

from typeguard import typechecked

from .i18n import (
    translate as tr,
    setupTranslation,
)
from .config import Config, get_config_path
from .const import (
    CONFIG_FN,
    ICON_FLD,
    PLUGIN_ICON_FN,
    PLUGIN_NAME,
    TRANSLATION_FLD,
)
from .error import ClusterConnected, ClusterDisconnected
from .fsm import Fsm
from .msg import msg_critical, msg_warning

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

        self._ui_dict = {}
        self._ui_cleanup = []

        self._fsm = None
        self._translator = None
        self._translator_path = None
        self._wait_for_mainwindow = None
        self._loop = None


    def initGui(self):
        """
        QGIS Plugin Interface Routine
        """

        self._translator, self._translator_path = setupTranslation(os.path.join(
            self._plugin_root_fld, TRANSLATION_FLD
            ))

        # self._ui_dict['action_manage'] = QAction(tr('&Nahleberg Management'))
        # self._ui_dict['action_manage'].setObjectName('action_manage')
        # self._ui_dict['action_manage'].setEnabled(False)
        # self._ui_dict['action_manage'].setIcon(QIcon(os.path.join(
        #     self._plugin_root_fld, ICON_FLD, PLUGIN_ICON_FN
        #     )))
        #
        # nahlebergMenuText = tr('Nahle&berg')
        # self._iface.addPluginToMenu(nahlebergMenuText, self._ui_dict['action_manage'])
        # self._ui_cleanup.append(
        #     lambda: self._iface.removePluginMenu(nahlebergMenuText, self._ui_dict['action_manage'])
        #     )

        self._ui_dict['toolbar_iface'] = self._iface.addToolBar(tr(PLUGIN_NAME))
        self._ui_dict['toolbar_iface'].setObjectName(PLUGIN_NAME.lower())
        self._ui_cleanup.append(
            lambda: self._ui_dict['toolbar_iface'].setParent(None)
            )

        for name, tooltip in (
            ('connect', tr('Connect to existing cluster')),
            ('disconnect', tr('Disconnect from cluster')),
            ('new', tr('New cluster')),
            ('destroy', tr('Destroy cluster')),
        ):
            self._ui_dict[f'action_{name:s}'] = QAction()
            self._ui_dict[f'action_{name:s}'].setObjectName(f'action_{name:s}')
            self._ui_dict[f'action_{name:s}'].setIcon(QIcon(os.path.join(
                self._plugin_root_fld, ICON_FLD, f'{name:s}.svg'
                )))
            self._ui_dict[f'action_{name:s}'].setToolTip(tooltip)
            self._ui_dict[f'action_{name:s}'].setEnabled(False)
            self._ui_dict['toolbar_iface'].addAction(self._ui_dict[f'action_{name:s}'])

        self._wait_for_mainwindow = True
        self._iface.initializationCompleted.connect(self._connect_ui)


    def _connect_ui(self):

        if not self._wait_for_mainwindow:
            return
        self._wait_for_mainwindow = False
        self._iface.initializationCompleted.disconnect(self._connect_ui)

        try:
            app = QCoreApplication.instance()
            self._loop = QEventLoop(app, already_running = True)
            asyncio.set_event_loop(self._loop)
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return

        try:
            config = Config(os.path.join(get_config_path(), CONFIG_FN))
            self._fsm = Fsm(config = config)
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return

        for name in (
            'connect',
            'disconnect',
            'new',
            'destroy',
        ):
            self._ui_dict[f'action_{name:s}'].triggered.connect(getattr(self, f'_{name:s}'))


    @asyncSlot
    async def _connect(self):

        prefix = 'cluster' # TODO

        try:
            await self._fsm.connect(prefix = prefix)
        except ClusterConnected as e:
            msg_warning(e, self._mainwindow)
            return
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return


    @asyncSlot
    async def _disconnect(self):

        try:
            await self._fsm.disconnect()
        except ClusterDisconnected as e:
            msg_warning(e, self._mainwindow)
            return
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return


    @asyncSlot
    async def _new(self):

        prefix = 'cluster' # TODO

        try:
            await self._fsm.new(prefix = prefix)
        except ClusterConnected as e:
            msg_warning(e, self._mainwindow)
            return
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return


    @asyncSlot
    async def _destroy(self):

        try:
            await self._fsm.destroy()
        except ClusterDisconnected as e:
            msg_warning(e, self._mainwindow)
            return
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return


    def unload(self):
        """
        QGIS Plugin Interface Routine
        """

        for item in self._ui_dict.values():
            if not hasattr(item, 'setVisible'):
                continue
            item.setVisible(False)

        for cleanup_action in self._ui_cleanup:
            cleanup_action()

        self._ui_dict.clear()
        self._ui_cleanup.clear()
