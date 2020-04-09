import sys

import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

import connect4

class QLabel_Kai(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, j, parent=None):
        super().__init__(parent)
        self.j = j
        self.parent = parent
        self.clicked.connect(self.label_clicked)

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def label_clicked(self):
        if connect4.check_move(self.parent.game, self.j):
            self.parent.game.mat = connect4.apply_move(self.parent.game, self.j)

            for i in range(self.parent.game.rows):
                for j in range(self.parent.game.cols):
                    label = self.parent.labels[i, j]
                    if self.parent.game.mat[i, j] == 1:
                        label.setPixmap(self.parent.RED_PIXMAP)
                    elif self.parent.game.mat[i, j] == 2:
                        label.setPixmap(self.parent.YELLOW_PIXMAP)

            if connect4.check_victory(self.parent.game):
                msgBox = QtWidgets.QMessageBox(self.parent)
                msgBox.setIcon(QtWidgets.QMessageBox.Information)
                msgBox.setText('Victory for player' + str(self.parent.game.turn))
                msgBox.setWindowTitle('Victory for player' + str(self.parent.game.turn))
                msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msgBox.exec()
                exit()
            self.parent.game.turn ^= 3  # toggles between 1 and 2



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.game = kwargs.get('game')
        self.labels = np.empty((self.game.rows, self.game.cols), dtype=object)
        self.win = QtWidgets.QWidget(self)
        self.setCentralWidget(self.win)

        self.win.setAutoFillBackground(True)
        palette = self.win.palette()
        palette.setColor(self.win.backgroundRole(), QtCore.Qt.blue)
        self.win.setPalette(palette)

        self.setWindowTitle('QF205 - Connect 4')
        self.setGeometry(50, 50, self.game.cols * 50, self.game.rows * 50)
        self.setWindowIcon(QtGui.QIcon('empty.png'))

        self.EMPTY_PIXMAP = QtGui.QPixmap('empty.png')
        self.RED_PIXMAP = QtGui.QPixmap('red.png')
        self.YELLOW_PIXMAP = QtGui.QPixmap('yellow.png')
        self.render()


    def render(self):
        grid = QtWidgets.QGridLayout(self.win)
        grid.setContentsMargins(0, 0, 0, 0)
        for i in range(self.game.rows):
            for j in range(self.game.cols):
                label = QLabel_Kai(j, self)
                label.setPixmap(self.EMPTY_PIXMAP)
                label.resize(self.EMPTY_PIXMAP.width(), self.EMPTY_PIXMAP.height())
                grid.addWidget(label, i, j)
                self.labels[i, j] = label


if __name__ == "__main__":
    my_game = connect4.Game()
    my_game.mat = np.zeros((my_game.rows, my_game.cols))

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(game=my_game)
    window.show()
    sys.exit(app.exec_())
