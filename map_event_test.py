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
        self.array = array
        self.findPathArray = []
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 1000)
        self.setWindowTitle('Draw MAP')
        self.listModel = QStandardItemModel()

    def mousePressEvent(self, QMouseEvent):
        self.mousePos = QMouseEvent.pos()
        x = self.mousePos.x() - self.width_ot  # Так как начинаем не от начала, то подправляем координаты
        y = self.mousePos.y() - self.height_ot
        ############################################
        x /= self.rectangleWidth      # Находим нужный кубикя
        x = int(np.floor(x))
        y /= self.rectangleHeight
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

        array = self.array
        size = self.size()
        self.width_ot = size.width()/100
        self.height_ot = size.height()/100
        self.row_items = len(array[0])   #Длина ряда
        self.colomn_items = len(array)   #Длина колонны
        self.rectangleWidth = (size.width()-(self.width_ot*2))/self.row_items
        self.rectangleHeight = (size.height()-(self.height_ot*2))/self.colomn_items
        start = self.width_ot
        startPoint = [self.width_ot,self.height_ot]

        for k in range(self.colomn_items):
            for i in range(self.row_items):          #Рисуем прямоугольники                if array[k][i] == 0:
                if array[k][i] == -1:
                    qp.setBrush(QColor(0, 0, 255))
                    qp.setPen(QColor(0, 0, 255))
                if array[k][i] == 0:
                    qp.setBrush(QColor(0,0,0))
                    qp.setPen(QColor(0,0,0))
                if array[k][i] == 1:
                    qp.setBrush(QColor(255,0,0))
                    qp.setPen(QColor(255, 0, 0))
                '''if array[k][i] == -3:
                    qp.setBrush(QColor(255,0,0))
                    qp.setPen(QColor(255, 0, 0))
                if array[k][i] == -2:
                    qp.setBrush(QColor(0,255,0))
                    qp.setPen(QColor(0, 255, 0))'''

                if array[k][i] != 1:
                    qp.drawRect(startPoint[0],startPoint[1],self.rectangleWidth, self.rectangleHeight)
                startPoint[0] += self.rectangleWidth

            startPoint[0] = start               #Обнуляем координату ряда
            startPoint[1] += self.rectangleHeight    #Увеличиваем координату высоты

class MapWidget(QWidget):
    def __init__(self,array):
        super().__init__()
        self.array = array # Используем для расчета
        self.screenArray = array # Используем для отображения
        self.map = Map(self.screenArray)
        self.grid = Grid(matrix=self.array)  # eto tut koroche delaet kartu
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
        self.list = QListView()
        self.list.setModel(self.map.listModel)
        vbox = QVBoxLayout()
        vbox.addWidget(self.list,stretch=50)
        vbox.addWidget(self.buttonFindPath,stretch=30)
        vbox.addWidget(self.buttonClearArray,stretch=30)
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
        self.screenArray = self.array

    def findPath(self):
        if len(self.map.findPathArray) >= 2:
            while len(self.map.findPathArray) > 1:
                self.grid.cleanup()
                startPoint = self.grid.node(self.map.findPathArray[0][0], self.map.findPathArray[0][1])
                finishPoint = self.grid.node(self.map.findPathArray[1][0], self.map.findPathArray[1][1])
                finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
                path, run = finder.find_path(startPoint, finishPoint, self.grid)

                print(path)
                print(run)
                #int_mapmap[startPoint[0]][startPoint[1]] = -2 #вносим старт так как не было       -2 - начало
                for elem in path:         #вносим в массив путь,финиш не берем      -3 - конец
                    self.screenArray[elem[1]][elem[0]] = -1   #  путь ..почему то столбики и стролбци наоборот
                    if elem == finishPoint:       #
                        self.screenArray[elem[0]][elem[1]] = -3
                    if elem == startPoint:       #
                        self.screenArray[elem[0]][elem[1]] = -2

                #self.map.update()
                self.map.findPathArray.pop(0)
                self.map.listModel.removeRow(0)
            self.map.update()
