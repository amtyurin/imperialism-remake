# Imperialism remake
# Copyright (C) 2014 Trilarion
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""
    Generates the default options.
"""

import os
os.chdir('..')

import constants as c

rules = {}

terrain_names = {
    '0': 'Sea',
    '1': 'Plain',
    '2': 'Hills',
    '3': 'Mountains',
    '4': 'Tundra',
    '5': 'Swamp',
    '6': 'Desert'
}
rules['terrain.names'] = terrain_names

# save
import tools as t
file = c.Scenario_Ruleset_Standard_File
print('write to {}'.format(file))
t.write_json(file, rules)