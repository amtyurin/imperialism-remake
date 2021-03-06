# Imperialism remake
# Copyright (C) 2015-16 Trilarion
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
The main game screen.
"""
import logging
import uuid

from PyQt5 import QtGui, QtCore

from imperialism_remake.base import constants, tools
from imperialism_remake.client.common.generic_screen import GenericScreen
from imperialism_remake.client.common.main_map import MainMap
from imperialism_remake.client.game.game_scenario import GameScenario
from imperialism_remake.client.game.game_selected_object import GameSelectedObject
from imperialism_remake.client.game.order_buttons_widget import OrderButtonsWidget
from imperialism_remake.client.game.turn_end_widget import TurnEndWidget
from imperialism_remake.client.game.turn_manager import TurnManager
from imperialism_remake.client.workforce.workforce_animated_widget import WorkforceAnimatedWidget
from imperialism_remake.lib import qt
from imperialism_remake.server.models.turn_result import TurnResult
from imperialism_remake.server.models.workforce import Workforce
from imperialism_remake.server.models.workforce_action import WorkforceAction
from imperialism_remake.server.models.workforce_type import WorkforceType
from imperialism_remake.server.workforce.workforce_factory import WorkforceFactory

logger = logging.getLogger(__name__)


class GameMainScreen(GenericScreen):
    """
        The whole screen (layout of single elements and interactions.
    """

    def __init__(self, client, server_base_scenario, selected_nation):
        logger.debug('__init__ server_base_scenario:%s, selected_nation:%s', server_base_scenario, selected_nation)

        self._selected_nation = selected_nation
        self.scenario = GameScenario()

        self._main_map = MainMap(self.scenario, selected_nation)

        super().__init__(client, self.scenario, self._main_map)
        self._layout.addWidget(self._toolbar, 0, 0, 1, 2)
        self._layout.addWidget(self._mini_map, 1, 0)

        self.scenario.init(server_base_scenario)

        self._selected_object = GameSelectedObject(self._info_panel)

        self._default_cursor = self.main_map.viewport().cursor()

        self._main_map.mouse_press_event.connect(self._main_map_mouse_press_event)
        self._main_map.mouse_move_event.connect(self._main_map_mouse_move_event)

        self._turn_manager = TurnManager(self.scenario, selected_nation)
        self._turn_manager.event_turn_completed.connect(self._event_turn_completed)

        turn_end_widget = TurnEndWidget(self._turn_manager)
        order_buttons_widget = OrderButtonsWidget(self.scenario, client)

        self._layout.addWidget(order_buttons_widget, 2, 0)
        self._layout.addWidget(self._info_panel, 3, 0)
        self._layout.addWidget(turn_end_widget, 4, 0)
        self._layout.addWidget(self.main_map, 1, 1, 4, 1)
        self._layout.setRowStretch(3, 1)  # the info box will take all vertical space left
        self._layout.setColumnStretch(1, 1)  # the main map will take all horizontal space left

        self._workforce_widgets = {}

        # !!! TODO this is just to test, remove me a little bit later!!!
        self._create_workforce_widget(13, 29, WorkforceType.ENGINEER)
        self._create_workforce_widget(11, 27, WorkforceType.PROSPECTOR)
        self._create_workforce_widget(12, 30, WorkforceType.FARMER)
        self._create_workforce_widget(15, 29, WorkforceType.FORESTER)
        self._create_workforce_widget(14, 29, WorkforceType.MINER)
        self._create_workforce_widget(13, 28, WorkforceType.RANCHER)
        # !!! TODO remove above

        a = qt.create_action(tools.load_ui_icon('icon.scenario.load.png'), 'Load scenario', self,
                             self.load_scenario_dialog)
        self._toolbar.addAction(a)
        a = qt.create_action(tools.load_ui_icon('icon.scenario.save.png'), 'Save scenario', self,
                             self.save_scenario_dialog)
        self._toolbar.addAction(a)

        self._add_help_and_exit_buttons(client)

        self._add_workforces()

        self._info_panel.refresh_nation_asset_info()

        self._selected_object.set_workforce_widgets_getter(lambda: self._workforce_widgets)

        logger.debug('__init__ finished')

    def _create_workforce_widget(self, row, col, workforce_type):
        workforce_primitive = Workforce(uuid.uuid4(), row, col, self._selected_nation, workforce_type)
        workforce = WorkforceFactory.create_new_workforce(self.scenario.server_scenario,
                                                          self._turn_manager.get_turn_planned(),
                                                          workforce_primitive)
        workforce_widget = WorkforceAnimatedWidget(self._main_map, self._info_panel, workforce)
        workforce_widget.plan_action(row, col, WorkforceAction.STAND)

        workforce_widget.event_widget_selected.connect(self._selected_widget_object_event)
        workforce_widget.event_widget_deselected.connect(self._deselected_widget_object_event)

        self._workforce_widgets[workforce_widget.get_workforce().get_id()] = workforce_widget

    def _main_map_mouse_press_event(self, main_map, event: QtGui.QMouseEvent) -> None:
        scene_position = main_map.mapToScene(event.pos()) / constants.TILE_SIZE
        column, row = self.scenario.server_scenario.map_position(scene_position.x(), scene_position.y())

        logger.debug("_main_map_mouse_press_event x:%s, y:%s, button:%s, row:%s, col:%s", event.x(), event.y(),
                     event.button(), row,
                     column)

        if event.button() == QtCore.Qt.LeftButton:
            logger.debug("_main_map_mouse_press_event reset selected object and select other if it is there")
            self._selected_object.deselect_widget_object_rather_than(row, column)

        elif event.button() == QtCore.Qt.RightButton:
            logger.debug("_main_map_mouse_press_event do duty action or nothing")

            # TODO if this row and col is busy with other object -> do nothing
            # if scenario has object(workforce) in row, col for this x, y
            # then do nothing
            self._selected_object.do_action(row, column)

    def _main_map_mouse_move_event(self, column: int, row: int) -> None:
        self._update_cursor(row, column)

    def _update_cursor(self, row: int, column: int) -> None:
        if self._selected_object.is_selected():
            cursor = self._selected_object.get_workforce_to_action_cursor(row, column)

            if cursor is None:
                self._set_default_cursor()
            elif cursor != self.main_map.viewport().cursor():
                logger.debug("_update_cursor cursor changed cur_curs:%s, cursor:%s, row:%s, column:%s",
                             hex(id(self.main_map.viewport().cursor())), hex(id(cursor)), row, column)
                self.main_map.viewport().setCursor(cursor)
                # TODO should we change cursor when pointing workforce?
                # self._selected_object._selected_widget_object.setCursor(cursor)
        elif self._default_cursor != self.main_map.viewport().cursor():
            self._set_default_cursor()

    def _set_default_cursor(self):
        logger.debug("_set_default_cursor set default cursor")
        self.main_map.viewport().setCursor(self._default_cursor)

    def _selected_widget_object_event(self, widget_object: WorkforceAnimatedWidget) -> None:
        self._set_default_cursor()

        self._selected_object.select_widget_object(widget_object)

        row, col = widget_object.get_workforce().get_current_position()
        logger.debug("_selected_widget_object_event object type:%s, row:%s, col :%s",
                     widget_object.get_workforce().get_type(), row, col)

    def _deselected_widget_object_event(self, widget_object: WorkforceAnimatedWidget) -> None:
        logger.debug("_deselected_widget_object_event object type:%s", widget_object.get_workforce().get_type())
        self._set_default_cursor()

    def _event_turn_completed(self, turn_result: TurnResult) -> None:
        logger.debug("_event_turn_completed")

        for k, wf_widget in self._workforce_widgets.items():
            wf_widget.destroy()
            del wf_widget
        self._workforce_widgets = {}

        self.scenario.server_scenario.update_scenario_base(turn_result.get_server_scenario_base())

        self._add_workforces()

        self._main_map.partial_redraw()

        self._info_panel.refresh_nation_asset_info()

    def _add_workforces(self):
        for nation in self.scenario.server_scenario.nations():
            for k, workforce in self.scenario.server_scenario.get_nation_asset(nation).get_workforces().items():
                new_workforce = WorkforceFactory.create_new_workforce(self.scenario.server_scenario,
                                                                      self._turn_manager.get_turn_planned(),
                                                                      workforce)
                r, c = new_workforce.get_current_position()
                new_workforce_widget = WorkforceAnimatedWidget(self._main_map, self._info_panel, new_workforce)
                new_workforce_widget.plan_action(r, c, new_workforce.get_action())

                new_workforce_widget.event_widget_selected.connect(self._selected_widget_object_event)
                new_workforce_widget.event_widget_deselected.connect(self._deselected_widget_object_event)

                self._workforce_widgets[new_workforce_widget.get_workforce().get_id()] = new_workforce_widget

    def deleteLater(self) -> None:
        logger.debug('deleteLater')

        self._turn_manager.destroy()
        super().deleteLater()
