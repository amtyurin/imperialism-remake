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
import logging
import uuid

from PyQt5 import QtCore

from imperialism_remake.base import tools
from imperialism_remake.client.common.generic_screen import GenericScreen
from imperialism_remake.client.editor.add_workforce_widget import AddWorkforceWidget
from imperialism_remake.client.editor.change_terrain_resource_widget import ChangeTerrainResourceWidget
from imperialism_remake.client.editor.change_terrain_widget import ChangeTerrainWidget
from imperialism_remake.client.editor.editor_mainmap import EditorMainMap
from imperialism_remake.client.editor.editor_scenario import EditorScenario
from imperialism_remake.client.editor.nation_properties_widget import NationPropertiesWidget
from imperialism_remake.client.editor.new_scenario_widget import NewScenarioWidget
from imperialism_remake.client.editor.province_property_widget import ProvincePropertiesWidget
from imperialism_remake.client.editor.scenario_properties_widget import ScenarioPropertiesWidget
from imperialism_remake.client.editor.set_nation_widget import SetNationWidget
from imperialism_remake.client.graphics.game_dialog import GameDialog
from imperialism_remake.client.workforce.workforce_animated_widget import WorkforceAnimatedWidget
from imperialism_remake.lib import qt
from imperialism_remake.server.models.workforce import Workforce
from imperialism_remake.server.models.workforce_action import WorkforceAction
from imperialism_remake.server.models.workforce_type import WorkforceType
from imperialism_remake.server.workforce.workforce_factory import WorkforceFactory

logger = logging.getLogger(__name__)


class EditorScreen(GenericScreen):
    """
    The screen the contains the whole scenario editor. Is copied into the application main window if the user
    clicks on the editor pixmap in the client main screen.
    """

    def __init__(self, client):
        """
        Create and setup all the elements.
        """
        self.scenario = EditorScenario()

        super().__init__(client, self.scenario, EditorMainMap(self.scenario, None))

        # new, load, save scenario actions
        a = qt.create_action(tools.load_ui_icon('icon.scenario.new.png'), 'Create new scenario', self,
                             self.new_scenario_dialog)
        self._toolbar.addAction(a)
        a = qt.create_action(tools.load_ui_icon('icon.scenario.load.png'), 'Load scenario', self,
                             self.load_scenario_dialog)
        self._toolbar.addAction(a)
        a = qt.create_action(tools.load_ui_icon('icon.scenario.save.png'), 'Save scenario', self,
                             self.save_scenario_dialog)
        self._toolbar.addAction(a)

        # main map
        self.main_map.change_terrain.connect(self.map_change_terrain)
        self.main_map.change_terrain_resource.connect(self.map_change_terrain_resource)
        self.main_map.province_info.connect(self.provinces_dialog)
        self.main_map.nation_info.connect(self.nations_dialog)
        self.main_map.set_nation_event.connect(self.set_nation_dialog)
        self.main_map.add_workforce_event.connect(self.add_workforce_dialog)
        self.main_map.remove_workforce_event.connect(self.remove_workforce_event_impl)

        # edit properties (general, nations, provinces) actions
        a = qt.create_action(tools.load_ui_icon('icon.editor.general.png'), 'Edit general properties', self,
                             self.general_properties_dialog)
        self._toolbar.addAction(a)
        a = qt.create_action(tools.load_ui_icon('icon.editor.nations.png'), 'Edit nations', self, self.nations_dialog)
        self._toolbar.addAction(a)
        a = qt.create_action(tools.load_ui_icon('icon.editor.provinces.png'), 'Edit provinces', self,
                             self.provinces_dialog)
        self._toolbar.addAction(a)

        self._layout.addWidget(self._toolbar, 0, 0, 1, 2)
        self._layout.addWidget(self._mini_map, 1, 0)
        self._layout.addWidget(self.main_map, 1, 1, 2, 1)
        self._layout.addWidget(self._info_panel, 2, 0)
        self._layout.setRowStretch(2, 1)  # the info box will take all vertical space left
        self._layout.setColumnStretch(1, 1)  # the main map will take all horizontal space left

        self._add_help_and_exit_buttons(client)

        self._workforce_widgets = {}

    def new_scenario_dialog(self):
        """
        Shows the dialog for creation of a new scenario dialog and connect the "create new scenario" signal.
        """
        content_widget = NewScenarioWidget()
        content_widget.finished.connect(self.scenario.create)
        dialog = GameDialog(self._client.main_window, content_widget, title='New Scenario',
                            delete_on_close=True, help_callback=self._client.show_help_browser)
        dialog.setFixedSize(QtCore.QSize(600, 400))
        dialog.show()

    def map_change_terrain(self, column, row):
        """
        :param column:
        :param row:
        """
        content_widget = ChangeTerrainWidget(self, column, row)
        dialog = GameDialog(self._client.main_window, content_widget, title='Change terrain',
                            delete_on_close=True, help_callback=self._client.show_help_browser)
        # dialog.setFixedSize(QtCore.QSize(900, 700))
        dialog.show()

    def map_change_terrain_resource(self, column, row):
        """
        :param column:
        :param row:
        """
        content_widget = ChangeTerrainResourceWidget(self, column, row)
        dialog = GameDialog(self._client.main_window, content_widget, title='Change resource',
                            delete_on_close=True, help_callback=self._client.show_help_browser)
        # dialog.setFixedSize(QtCore.QSize(900, 700))
        dialog.show()

    def general_properties_dialog(self):
        """
        Display the modify general properties dialog.
        """
        if not self.scenario.server_scenario:
            return

        content_widget = ScenarioPropertiesWidget(self.scenario)
        dialog = GameDialog(self._client.main_window, content_widget, title='General Properties',
                            delete_on_close=True, help_callback=self._client.show_help_browser,
                            close_callback=content_widget.close_request)
        # TODO derive meaningful size depending on screen size
        dialog.setFixedSize(QtCore.QSize(900, 700))
        dialog.show()

    def add_workforce_dialog(self, row, col):
        if not self.scenario.server_scenario:
            return

        content_widget = AddWorkforceWidget(row, col, self.scenario.server_scenario.get_workforce_settings(),
                                            self.scenario.get_workforce_to_texture_mapper(),
                                            self.create_workforce_widget)
        dialog = GameDialog(self._client.main_window, content_widget, title='Workers', delete_on_close=True,
                            help_callback=self._client.show_help_browser)
        dialog.show()

    def remove_workforce_event_impl(self, workforce):
        self.scenario.server_scenario.get_nation_asset(workforce.get_nation()).delete_workforce(workforce)

        self._workforce_widgets[workforce.get_id()].destroy()
        del self._workforce_widgets[workforce.get_id()]

    def set_nation_dialog(self, row, col, nation, province):
        if not self.scenario.server_scenario:
            return

        content_widget = SetNationWidget(self.scenario, self.main_map, row, col, nation, province)
        dialog = GameDialog(self._client.main_window, content_widget, title='Nations', delete_on_close=True,
                            help_callback=self._client.show_help_browser)
        dialog.setFixedSize(QtCore.QSize(900, 700))
        dialog.show()

    def nations_dialog(self, nation=None):
        """
        Show the modify nations dialog.
        """
        if not self.scenario.server_scenario:
            return

        content_widget = NationPropertiesWidget(self.scenario, self.main_map, nation)
        dialog = GameDialog(self._client.main_window, content_widget, title='Nations', delete_on_close=True,
                            help_callback=self._client.show_help_browser)
        dialog.setFixedSize(QtCore.QSize(900, 700))
        dialog.show()

    def provinces_dialog(self, province=None):
        """
            Display the modify provinces dialog.
        """
        if not self.scenario.server_scenario:
            return

        content_widget = ProvincePropertiesWidget(self.scenario, province)
        dialog = GameDialog(self._client.main_window, content_widget, title='Provinces', delete_on_close=True,
                            help_callback=self._client.show_help_browser)
        dialog.setFixedSize(QtCore.QSize(900, 700))
        dialog.show()

    def create_workforce_widget(self, row, col, workforce_type):
        if workforce_type not in WorkforceType:
            logger.warning(f"Wrong workforce type: {workforce_type}")
            return

        selected_nation = self.scenario.server_scenario.nation_at(row, col)

        workforce_primitive = Workforce(uuid.uuid4(), row, col, selected_nation, workforce_type)
        workforce = WorkforceFactory.create_new_workforce(self.scenario.server_scenario,
                                                          None,
                                                          workforce_primitive)
        if not workforce:
            logger.warning(f"Was not able to create workforce type: {workforce_type}")
            return

        workforce_widget = WorkforceAnimatedWidget(self.main_map, self._info_panel, workforce)
        workforce_widget.plan_action(row, col, WorkforceAction.EDITOR)

        self._workforce_widgets[workforce_widget.get_workforce().get_id()] = workforce_widget

        self.scenario.server_scenario.get_nation_asset(selected_nation).add_or_update_workforce(workforce_primitive)

