#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,numpy as np
from PyQt5.QtWidgets import QWidget, QApplication,QVBoxLayout,QHBoxLayout,QGroupBox,QPushButton,QListView
from PyQt5.QtGui import QPainter, QColor,QPen,QStandardItemModel,QStandardItem
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder
from pathfinding.finder.dijkstra import DijkstraFinder
from PyQt5.QtCore import Qt
import random



class Map(QWidget):

    def __init__(self,array):
        super().__init__()
        self.mapArray = array
        self.path = []         #Отсюда начать
        self.findPathArray = []
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle('Draw MAP')
        self.listModel = QStandardItemModel()

    def mousePressEvent(self, QMouseEvent):
        self.mousePos = QMouseEvent.pos()
        x = self.mousePos.x()
        y = self.mousePos.y()

        ############################################
        x /= self.rectangleWidth      # Находим нужный кубикя rjординаты
        y /= self.rectangleHeight

        x = int(np.floor(x))
        y = int(np.floor(y))

        strItem = str(x)+','+str(y) #Делаем строку
        item = QStandardItem(strItem) # QItem

        self.listModel.appendRow(item)
        self.findPathArray.append([x,y])
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
                if array[k][i] == -1:
                    qp.setBrush(QColor(0, 0, 255))
                    qp.setPen(QColor(0, 0, 255))
                if array[k][i] == 0:
                    qp.setBrush(QColor(0,0,0))
                    qp.setPen(QColor(0,0,0))
                if array[k][i] == -5:
                    qp.setBrush(QColor(255,0,0))
                    qp.setPen(QColor(255, 0, 0))
                if array[k][i] > 1:
                    weight = array[k][i]
                    qp.setBrush(QColor(255,255-weight,255-weight))
                    qp.setPen(QColor(255,255-weight,255-weight))
                if array[k][i] != 1:
                    qp.drawRect(startPoint[0],startPoint[1],self.rectangleWidth, self.rectangleHeight)
                startPoint[0] += self.rectangleWidth

            startPoint[0] = start               #Обнуляем координату ряда
            startPoint[1] += self.rectangleHeight    #Увеличиваем координату высоты

class MapWidget(QWidget):
    def __init__(self,massive):
        super().__init__()
        self.screenArray = massive.copy() # Используем для отображения
        self.map = Map(self.screenArray)
        self.totalPath = []
        self.initUI()
    def initUI(self):
        self.setGeometry(300,300,1300,1000)
        self.rightSide()
        self.leftSide()

        hbox = QHBoxLayout()
        hbox.addWidget(self.leftGroupBox,stretch=100)
        hbox.addWidget(self.rightGroupBox,stretch=20)
        self.setLayout(hbox)
        self.show()
    def rightSide(self):
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
        self.totalPath.clear()

    def findPath(self):    # Должна быть в Росе
        if len(self.map.findPathArray) >= 2:
            while len(self.map.findPathArray) > 1:
                grid = Grid(matrix=self.screenArray)  # eto tut koroche delaet kartu
                startPoint = grid.node(self.map.findPathArray[0][0], self.map.findPathArray[0][1])
                finishPoint = grid.node(self.map.findPathArray[1][0], self.map.findPathArray[1][1])
                finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle)
                path, run = finder.find_path(startPoint, finishPoint, grid)

                print(path)
                print(run)
                #int_mapmap[startPoint[0]][startPoint[1]] = -2 #вносим старт так как не было       -2 - начало
                for elem in path:         #вносим в массив путь,финиш не берем      -3 - конец
                    self.screenArray[elem[1]][elem[0]] = -1   #  путь ..почему то столбики и стролбци наоборот
                self.map.findPathArray.pop(0)
                self.map.listModel.removeRow(0)
                self.totalPath.extend(path)
            self.map.update()
    def makeGradTunnel(self):

        neighbour = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]]
        gridArray = self.totalPath.copy()

        visitedArray = []
        border = []

        tunnelWidth = 10
        weight = 20
        #weightStep = int((255-weight)/tunnelWidth)
        weightStep = 2
        # сюда цикл на сколько то фигнь
        for iter in range(tunnelWidth):
            for i in gridArray:
                for elem in neighbour:
                    y = i[0] + elem[0]
                    x = i[1] + elem[1]  # все перепутано икс и игрик для машины и человека это разное
                    if x < 0 or y < 0 or x>(len(self.screenArray)-1) or y>(len(self.screenArray[0])-1):  # смотрим уходим ли за границу
                        continue
                    if self.screenArray[x][y] == -1 or self.screenArray[x][y] == 0: #смотрим препятствия и путь
                        continue
                    if [x,y] in visitedArray:     #смотрим посещали ли
                        continue
                    border.append([x,y])
                    visitedArray.append([x,y])
            for elem in border:        # раздаем веса
                x = elem[0]
                y = elem[1]
                if iter == tunnelWidth-1:  # В последний раз ставим границу
                    self.screenArray[x][y] = 0  # добавил только для отображения
                else:
                    self.screenArray[x][y] = weight  # добавил только для отображения
            # Повторяю все напутано x и y почему то печаются на экран и в терминал по разному. Координаты границ инвертированы поэтому меняю. НАДО ПЕРЕДЕЛАТЬ
            gridArray.clear()
            weight += weightStep
            for i in border:
                gridArray.append(i[::-1])
            border.clear()
            ################
        self.map.update()



