import sys
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QKeySequence
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtGui import QLinearGradient
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QCursor

# TODO: order of waypoints
#   add button to say that waypoint has been reached and change colors of current and next waypoints
#   figure out how to update the the picture

# TODO: fix draw_gates

def create_action(parent, text, slot=None,
                  shortcut=None, shortcuts=None, shortcut_context=None,
                  icon=None, tooltip=None,
                  checkable=False, checked=False):
    action = QtWidgets.QAction(text, parent)

    # if icon is not None:
    #     action.setIcon(QIcon(':/%s.png' % icon))
    if shortcut is not None:
        action.setShortcut(shortcut)
    if shortcuts is not None:
        action.setShortcuts(shortcuts)
    if shortcut_context is not None:
        action.setShortcutContext(shortcut_context)
    if tooltip is not None:
        action.setToolTip(tooltip)
        action.setStatusTip(tooltip)
    if checkable:
        action.setCheckable(True)
    if checked:
        action.setChecked(True)
    # if slot is not None:
    #     action.triggered.connect(slot)

    return action


class Settings:

    WIDTH = 40
    HEIGHT = 40
    NUM_BLOCKS_X = 25
    NUM_BLOCKS_Y = 25


class QS(QtWidgets.QGraphicsScene):

    count = 0
    gate_coors = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lines = []

        self.draw_grid()
        self.set_opacity(1)
        # self.set_visible(False)
        # self.delete_grid()

    def draw_grid(self):
        width = Settings.NUM_BLOCKS_X * Settings.WIDTH
        height = Settings.NUM_BLOCKS_Y * Settings.HEIGHT
        self.setSceneRect(0, 0, width, height)
        self.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)

        pen = QPen(QColor(0, 0, 0), 1, Qt.SolidLine)

        for x in range(0, Settings.NUM_BLOCKS_X+1):
            xc = x * Settings.WIDTH
            self.lines.append(self.addLine(xc, 0, xc, height, pen))

        for y in range(0, Settings.NUM_BLOCKS_Y+1):
            yc = y * Settings.HEIGHT
            self.lines.append(self.addLine(0, yc, width, yc, pen))

    def set_visible(self, visible=True):
        for line in self.lines:
            line.setVisible(visible)

    def delete_grid(self):
        for line in self.lines:
            self.removeItem(line)
        del self.lines[:]

    def set_opacity(self, opacity):
        for line in self.lines:
            line.setOpacity(opacity)

    def draw_boat(self, x, y):
        # width and height of the boat
        boat_w = Settings.WIDTH * 0.75
        boat_h = Settings.HEIGHT * 0.75

        # create boat
        boat = QRectF(x * Settings.WIDTH, y * Settings.HEIGHT, boat_w, boat_h)

        # set gradient
        gradient = QLinearGradient(boat.topLeft(), boat.bottomRight())
        gradient.setColorAt(1, QColor(50, 175, 255, 150))
        gradient.setColorAt(0, QColor(0, 50, 200, 100))

        # add boat
        self.addEllipse(boat, Qt.black, gradient)

    def draw_gates(self, y, x):

        # TODO: take coordinates and put them into global var in a tuple with id
        #   then check to see if the id is less than count --> green

        gate_d = Settings.WIDTH * 0.2  # diameter of gates
        aoe_d = Settings.WIDTH * 3  # diameter of gate_AOE

        # create and add gates
        gate_x = x * Settings.WIDTH - gate_d / 2
        gate_y = y * Settings.HEIGHT - gate_d / 2
        gate = QRectF(gate_x, gate_y, gate_d, gate_d)
        self.addEllipse(gate, Qt.black, QColor(255, 0, 0, 255))

        # create and add gate_AOE
        aoe_x = x * Settings.WIDTH - aoe_d / 2
        aoe_y = y * Settings.HEIGHT - aoe_d / 2
        aoe = QRectF(aoe_x, aoe_y, aoe_d, aoe_d)
        print(aoe.getCoords())
        self.addEllipse(aoe, Qt.black, QColor(0, 255, 0, 25))

    def draw_button(self):
        button_next = QPushButton("            Waypoint reached")
        button_next.clicked.connect(self.button_click)
        self.addWidget(button_next)
        button_count = QPushButton(self.count.__str__())
        self.addWidget(button_count)

    # update active waypoint
    def button_click(self):
        # TODO: change current waypoint to green and make the next waypoint red
        print("waypoint reached")
        self.count = self.count + 1

class QV(QtWidgets.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_menu = QMenu(self)
        self.create_actions()

    def create_actions(self):
        act = create_action(self.view_menu, "Zoom in",
                            slot=self.on_zoom_in,
                            shortcut=QKeySequence("+"), shortcut_context=Qt.WidgetShortcut)
        self.view_menu.addAction(act)

        act = create_action(self.view_menu, "Zoom out",
                            slot=self.on_zoom_out,
                            shortcut=QKeySequence("-"), shortcut_context=Qt.WidgetShortcut)
        self.view_menu.addAction(act)
        self.addActions(self.view_menu.actions())

    def on_zoom_in(self):
        if not self.scene():
            return
        self.scale(1.5, 1.5)

    def on_zoom_out(self):
        if not self.scene():
            return
        self.scale(1.0 / 1.5, 1.0 / 1.5)

    def drawBackground(self, painter, rect):
        gr = rect.toRect()
        start_x = gr.left() + Settings.WIDTH - (gr.left() % Settings.WIDTH)
        start_y = gr.top() + Settings.HEIGHT - (gr.top() % Settings.HEIGHT)
        painter.save()
        painter.setPen(QtGui.QColor(60, 70, 80).lighter(90))
        painter.setOpacity(0.7)

        for x in range(start_x, gr.right(), Settings.WIDTH):
            painter.drawLine(x, gr.top(), x, gr.bottom())
        for y in range(start_y, gr.bottom(), Settings.HEIGHT):
            painter.drawLine(gr.left(), y, gr.right(), y)

        painter.restore()
        super().drawBackground(painter, rect)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    a = QS()
    b = QV()

    boat = (7.25, 7.83)
    gates = {
        (5, 3),
        (5, 22),
        (18, 8),
        (8.236, 12.9),
        (23.1345, 17.753)
    }

    a.draw_boat(boat[0], boat[1])
    for (x, y) in gates:
        a.draw_gates(x, y)
    a.draw_button()

    b.setScene(a)
    b.resize(1200, 1200)
    b.show()
    sys.exit(app.exec_())
