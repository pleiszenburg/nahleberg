# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    nahleberg/_core/i18n.py: i18n support

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
from typing import Tuple

from PyQt5.QtCore import (
    QCoreApplication,
    QSettings,
    QTranslator,
)
from PyQt5.QtWidgets import QApplication

from typeguard import typechecked

from .error import TranslationError

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
def setupTranslation(translationsPath: str) -> Tuple[QTranslator, str]:
    """
    Setup translation system for current plugin.
    TODO: add support for regions (e.g. English for US and UK)
    """

    userLocale = str(QSettings().value('locale/userLocale'))
    if '_' in userLocale:
        language, _ = userLocale.split('_') # language_region
    else:
        language = userLocale

    try:  # Try current language first
        localePath = _getTranslationPath(translationsPath, language)
    except:  # Fall back to English
        try:
            localePath = _getTranslationPath(translationsPath, 'en')
        except:
            return None, None

    translator = QTranslator()
    translator.load(localePath)
    QCoreApplication.installTranslator(translator)

    return translator, localePath


@typechecked
def _getTranslationPath(translationsPath: str, language: str) -> str:

    outPath = os.path.join(
        translationsPath, f'nahleberg_{language:s}.qm'
    )

    if not os.path.exists(outPath):
        raise TranslationError(f'Translation not found: {outPath:s}')

    return outPath


@typechecked
def translate(key: str, context: str = 'global') -> str:
    """
    http://pyqt.sourceforge.net/Docs/PyQt5/i18n.html#differences-between-pyqt5-and-qt
    """

    return QApplication.translate(context, key)
