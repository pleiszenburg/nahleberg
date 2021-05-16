# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    nahleberg/_core/fsm.py: Finite state machine

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

from typeguard import typechecked

from .abc import ConfigABC, FsmABC
from .error import ClusterConnected, ClusterDisconnected
from .i18n import translate as tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Fsm(FsmABC):

    def __init__(self, config: ConfigABC):

        self._config = config

        self._dask_client = None
        self._cluster = None


    @property
    def connected(self) -> bool:

        return self._dask_client is not None


    async def connect(self):

        if self.connected:
            raise ClusterConnected(tr('cluster is already connected'))


    async def disconnect(self):

        if not self.connected:
            raise ClusterDisconnected(tr('cluster is already disconnect'))


    async def new(self):

        if self.connected:
            raise ClusterConnected(tr('cluster is already connected - disconnect before creating a new one'))


    async def destroy(self):

        if not self.connected:
            raise ClusterDisconnected(tr('cluster is disconnect - can not destroy'))
