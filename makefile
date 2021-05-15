# NAHLEBERG
# QGIS vs. HPC
# https://github.com/pleiszenburg/nahleberg
#
#     makefile: Project makefile
#
#     Copyright (C) 2021 Sebastian M. Ernst <ernst@pleiszenburg.de>
#
# <LICENSE_BLOCK>
# The contents of this file are subject to the GNU General Public License
# Version 2 ("GPL" or "License"). You may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# https://github.com/pleiszenburg/nahleberg/blob/master/LICENSE
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
# specific language governing rights and limitations under the License.
# </LICENSE_BLOCK>


plugin = nahleberg

release:
	make clean
	mkdir -p release/$(plugin)
	cp --parents -a $$(git ls-tree -r $$(git rev-parse --abbrev-ref HEAD) --name-only) release/$(plugin)/
	cd release/; zip -r $(plugin).zip $(plugin); gpg --detach-sign -a $(plugin).zip

clean:
	-rm -r release
	find nahleberg/ -name '*.pyc' -exec rm -f {} +
	find nahleberg/ -name '*.pyo' -exec rm -f {} +
	find nahleberg/ -name '*~' -exec rm -f {} +
	find ./ -name '__pycache__' -exec rm -fr {} +

translate:
	python3 -c "import makefile; makefile.translate()"
