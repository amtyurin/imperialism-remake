# Imperialism remake
# Copyright (C) 2020 amtyurin
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
from imperialism_remake.server.models.workforce import Workforce


class TurnPlanned:
    def __init__(self, nation):
        self._workforces = {}
        self._nation = nation

    def add_workforce(self, workforce: Workforce) -> None:
        self._workforces[workforce.get_id()] = workforce

    def remove_workforce(self, workforce: Workforce) -> None:
        del self._workforces[workforce.get_id()]

    def get_workforces(self) -> {}:
        return self._workforces

    def get_nation(self):
        return self._nation
