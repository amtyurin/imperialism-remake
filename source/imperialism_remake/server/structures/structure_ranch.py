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
from imperialism_remake.server.models.structure import Structure
from imperialism_remake.server.server_scenario import ServerScenario
from imperialism_remake.server.structures.structure_common import StructureCommon


class StructureRanch(StructureCommon):
    def __init__(self, server_scenario: ServerScenario, structure: Structure):
        super().__init__(server_scenario, structure)

    def can_build(self, row, column) -> bool:
        can_build = super().can_build(row, column)
        if not can_build:
            return False

        # TODO check for tech

        return True

    def can_upgrade(self) -> bool:
        if not super().can_upgrade():
            return False

        # TODO check for technology

    def upgrade(self) -> None:
        if self.can_upgrade():
            self.upgrade()
