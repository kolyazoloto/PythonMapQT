#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,numpy as np
from PyQt5.QtWidgets import QWidget, QApplication,QVBoxLayout,QHBoxLayout,QGroupBox,QPushButton,QListView,QLineEdit,QTextEdit,QMainWindow
from PyQt5.QtGui import QPainter, QColor,QPen,QStandardItemModel,QStandardItem
from PyQt5.QtCore import QThread, pyqtSignal
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder


class Map(QWidget):

    def __init__(self,array):
        super().__init__()
        self.mapArray = array
        self.totalPath = []         #Глобальный путь
        self.localPath = []
        self.findPathArray = []
        self.pose = [25,25]
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle('Draw MAP')
        self.listModel = QStandardItemModel()

    def mousePressEvent(self, QMouseEvent):
        self.mousePos = QMouseEvent.pos()
        x_mouse = self.mousePos.x()
        y_mouse = self.mousePos.y()

        ############################################
        x = x_mouse / self.rectangleWidth      # Находим нужный кубикя rjординаты
        y = y_mouse / self.rectangleHeight

        x = int(np.floor(x))
        y = int(np.floor(y))

        strItem = str(x)+','+str(y) #Делаем строку
        item = QStandardItem(strItem) # QItem

        self.listModel.appendRow(item)
        self.findPathArray.append([x,y])
        #self.update(x_mouse-self.rectangleWidth,y_mouse-self.rectangleHeight,self.rectangleWidth*2,self.rectangleHeight*2)
        self.update()
        print(self.findPathArray)
    def paintEvent(self, event):

        qp = QPainter()
        qp.begin(self)
        self.drawRectangle(qp)
        qp.end()

    def drawRectangle(self,qp):
        pen = QPen()
        pen.setStyle(1)     #no lines
        qp.setPen(pen)

        array = self.mapArray
        size = self.size()
        self.row_items = len(array[0])   #Длина ряда
        self.colomn_items = len(array)   #Длина колонны
        self.rectangleWidth = (size.width())/self.row_items
        self.rectangleHeight = (size.height())/self.colomn_items
        start = 0
        startPoint = [0,0]


        for k in range(self.colomn_items):
            for i in range(self.row_items):          #Рисуем прямоугольники                if array[k][i] == 0:
                '''if array[k][i] == 1:
                    startPoint[0] += self.rectangleWidth
                    continue   # если 1 сразу прерываем'''
                if array[k][i] == 0:
                    qp.setBrush(QColor(0,0,0))
                    qp.setPen(QColor(0,0,0))
                    qp.drawRect(startPoint[0], startPoint[1], self.rectangleWidth, self.rectangleHeight)
                if array[k][i] > 1:
                    weight = array[k][i]
                    qp.setBrush(QColor(255,255-weight,255-weight))
                    qp.setPen(QColor(255,255-weight,255-weight))
                    qp.drawRect(startPoint[0], startPoint[1], self.rectangleWidth, self.rectangleHeight)
                startPoint[0] += self.rectangleWidth

            startPoint[0] = start               #Обнуляем координату ряда
            startPoint[1] += self.rectangleHeight    #Увеличиваем координату высоты

        ### Отображение из массивов
        for i in self.totalPath:  # Рисуем массив пути
            qp.setBrush(QColor(0, 0, 255))
            qp.setPen(QColor(0, 0, 255))
            qp.drawRect(self.rectangleWidth * i[0], self.rectangleHeight * i[1], self.rectangleWidth,
                        self.rectangleHeight)
        for i in self.findPathArray:  # Рисуем точки
            qp.setBrush(QColor(255, 0, 0))
            qp.setPen(QColor(255, 0, 0))
            qp.drawRect(self.rectangleWidth * i[0], self.rectangleHeight * i[1], self.rectangleWidth,
                        self.rectangleHeight)

        qp.setBrush(QColor(0, 255, 0))  # Отображение точки нахождения
        qp.setPen(QColor(0, 0, 0))
        qp.drawRect(self.rectangleWidth * self.pose[0], self.rectangleHeight * self.pose[1], self.rectangleWidth,
                    self.rectangleHeight)

class MapWidget(QWidget):

    def __init__(self,massive):
        super().__init__()
        self.screenArray = massive.copy() # Используем для отображения
        self.map = Map(self.screenArray)
        self.initUI()
    def initUI(self):
        self.setGeometry(300,300,1300,1000)
        self.poseWID() ################
        self.rightSide()
        self.leftSide()

        hbox = QHBoxLayout()
        hbox.addWidget(self.leftGroupBox,stretch=100)
        hbox.addWidget(self.rightGroupBox,stretch=20)
        print(len(self.map.mapArray))
        print(len(self.map.mapArray[0]))
        self.setLayout(hbox)
        self.show()
        self.posewid.show()  ##########
    def poseWID(self):
        def update_pose():
            y = int(self.pose_x_lineEdit.text())
            x = int(self.pose_y_lineEdit.text())
            recountLength = 10    # В настройки
            prev_pose = self.map.pose
            self.map.pose = [x, y]
            print(self.map.pose)
            print(self.map.totalPath)
            if (x, y) not in self.map.totalPath:    # Если мы не на пути включаем перерасчет
                # включить перерасчет
                ######################
                print("ПЕРЕРАСЧЕТ")
                self.recountPath(self.map.pose,self.map.totalPath[recountLength])  # переделать в возвращение функции
                del(self.map.totalPath[:recountLength])    # удаляем из глобального пути все точки до N
                self.map.totalPath = self.map.localPath + self.map.totalPath
                self.map.localPath.clear()
                ######################'''
            if (x,y) in self.map.totalPath:
                #определяем где мы в пути
                ######################
                print("НА ПУТИ")
                del(self.map.totalPath[:self.map.totalPath.index((x,y))])  # Удаляем все элементы в массиве до нашего
                #self.recountPath(self.map.pose,self.map.totalPath[10])
                ######################'''
            if self.map.pose != prev_pose:
                self.map.update()


        self.posewid = QWidget()
        self.posewid.setGeometry(300,300,300,100)
        self.posewid.setMinimumSize(300,100)
        self.posewid.setMaximumSize(300,100)
        lineedit_wid =  QWidget()
        self.pose = [0,0]
        self.pose_x_lineEdit = QLineEdit(lineedit_wid)
        self.pose_y_lineEdit = QLineEdit(lineedit_wid)

        self.button_apply_pose = QPushButton()
        self.button_apply_pose.setText("Применить")
        self.button_apply_pose.clicked.connect(update_pose)
        hbox = QHBoxLayout()
        hbox.addWidget(self.pose_x_lineEdit)
        hbox.addWidget(self.pose_y_lineEdit)
        lineedit_wid.setLayout(hbox)

        vbox = QVBoxLayout(self.posewid)
        vbox.addWidget(lineedit_wid)
        vbox.addWidget(self.button_apply_pose)

    def rightSide(self):
        #self.buttonRun = QPushButton()
        #self.buttonRun.setText("ПОИХАЛI")
        #self.buttonRun.clicked.connect(pass)
        ##
        self.buttonFindPath = QPushButton()
        self.buttonFindPath.setText("Find path")
        self.buttonFindPath.clicked.connect(self.findPath)
        ##
        self.buttonClearArray = QPushButton()
        self.buttonClearArray.setText("Clear Array")
        self.buttonClearArray.clicked.connect(self.clearPathArrayCallback)
        ##
        self.buttonTestGrad = QPushButton()
        self.buttonTestGrad.setText("TEST GRAD")
        self.buttonTestGrad.clicked.connect(self.makeGradTunnel)
        ##
        self.list = QListView()
        self.list.setModel(self.map.listModel)
        vbox = QVBoxLayout()
        vbox.addWidget(self.list,stretch=50)
        #vbox.addWidget(self.buttonRun, stretch=30)
        vbox.addWidget(self.buttonFindPath,stretch=30)
        vbox.addWidget(self.buttonClearArray,stretch=30)
        vbox.addWidget(self.buttonTestGrad, stretch=50)
        self.rightGroupBox = QGroupBox()
        self.rightGroupBox.setLayout(vbox)
    def leftSide(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.map)
        self.leftGroupBox = QGroupBox()
        self.leftGroupBox.setLayout(vbox)
    def clearPathArrayCallback(self):
        self.map.findPathArray.clear()
        self.map.listModel.clear()
        self.map.totalPath.clear()
        self.map.update()

    def findPath(self):    # Thread
        def updateFindPath(path):
            self.map.listModel.removeRow(0)
            self.map.totalPath.extend(path)
            self.map.update()
        def done():
            print("find path DONE")
        self.findThread = FindPathThread(self.screenArray,self.map.findPathArray,self.map.pose)
        self.findThread.findPathSignal.connect(updateFindPath)
        self.findThread.finished.connect(done)
        self.findThread.start()


    def recountPath(self,start,finish):    # Должна быть в Росе
        grid = Grid(matrix=self.screenArray)  # eto tut koroche delaet kartu
        startPoint = grid.node(start[0], start[1])
        finishPoint = grid.node(finish[0], finish[1])
        finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)
        self.map.localPath, run = finder.find_path(startPoint, finishPoint, grid)
        self.map.update()
    def makeGradTunnel(self): #Thread
        def updateGradTunnel(border,width):
            for i in border:
                self.screenArray[i[0]][i[1]] = width
            self.map.update()
        def done():
            print("Grad done")
        self.gradThread = MakeGradThread(self.screenArray,self.map.totalPath)
        self.gradThread.makeGradSignal.connect(updateGradTunnel)
        self.gradThread.finished.connect(done)
        self.gradThread.start()

class FindPathThread(QThread):
    findPathSignal = pyqtSignal(list)
    def __init__(self,screenArray,findPathArray,pose):
        super().__init__()
        self.screenArray = screenArray
        self.findPathArray = findPathArray
        self.pose = pose
    def __del__(self):
        self.wait()

    def _findPath(self,startPose,endPose):
        grid = Grid(matrix=self.screenArray)  # eto tut koroche delaet kartu
        startPoint = grid.node(startPose[0], startPose[1])
        finishPoint = grid.node(endPose[0], endPose[1])
        finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)
        path, run = finder.find_path(startPoint, finishPoint, grid)
        return path, run

    def run(self):
        if len(self.findPathArray) >= 1:
            self.findPathArray.insert(0, self.pose)
            while len(self.findPathArray) > 1:
                path, run = self._findPath(self.findPathArray[0],self.findPathArray[1])
                self.findPathSignal.emit(path)
                del(self.findPathArray[0])

class MakeGradThread(QThread):
    makeGradSignal = pyqtSignal(list,float)
    def __init__(self,screenArray,totalPath):
        super().__init__()
        self.screenArray = screenArray
        self.totalPath = totalPath
        self.neighbour = [[-1, -1], [0, -1], [1, -1], [-1, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
        self.visitedArray = []
        self.gridArray = totalPath.copy()

    def __del__(self):
        self.wait()

    def _makeGrad(self,weight):
        border = []
        width_len = len(self.screenArray) - 1
        height_len = len(self.screenArray[0]) - 1
        for i in self.gridArray:
            for elem in self.neighbour:
                y = i[0] + elem[0]
                x = i[1] + elem[1]  # все перепутано икс и игрик для машины и человека это разное
                if x < 0 or y < 0 or x > (width_len) or y > (height_len):  # смотрим уходим ли за границу
                    continue
                if self.screenArray[x][y] == 0:  # смотрим препятствия и путь
                    continue
                if [x, y] in self.visitedArray:  # смотрим посещали ли
                    continue
                if [x, y] in self.totalPath:  # смотрим посещали ли
                    continue
                border.append([x, y])
                self.visitedArray.append([x, y])
        self.gridArray.clear()
        self.makeGradSignal.emit(border,weight)
        for i in border:
            self.gridArray.append(i[::-1])  # Нужно развернуть
    def run(self):

        tunnelWidth = 5
        weight = 20
        #weightStep = int((255 - weight) / tunnelWidth)
        weightStep = 30  # В настройки
        # сюда цикл на сколько то фигнь
        for iter in range(tunnelWidth):
            self._makeGrad(weight)
            weight += weightStep



















