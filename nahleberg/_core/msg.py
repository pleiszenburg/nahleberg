# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    nahleberg/_core/msg.py: UI messages

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

import traceback
from typing import Union

from PyQt5.Qt import QWidget
from PyQt5.QtWidgets import QMessageBox

from typeguard import typechecked

from .util import translation as tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
def msg_critical(exception: Exception, widget: Union[QWidget, None] = None):

    _msg('critical', tr('Critical error'), exception, widget)


@typechecked
def msg_warning(exception: Exception, widget: Union[QWidget, None] = None):

    _msg('warning', tr('Warning'), exception, widget)


@typechecked
def _msg(msg_type, msg_title, exception: Exception, widget: Union[QWidget, None] = None):

    if len(exception.args) == 0:
        msg = tr('Internal error. No description can be provided. Please file a bug!')
    else:
        msg = str(exception.args[0])

    msg += '\n\n---------------------------\n\n' + traceback.format_exc()

    getattr(QMessageBox, msg_type)(
        widget,
        msg_title,
        msg,
        QMessageBox.Ok
        )
