# -*- coding: utf-8 -*-

"""

NAHLEBERG
QGIS vs. HPC
https://github.com/pleiszenburg/nahleberg

    makefile.py: Helper routines for building and distributing the plugin

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
import subprocess

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TRANSLATION_FLD = 'i18n'

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def translate():

    tmpProFileName = 'nahleberg.pro'

    _writeProjectFile(tmpProFileName)

    _runCommand(['pylupdate5', '-noobsolete', '-verbose', tmpProFileName])
    _runCommand(['lrelease-qt5', tmpProFileName])

    os.remove(tmpProFileName)


def _genPythonFiles():

    for path, _, filesList in os.walk('nahleberg'):
        for fileName in filesList:
            if not fileName.endswith('.py'):
                continue
            pythonFilePath = os.path.join(path, fileName)
            if not os.path.isfile(pythonFilePath):
                continue
            yield pythonFilePath


def _genTranslationFiles():

    for fileName in os.listdir(TRANSLATION_FLD):
        if not fileName.endswith('.ts'):
            continue
        translationPath = os.path.join(TRANSLATION_FLD, fileName)
        if not os.path.isfile(translationPath):
            continue
        yield translationPath


def _runCommand(commandList):

    proc = subprocess.Popen(
        commandList, stdout = subprocess.PIPE, stderr = subprocess.PIPE
        )
    outs, errs = proc.communicate()
    print(outs.decode('utf-8'), errs.decode('utf-8'))


def _writeProjectFile(fn):

    seperator = ' \\\n\t'

    with open(fn, 'w', encoding = 'utf-8') as f:
        f.write(
            'SOURCES = %s\n\nTRANSLATIONS = %s\n' % (
                seperator.join(list(_genPythonFiles())),
                seperator.join(list(_genTranslationFiles()))
                )
            )
