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

from PyQt5 import QtWidgets, QtGui

from imperialism_remake.base import constants


#TODO may be we need to use layouts?

def put_pixmap_in_tile_center(scene: QtWidgets.QGraphicsScene, pixmap: QtGui.QPixmap, row, column, z_value):
    x = (row + 0.5) * constants.TILE_SIZE - pixmap.width() / 2
    y = (column + 0.5) * constants.TILE_SIZE - pixmap.height() / 2
    item = scene.addPixmap(pixmap)
    item.setOffset(x, y)
    item.setZValue(z_value)

def put_label_in_tile_center(scene: QtWidgets.QGraphicsScene, label: QtWidgets.QLabel, row, column, z_value):
    x = (row + 0.5) * constants.TILE_SIZE - label.width() / 2
    y = (column + 0.5) * constants.TILE_SIZE - label.height() / 2
    item = scene.addWidget(label)
    item.setX(x)
    item.setY(y)
    item.setZValue(z_value)
