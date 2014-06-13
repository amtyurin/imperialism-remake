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

from PySide import QtCore, QtGui

class ClickableWidget(QtGui.QWidget):
    """

    """

    clicked = QtCore.Signal(QtGui.QMouseEvent)

    def __init__(self, *args, **kwargs):
        """

        """
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        """

        """
        self.clicked.emit(event)

class ExtendedGraphicsPixmapItem(QtGui.QGraphicsPixmapItem, QtCore.QObject):

    entered = QtCore.Signal()
    left = QtCore.Signal()
    clicked = QtCore.Signal()

    def __init__(self, pixmap):
        QtGui.QGraphicsPixmapItem.__init__(self, pixmap)
        QtCore.QObject.__init__(self)
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)

    def hoverEnterEvent(self, event):
        self.entered.emit()

    def hoverLeaveEvent(self, event):
        self.left.emit()

    def mousePressEvent(self, event):
        self.clicked.emit()

Notification_Default_Style = 'border: 1px solid black; padding: 5px 10px 5px 10px; background-color: rgba(128, 128, 128, 128); color: white;'

def show_notification(parent, text, style=Notification_Default_Style, fade_duration=2000, stay_duration=2000, positioner=None, callback=None):
    """
        border_style example: "border: 1px solid black"
        Please only use a color that is fully opaque (alpha = 255) for bg_color, otherwise a black background will appear.
    """
    # create a clickable widget as standalone window and without a frame
    widget = ClickableWidget(parent, QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
    # connect the click event with closing of the widget and optional the callback action
    widget.clicked.connect(widget.close)
    if callback:
        widget.clicked.connect(callback)

    # widget must be translucent, otherwise when setting semi-transparent background colors
    widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    # create a label and set the text
    label = QtGui.QLabel(widget)
    label.setText(text)

    # set style (border, padding, background color, text color
    label.setStyleSheet(style)

    # we need to manually tell the widget that it should be exactly as big as the label it contains
    widget.resize(label.sizeHint())

    # fade in animation
    widget.fade_in = QtCore.QPropertyAnimation(widget, 'windowOpacity')
    widget.fade_in.setDuration(fade_duration)
    widget.fade_in.setStartValue(0)
    widget.fade_in.setEndValue(1)

    # fading out and waiting for fading out makes only sense if a positive stay_duration has been given
    if stay_duration:

        # fade out animation
        widget.fade_out = QtCore.QPropertyAnimation(widget, 'windowOpacity')
        widget.fade_out.setDuration(fade_duration)
        widget.fade_out.setStartValue(1)
        widget.fade_out.setEndValue(0)
        widget.fade_out.finished.connect(widget.close)

        # timer for fading out animation
        widget.timer = QtCore.QTimer()
        widget.timer.setSingleShot(True)
        widget.timer.setInterval(stay_duration)
        widget.timer.timeout.connect(widget.fade_out.start)

        # start the timer as soon as the fading in animation has finished
        widget.fade_in.finished.connect(widget.timer.start)

    # if given, position
    if parent and positioner:
        position = positioner.calculate(parent.size(), widget.size())
        widget.move(position)

    # to avoid short blinking show transparent and start animation
    widget.setWindowOpacity(0)
    widget.show()
    widget.fade_in.start()

class Relative_Positioner():

    def __init__(self, x=(0, 0, 0), y=(0, 0, 0)):
        self.x = x
        self.y = y

    def south(self, gap):
        self.y = (1, -1, -gap)
        return self

    def north(self, gap):
        self.y = (0, 0, gap)
        return self

    def west(self, gap):
        self.x = (0, 0, gap)
        return self

    def east(self, gap):
        self.x = (1, -1, -gap)
        return self

    def centerH(self):
        self.x = (0.5, -0.5, 0)
        return self

    def centerV(self):
        self.y = (0.5, -0.5, 0)
        return self


    def calculate(self, parent_size, own_size):
        pos_x = self.x[0] * parent_size.width() + self.x[1] * own_size.width() + self.x[2]
        pos_y = self.y[0] * parent_size.height() + self.y[1] * own_size.height() + self.y[2]
        return QtCore.QPoint(pos_x, pos_y)

class FadeAnimation():

    def __init__(self, graphics_item, duration):

        # create opacity effect
        self.effect = QtGui.QGraphicsOpacityEffect()
        self.effect.setOpacity(0)
        graphics_item.setGraphicsEffect(self.effect)

        # create animation
        self.animation = QtCore.QPropertyAnimation(self.effect, 'opacity')
        self.animation.setDuration(duration)  # in ms
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)

    def fade_in(self):
        self.animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self.animation.start()

    def fade_out(self):
        self.animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self.animation.start()

class GraphicsItemSet():
    """
        A set (internally a list because a list might be less overhead) of QGraphicsItem elements.
        Some collective actions are possible like setting a Z-value to each of them.
    """

    def __init__(self):
        self.content = []

    def add_item(self, item):
        """
            item -- QGraphicsItem
        """
        if not isinstance(item, QtGui.QGraphicsItem):
            raise RuntimeError('Expected instance of QGraphicsItem!')
        self.content.append(item)

    def set_level(self, level):
        """

        """
        for item in self.content:
            item.setZValue(level)

class ZStackingManager():
    """

    """

    def __init__(self):
        self.floors = []

    def new_floor(self, floor=None, above=True):
        """

        """
        # if a floor is given, it should exist
        if floor and floor not in self.floors:
            raise RuntimeError('Specified floor unknown!')
        if floor:
            # insert above or below the given floor
            insert_position = self.floors.index(floor) + (1 if above else 0)
        else:
            # insert at the end or the beginning of the floors
            insert_position = len(self.floors) if above else 0
        # create new floor, insert in list and return it
        new_floor = GraphicsItemSet()
        self.floors.insert(insert_position, new_floor)
        return new_floor


    def stack(self):
        """

        """
        for z in range(0, len(self.floors)):
            self.floors[z].set_level(z)


class Dialog(QtGui.QWidget):

    def __init__(self, parent, title=None, icon=None, delete_on_close=False, modal=False, style=None, close_callback=None):
        super().__init__(parent, QtCore.Qt.Dialog)
        # no context help button in the title bar (Qt.Dialog has it by default)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        if title:
            self.setWindowTitle(title)
        if icon:
            self.setWindowIcon(icon)
        if delete_on_close:
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        if modal:
            self.setWindowModality(QtCore.Qt.WindowModal) # default is non-modal
        if style:
            id = 'dialog'
            self.setObjectName(id)
            self.setAttribute(QtCore.Qt.WA_StyledBackground) # in case
            style = '#{}{{{}}}'.format(id, style) # escaping the {} by doubling {{}}
            self.setStyleSheet(style)

        self.close_callback = close_callback

    def set_content(self, widget, no_margins=True):
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(widget)
        if no_margins:
            layout.setContentsMargins(0, 0, 0, 0)

    def closeEvent(self, event):
        if self.close_callback and not self.close_callback(self):
            event.ignore()