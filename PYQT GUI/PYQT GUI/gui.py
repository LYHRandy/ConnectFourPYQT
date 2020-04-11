import os
import sys

import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic

import connect4

import glob

class QLabel_Kai(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, col, parent=None):
        super().__init__(parent)
        self.col = col
        self.parent = parent
        self.clicked.connect(self.label_clicked)

    def mousePressEvent(self, ev):
        self.clicked.emit()

    def label_clicked(self):
        if self.parent.mode == "player":
            if connect4.check_move(self.parent.game, self.col):
                self.parent.game.mat = connect4.apply_move(self.parent.game, self.col)
        else:
            level_mapping = {"easy":1,"medium":2,"hard":3}
            level = level_mapping[self.parent.mode]

            if self.parent.game.turn == 1:
                if connect4.check_move(self.parent.game, self.col):
                    self.parent.game.mat = connect4.apply_move(self.parent.game, self.col)
                    self.parent.game.turn ^= 3  # toggles between 1 and 2
                    col = connect4.computer_move(self.parent.game,player_move=self.col, level=level)
                    if connect4.check_move(self.parent.game,self.col):
                        self.parent.game.mat = connect4.apply_move(self.parent.game, col,mode=self.parent.mode)
                    self.parent.game.turn ^= 3  # toggles between 1 and 2
                
            
        for i in range(self.parent.game.rows):
            for j in range(self.parent.game.cols):
                label = self.parent.labels[i, j]
                if self.parent.game.mat[i, j] == 1:
                    label.setPixmap(self.parent.RED_PIXMAP)
                elif self.parent.game.mat[i, j] == 2:
                    label.setPixmap(self.parent.YELLOW_PIXMAP)
        
        if connect4.check_victory(self.parent.game,mode=self.parent.mode) == 1:
            msgBox = QtWidgets.QMessageBox(self.parent)
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Victory for Player ' + str(self.parent.game.turn))
            msgBox.setWindowTitle('Victory for Player ' + str(self.parent.game.turn))
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
            exit()
        elif self.parent.mode == "player" and connect4.check_victory(self.parent.game,mode=self.parent.mode) == 2:
            msgBox = QtWidgets.QMessageBox(self.parent)
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Victory for Player ' + str(self.parent.game.turn))
            msgBox.setWindowTitle('Victory for Player ' + str(self.parent.game.turn))
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
            exit()
        elif self.parent.mode != "player" and connect4.check_victory(self.parent.game,mode=self.parent.mode) == 2:
            msgBox = QtWidgets.QMessageBox(self.parent)
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Victory for Computer')
            msgBox.setWindowTitle('Victory for Computer')
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
            exit()

                
                
        self.parent.game.turn ^= 3  # toggles between 1 and 2
        



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.game = kwargs.get('game')
        self.mode = kwargs.get('mode')
        self.labels = np.empty((self.game.rows, self.game.cols), dtype=object)
        self.win = QtWidgets.QWidget(self)
        self.setCentralWidget(self.win)

        self.win.setAutoFillBackground(True)
        palette = self.win.palette()
        palette.setColor(self.win.backgroundRole(), QtCore.Qt.blue)
        self.win.setPalette(palette)

        name_mapping = {"player":"VS Player","easy":"VS AI - Easy","medium":"VS AI - Medium","hard":"VS AI - Hard"}
        self.setWindowTitle('QF205 - Connect4 ({})'.format(name_mapping[self.mode]))
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
                # Everytime game start, we need to render the loaded state
                if self.game.mat[i, j] == 1:
                        label.setPixmap(self.RED_PIXMAP)
                elif self.game.mat[i, j] == 2:
                    label.setPixmap(self.YELLOW_PIXMAP)
                else:
                    label.setPixmap(self.EMPTY_PIXMAP)
                    label.resize(self.EMPTY_PIXMAP.width(), self.EMPTY_PIXMAP.height())
                grid.addWidget(label, i, j)
                self.labels[i, j] = label


class MenuWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.title = "QF205 - Connect4 Menu"
        self.game = kwargs.get('game')
        self.top = 100
        self.left = 100
        self.width = 200
        self.height = 300

        self.playerButton = QtWidgets.QPushButton("VS Player 2", self)
        self.playerButton.move(55, 30)

        self.playerButton.clicked.connect(self.player_window)

        self.easyButton = QtWidgets.QPushButton("AI - Easy", self)
        self.easyButton.move(55, 70)

        self.easyButton.clicked.connect(self.easy_window)

        self.mediumButton = QtWidgets.QPushButton("AI - Medium", self)
        self.mediumButton.move(55, 110)

        self.mediumButton.clicked.connect(self.medium_window)

        self.hardButton = QtWidgets.QPushButton("AI - Hard", self)
        self.hardButton.move(55, 150)

        self.hardButton.clicked.connect(self.hard_window)              # <===

        self.stateButton = QtWidgets.QPushButton("Delete all states", self)
        self.stateButton.move(55, 190)

        self.stateButton.clicked.connect(self.delete_states)              # <===

        self.main_window()

    def main_window(self):
        self.label = QtWidgets.QLabel("Game Mode", self)
        self.label.move(70,5)
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def player_window(self): 
        if os.path.exists("state-player.txt") and os.stat("state-player.txt").st_size != 0:
            with open("state-player.txt", "r") as f:
                list_state = f.read().splitlines()
                my_game.turn = int(list_state.pop())
                list_state = [row.split('|') for row in list_state]
                my_game.mat = np.asarray(list_state,dtype=np.float64)
        else:
            my_game.mat = np.zeros((my_game.rows, my_game.cols))                                            # <===
        self.w = MainWindow(game=self.game,mode="player")
        self.w.show()
        self.hide()

    def easy_window(self):            
        if os.path.exists("state-easy.txt") and os.stat("state-easy.txt").st_size != 0:
            with open("state-easy.txt", "r") as f:
                list_state = f.read().splitlines()
                my_game.turn = int(list_state.pop())
                list_state = [row.split('|') for row in list_state]
                my_game.mat = np.asarray(list_state,dtype=np.float64)
        else:
            my_game.mat = np.zeros((my_game.rows, my_game.cols))                                 # <===
        self.w = MainWindow(game=self.game,mode="easy")
        self.w.show()
        self.hide()

    def medium_window(self):               
        if os.path.exists("state-medium.txt") and os.stat("state-medium.txt").st_size != 0:
            with open("state-medium.txt", "r") as f:
                list_state = f.read().splitlines()
                my_game.turn = int(list_state.pop())
                list_state = [row.split('|') for row in list_state]
                my_game.mat = np.asarray(list_state,dtype=np.float64)
        else:
            my_game.mat = np.zeros((my_game.rows, my_game.cols))                              # <===
        self.w = MainWindow(game=self.game,mode="medium")
        self.w.show()
        self.hide()

    def hard_window(self):              
        if os.path.exists("state-hard.txt") and os.stat("state-hard.txt").st_size != 0:
            with open("state-hard.txt", "r") as f:
                list_state = f.read().splitlines()
                my_game.turn = int(list_state.pop())
                list_state = [row.split('|') for row in list_state]
                my_game.mat = np.asarray(list_state,dtype=np.float64)
        else:
            my_game.mat = np.zeros((my_game.rows, my_game.cols))                               # <===
        self.w = MainWindow(game=self.game,mode="hard")
        self.w.show()
        self.hide()

    def delete_states(self):                                             # <===
        filelist = glob.glob("./*.txt")
        for file in filelist:
            try:
                os.remove(file)
            except:
                continue
        
        msgBox = QtWidgets.QMessageBox(self)
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText('Deleted all states')
        msgBox.setWindowTitle('Delete States')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec()

if __name__ == "__main__":
    my_game = connect4.Game()
    
    # search for state file. If exist and not empty, load the state into game.mat
    # if os.path.exists("state.txt") and os.stat("state.txt").st_size != 0:
    #     with open("state.txt", "r") as f:
    #         list_state = f.read().splitlines()
    #         my_game.turn = int(list_state.pop())
    #         list_state = [row.split('|') for row in list_state]
    #         my_game.mat = np.asarray(list_state,dtype=np.float64)
    # else:
    #     my_game.mat = np.zeros((my_game.rows, my_game.cols))
    #my_game.mat = np.zeros((my_game.rows, my_game.cols))

    app = QtWidgets.QApplication(sys.argv)
    # window = MainWindow(game=my_game)
    window = MenuWindow(game=my_game)
    window.show()
    sys.exit(app.exec_())