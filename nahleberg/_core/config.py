# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    nahleberg/_core/config.py: Configuration

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

import copy
import json
import os
from typing import Any

from qgis.core import QgsApplication

from typeguard import typechecked

from .const import QGIS_CONFIG_FLD
from .error import ConfigFormatError
from .i18n import translate as tr

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
def get_config_path() -> str:

    root_fld = QgsApplication.qgisSettingsDirPath()
    if os.path.exists(root_fld) and not os.path.isdir(root_fld):
        raise ValueError(tr('QGIS settings path does not point to a directory.'))
    if not os.path.exists(root_fld):
        raise ValueError(tr('QGIS settings path does not exist.')) # TODO create?

    root_qgis_fld = os.path.join(root_fld, QGIS_CONFIG_FLD)
    if os.path.exists(root_qgis_fld) and not os.path.isdir(root_qgis_fld):
        raise ValueError(tr('QGIS plugin configuration path exists but is not a directory.'))
    if not os.path.exists(root_qgis_fld):
        os.mkdir(root_qgis_fld)

    return root_qgis_fld


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Config:

    def __init__(self, fn: str):

        self._fn = fn

        if not os.path.exists(fn):
            if not os.path.exists(os.path.dirname(fn)):
                raise ValueError(tr('Parent of "fn" must exists.'))
            if not os.path.isdir(os.path.dirname(fn)):
                raise ValueError(tr('Parent of "fn" must be a directory.'))
            self._data = {}
            self._save()
        else:
            if not os.path.isfile(fn):
                raise ValueError(tr('"fn" must be a file. (config)'))
            with open(fn, 'r', encoding = 'utf-8') as f:
                data = f.read()
            try:
                self._data = json.loads(data)
            except Exception as e:
                raise ConfigFormatError(tr('Config does not contain valid JSON.')) from e
            if not isinstance(self._data, dict):
                raise TypeError(tr('Configuration data must be a dict.'))


    def __getitem__(self, name: str) -> Any:

        if name not in self._data.keys():
            raise KeyError(tr('Unknown configuration field "name".'))

        return copy.deepcopy(self._data[name])


    def __setitem__(self, name: str, value):

        if not self._check_value(value):
            raise TypeError(tr('"value" contains not allowed types.'))

        self._data[name] = value
        self._save()


    def get(self, name: str, default: Any) -> Any:

        try:
            return self[name]
        except KeyError:
            return default


    @classmethod
    def _check_value(cls, value: Any) -> bool:

        if type(value) not in (int, float, bool, str, list, dict) and value is not None:
            return False

        if isinstance(value, list):
            for item in value:
                if not cls._check_value(item):
                    return False

        if isinstance(value, dict):
            for k, v in value.items():
                if not cls._check_value(k) or not cls._check_value(v):
                    return False

        return True


    def _save(self):

        backup_fn = None
        if os.path.exists(self._fn):
            backup_fn = f'{self._fn:s}.backup'
            max_attempts = 100
            attempt = 0
            attempt_ok = False
            while attempt < max_attempts:
                backup_fn_numbered = f'{backup_fn:s}{attempt:02d}'
                if not os.path.exists(backup_fn_numbered):
                    attempt_ok = True
                    backup_fn = backup_fn_numbered
                    break
                attempt += 1
            if not attempt_ok:
                raise ValueError(tr('Could not backup old configuration before saving new - too many old backups.'))
            os.rename(self._fn, backup_fn)

        with open(self._fn, 'w', encoding = 'utf-8') as f:
            f.write(json.dumps(self._data, indent = 4, sort_keys = True))

        if backup_fn is not None:
            os.unlink(backup_fn)


    @staticmethod
    def import_config(fn: str) -> Any:

        if not os.path.exists(fn):
            raise ValueError(tr('"fn" must exists.'))
        if not os.path.isfile(fn):
            raise ValueError(tr('"fn" must be a file.'))

        with open(fn, 'r', encoding = 'utf-8') as f:
            raw = f.read()

        try:
            value = json.loads(raw)
        except Exception as e:
            raise ConfigFormatError(tr('"fn" does not contain valid JSON.')) from e

        return value


    @classmethod
    def export_config(cls, fn: str, value: Any):

        if not os.path.exists(os.path.dirname(fn)):
            raise ValueError(tr('Parent of "fn" must exists.'))
        if not os.path.isdir(os.path.dirname(fn)):
            raise ValueError(tr('Parent of "fn" must be a directory.'))
        if not cls._check_value(value):
            raise TypeError(tr('"value" contains not allowed types.'))

        with open(fn, 'w', encoding = 'utf-8') as f:
            f.write(json.dumps(value, indent = 4, sort_keys = True))
