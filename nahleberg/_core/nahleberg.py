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

from asyncio import (
    CancelledError,
    create_task,
    set_event_loop,
    sleep,
)
import os
import platform
from typing import Any, Callable

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAction,
    QRadioButton,
)

from qgis.gui import QgisInterface

from qasync import QEventLoop

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
    RADIO_COLOR,
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
        self._action_names = None

        self._busy_task = None


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

        self._ui_dict['radio_status'] = QRadioButton()
        self._ui_dict['radio_status'].setObjectName('radio_status')
        self._ui_dict['radio_status'].setToolTip(tr('disconnected'))
        self._ui_dict['radio_status'].setEnabled(False)
        self._ui_dict['radio_status'].setChecked(True)
        self._set_color('red')
        self._ui_dict['toolbar_iface'].addWidget(self._ui_dict['radio_status'])

        self._action_names = (
            'connect',
            'disconnect',
            'new',
            'destroy',
        )

        for name, tooltip in zip(self._action_names, (
            tr('Connect to existing cluster'),
            tr('Disconnect from cluster'),
            tr('New cluster'),
            tr('Destroy cluster'),
        )):
            self._ui_dict[f'action_{name:s}'] = QAction("", self._mainwindow)
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
            set_event_loop(self._loop)
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return

        try:
            config = Config(os.path.join(get_config_path(), CONFIG_FN))
            self._fsm = Fsm(config = config)
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return

        for name in self._action_names:
            self._ui_dict[f'action_{name:s}'].triggered.connect(self._sync(getattr(self, f'_{name:s}')))

        for name in ('connect', 'new'):
            self._ui_dict[f'action_{name:s}'].setEnabled(True)


    def _sync(self, func: Callable, *args: Any, **kwargs: Any) -> Callable:

        def wrapper():
            create_task(func(*args, **kwargs))

        return wrapper


    async def _connect(self):
        """
        Event
        """

        prefix = 'cluster' # TODO

        if not self._ui_dict[f'action_connect'].isEnabled():
            return

        self._set_color('yellow')
        self._set_enabled(False)

        try:
            await self._fsm.connect(prefix = prefix)
        except ClusterConnected as e:
            msg_warning(e, self._mainwindow)
        except Exception as e:
            msg_critical(e, self._mainwindow)

        self._set_enabled(True)


    async def _disconnect(self):
        """
        Event
        """

        if not self._ui_dict[f'action_disconnect'].isEnabled():
            return

        self._set_color('red')
        self._set_enabled(False)

        try:
            await self._fsm.disconnect()
        except ClusterDisconnected as e:
            msg_warning(e, self._mainwindow)
        except Exception as e:
            msg_critical(e, self._mainwindow)

        self._set_enabled(True)


    async def _new(self):
        """
        Event
        """

        prefix = 'cluster' # TODO

        if not self._ui_dict[f'action_new'].isEnabled():
            return

        self._set_color('yellow')
        self._set_enabled(False)

        try:
            await self._fsm.new(prefix = prefix)
        except ClusterConnected as e:
            msg_warning(e, self._mainwindow)
        except Exception as e:
            msg_critical(e, self._mainwindow)

        self._set_enabled(True)


    async def _destroy(self):
        """
        Event
        """

        if not self._ui_dict[f'action_destroy'].isEnabled():
            return

        self._set_color('red')
        self._set_enabled(False)

        try:
            await self._fsm.destroy()
        except ClusterDisconnected as e:
            msg_warning(e, self._mainwindow)
            return
        except Exception as e:
            msg_critical(e, self._mainwindow)
            return

        self._set_enabled(True)


    async def _busy_blink(self, wait: float = 0.5):

        assert wait > 0

        setChecked = self._ui_dict['radio_status'].setChecked
        isChecked = self._ui_dict['radio_status'].isChecked

        try:
            while await sleep(wait, result = True):
                setChecked(not isChecked())
        except CancelledError:
            pass


    def _set_enabled(self, status: bool):

        if status:

            self._sync(self._set_busy, False)()
            if self._fsm.connected:
                self._ui_dict[f'action_disconnect'].setEnabled(True)
                self._ui_dict[f'action_destroy'].setEnabled(True)
                self._set_color('green')
            else:
                self._ui_dict[f'action_connect'].setEnabled(True)
                self._ui_dict[f'action_new'].setEnabled(True)
                self._set_color('red')

        else:

            self._sync(self._set_busy, True)()
            for name in self._action_names:
                self._ui_dict[f'action_{name:s}'].setEnabled(False)


    async def _set_busy(self, status: bool = True, wait: float = 0.5):

        assert wait > 0

        if status:

            if self._busy_task is None or self._busy_task.done():
                self._busy_task = create_task(self._busy_blink(wait = wait))

        else:

            if self._busy_task is not None and not self._busy_task.done():
                self._busy_task.cancel()
                try:
                    await self._busy_task
                except CancelledError:
                    pass
                self._ui_dict['radio_status'].setChecked(True)


    def _set_color(self, color: str):

        assert len(color) > 0

        self._ui_dict['radio_status'].setStyleSheet(RADIO_COLOR.format(COLOR = color))


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
