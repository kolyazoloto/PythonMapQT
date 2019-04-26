#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,numpy as np,utm
from PyQt5.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGroupBox,QPushButton,QListView,QLineEdit,QGridLayout,\
    QLabel,QGraphicsScene,QGraphicsView,QSlider
from PyQt5.QtGui import QPainter, QColor,QPen,QStandardItemModel,QStandardItem,QDoubleValidator,QImage,QPixmap
from PyQt5.QtCore import QThread, pyqtSignal,QSize,Qt,QRect
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder


class MyQScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        self.x_mouse = event.scenePos().x()
        self.y_mouse = event.scenePos().y()
        ############################################


class Map(QWidget):


    def __init__(self,array,coord):
        super().__init__()
        self.mapArray = array
        self.coordArray = coord
        self.row_items = len(array[0])
        self.colomn_items = len(array)
        self.mapScale = 5
        self.relation = self.row_items / self.colomn_items
        self.firstImage = self.make_image()   # Создаем фоновое изоюражение большого размера
        self.totalPath = []        #Глобальный путь
        self.localPath = []
        self.findPathArray = []
        self.utmPose = []
        self.pose = [0,0]
        self.initUI()

    def initUI(self):
        self.fonPixMap = QPixmap.fromImage(self.image)
        self.scaledPixMap = self.fonPixMap.scaled(800,800,Qt.KeepAspectRatio)
        self.imageView = QGraphicsView()
        self.imageView.setGeometry(0,0,self.width(),self.height())
        self.scene = MyQScene()
        self.scene.addPixmap(self.scaledPixMap)
        self.imageView.setScene(self.scene)

        vbox = QVBoxLayout()
        vbox.addWidget(self.imageView)
        self.setLayout(vbox)

        self.listModel = QStandardItemModel()
    def updateImage(self):
        self.fonPixMap = QPixmap.fromImage(self.image)
        self.scaledPixMap = self.fonPixMap.scaled(800,800,Qt.KeepAspectRatio)
        self.scene.clear()
        self.scene.addPixmap(self.scaledPixMap)
        self.imageView.setScene(self.scene)
        self.imageView.update()
    def mousePressEvent(self, QMouseEvent):
        x_mouse = self.scene.x_mouse
        y_mouse = self.scene.y_mouse
        ############################################
        x = x_mouse / self.rectangleWidth      # Находим нужный кубикя координаты
        y = y_mouse / self.rectangleHeight
        x = int(np.floor(x))
        y = int(np.floor(y))
        if x < 0 or y < 0:
            return
        strItem = "{0} {1}".format(x,y) #Делаем строку
        item = QStandardItem(strItem) # QItem
        self.listModel.appendRow(item)
        self.findPathArray.append([x,y])
        self.imageView.repaint()
        print(self.findPathArray)

    def make_image(self):


        im_width = 1500
        im_height = 1500/self.relation

        self.image = QImage(QSize(im_width,im_height),QImage.Format_RGB32)
        self.image.fill(Qt.white)
        painter = QPainter(self.image)

        array = self.mapArray
        size = self.image.size()
        self.rectangleWidth = (size.width())/self.row_items
        self.rectangleHeight = (size.height())/self.colomn_items
        start = 0
        startPoint = [0,0]

        for k in range(self.colomn_items):
            for i in range(self.row_items):          #Рисуем прямоугольники                if array[k][i] == 0:
                if array[k][i] == 0:  # Цвета для препятствия
                    #painter.fillRect(startPoint[0], startPoint[1], self.rectangleWidth, self.rectangleHeight,Qt.black)
                    painter.setBrush(QColor(0,0,0))
                    painter.setPen(QColor(0,0,0))
                    painter.drawRect(startPoint[0], startPoint[1], self.rectangleWidth, self.rectangleHeight)
                if array[k][i] > 1:  # Цвета для весов
                    #painter.fillRect(startPoint[0], startPoint[1], self.rectangleWidth, self.rectangleHeight,Qt.black)
                    painter.setBrush(QColor(255,255-array[k][i],255-array[k][i]))
                    painter.setPen(QColor(255,255-array[k][i],255-array[k][i]))
                    painter.drawRect(startPoint[0], startPoint[1], self.rectangleWidth, self.rectangleHeight)
                startPoint[0] += self.rectangleWidth

            startPoint[0] = start               #Обнуляем координату ряда
            startPoint[1] += self.rectangleHeight    #Увеличиваем координату высоты
        #self.image.save("alo.png")
        painter.end()
        return self.image
    def paintEvent(self, event):
        array = self.mapArray
        size = self.scaledPixMap.size()
        self.rectangleWidth = (size.width()) / self.row_items
        self.rectangleHeight = (size.height()) / self.colomn_items


        ### Отображение из массивов
        for i in self.totalPath:  # Рисуем массив пути
            self.scene.addRect(self.rectangleWidth * i[0], self.rectangleHeight * i[1], self.rectangleWidth,
                        self.rectangleHeight,Qt.blue,Qt.blue)
        for i in self.findPathArray:  # Рисуем точки

            self.scene.addRect(self.rectangleWidth * i[0], self.rectangleHeight * i[1], self.rectangleWidth,
                        self.rectangleHeight,Qt.red,Qt.red)


        self.scene.addRect(self.rectangleWidth * self.pose[0], self.rectangleHeight * self.pose[1], self.rectangleWidth,
                    self.rectangleHeight,Qt.green,Qt.green)

class MapWidget(QWidget):

    def __init__(self,massive,coord):
        super().__init__()
        self.screenArray = massive.copy() # Используем для отображения
        self.map = Map(self.screenArray,coord)
        self.initUI()
        self.resize(900,900) # для перерасчета размеров с учетом отношения сторон

    def initUI(self):
        self.setGeometry(300,300,800,800)
        self.poseWID() ################
        self.setPointWid()
        self.rightSide()
        self.leftSide()

        hbox = QHBoxLayout()
        hbox.addWidget(self.leftGroupBox,stretch=100)
        hbox.addWidget(self.rightGroupBox,stretch=20)
        print(self.map.row_items)
        print(self.map.colomn_items)
        self.setLayout(hbox)
        self.show()
        self.posewid.show()  ##########

    def bindingСoord(self,x,y):
        for index, cord in enumerate(self.map.coordArray):
            if float(cord[0])-(self.map.mapScale/2) < x < float(cord[0])+(self.map.mapScale/2):
                x_index = index  # Находим индекс

        for index, cord in enumerate(self.map.coordArray):
            if float(cord[1])-(self.map.mapScale/2) < y < float(cord[1])+(self.map.mapScale/2):
                y_index = index  # Находим индекс
        # Сделать проверку в нашу входят значения или нет
        return x_index,y_index
    def courseCalculation(self):
        a = self.map.utmPose
        b = self.map.totalPath[-1] # точка на рассчитанном пути к которой будем стороить курс координаты массивные
        b = [int(self.map.coordArray[b[0]][0]),int(self.map.coordArray[b[1]][1])] # взять из массива координат координату для нашей клетки

        ab = [b[0] - a[0], b[1] - a[1]]  # Определяем координаты вектора
        vecLength = np.sqrt(ab[0]**2 + ab[1]**2) # длина вектора
        katetLength = ab[1]
        course = (np.arccos(katetLength/vecLength))*180/np.pi  # Находим курс и переводим в градусы
        if ab[0] < 0:
            course *= -1
        print(course)
        return course

    def poseWID(self):
        def update_pose():
            a = float(self.pose_x_lineEdit.text())
            b = float(self.pose_y_lineEdit.text())
            utm_cord = utm.from_latlon(a,b)
            print(utm_cord)
            x,y = self.bindingСoord(utm_cord[0],utm_cord[1])

            recountLength = 10    # В настройки
            prev_pose = self.map.pose
            qrect = QRect(x,y,)
            self.map.pose = [x, y]   # заносим координаты клетки в память
            self.map.utmPose = [utm_cord[0], utm_cord[1]] # заносим координаты utm в память
            if len(self.map.totalPath) != 0:   # Проверяем есть ли в точках пути значения
                if (x, y) not in self.map.totalPath:    # Если мы не на пути включаем перерасчет
                    # включить перерасчет
                    ######################
                    print("ПЕРЕРАСЧЕТ")
                    self.recountPath(self.map.pose,self.map.totalPath[recountLength])  # переделать в возвращение функции
                    del(self.map.totalPath[:recountLength])    # удаляем из глобального пути все точки до N
                    self.map.totalPath = self.map.localPath + self.map.totalPath
                    self.map.localPath.clear()
                    ######################'''
                elif (x,y) in self.map.totalPath:
                    #определяем где мы в пути
                    ######################
                    print("НА ПУТИ")
                    del(self.map.totalPath[:self.map.totalPath.index((x,y))])  # Удаляем все элементы в массиве до нашего
                    #self.recountPath(self.map.pose,self.map.totalPath[10])
                    ######################'''
            if self.map.pose != prev_pose:   # Обновляем экран только в случае изменения координаты
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
    def setPointWid(self):

        validator = QDoubleValidator()
        latitude = QLineEdit()
        latitude.setWindowTitle("Широта")
        #latitude.setValidator(validator)
        longitude = QLineEdit()
        longitude.setWindowTitle("Долгота")
        #longitude.setValidator(validator)

        addPointButton = QPushButton()
        addPointButton.setText("Добавить точку")

        def addPointButtonCallback():
            x = float(latitude.text())
            y = float(longitude.text())
            utm_coords= utm.from_latlon(x,y)

            x,y = self.bindingСoord(utm_coords[0],utm_coords[1])
            strItem = "{0} {1}".format(x,y)
            item = QStandardItem(strItem)  # QItem
            self.map.listModel.appendRow(item)
            self.map.findPathArray.append([x,y])
            self.map.update()

        addPointButton.clicked.connect(addPointButtonCallback)


        vbox = QVBoxLayout()
        vbox.addWidget(latitude)
        vbox.addWidget(longitude)
        vbox.addWidget(addPointButton)

        self.setPointGroupBox = QGroupBox()
        self.setPointGroupBox.setLayout(vbox)
    def rightSide(self):
        def scaleImage():
            print(self.map.scaledPixMap.size())
            print(self.map.imageView.width(),self.map.imageView.height())
            #print("\n")
            value = self.scaleSlider.value()
            self.map.scaledPixMap = self.map.fonPixMap.scaled(value,value, Qt.KeepAspectRatio)
            self.map.scene.clear()
            self.map.imageView.setScene(self.map.scene)
            self.map.scene.addPixmap(self.map.scaledPixMap)
            self.map.imageView.update()
        def finishScaleImage():
            value = self.scaleSlider.value()
            self.map.scene = MyQScene()
            self.map.scaledPixMap = self.map.fonPixMap.scaled(value,value, Qt.KeepAspectRatio)
            self.map.scene.clear()
            self.map.imageView.setScene(self.map.scene)
            #self.map.scene.update()
            self.map.scene.addPixmap(self.map.scaledPixMap)
            self.map.imageView.update()
        self.buttonRun = QPushButton()
        self.buttonRun.setText("ПОИХАЛI")
        self.buttonRun.clicked.connect(self.map.make_image)
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
        ##
        self.scaleSlider = QSlider(Qt.Horizontal)
        self.scaleSlider.setMinimum(100)
        startScale = self.map.image.width()
        self.scaleSlider.setMaximum(startScale+2000)
        self.scaleSlider.setValue(startScale)
        self.scaleSlider.valueChanged.connect(scaleImage)
        self.scaleSlider.sliderReleased.connect(finishScaleImage)
        ##
        vbox = QVBoxLayout()
        vbox.addWidget(self.list,stretch=50)
        vbox.addWidget(self.buttonRun, stretch=30)
        vbox.addWidget(self.scaleSlider)
        vbox.addWidget(self.setPointGroupBox)
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
        ###########   Только обновляем сцены
        self.map.scene.clear()
        self.map.scene.addPixmap(self.map.scaledPixMap)
        self.map.imageView.update()
        ###########


    def findPath(self):    # Thread
        def updateFindPath(path):
            self.map.listModel.removeRow(0)
            self.map.totalPath.extend(path)
            self.map.update()
        def done():
            self.buttonFindPath.setEnabled(1)
            print("find path DONE")
            print(self.map.totalPath)
            print(len(self.map.totalPath))
            self.courseCalculation()
        def disButt():

            self.buttonFindPath.setDisabled(1)
        self.findThread = FindPathThread(self.screenArray,self.map.findPathArray,self.map.pose)
        self.findThread.findPathSignal.connect(updateFindPath)
        self.findThread.started.connect(disButt)
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
            self.map.make_image() # Так как карта
            self.map.updateImage()
            self.buttonTestGrad.setEnabled(1)
            print("Grad done")
        def disButt():
            self.buttonTestGrad.setDisabled(1)
        self.gradThread = MakeGradThread(self.screenArray,self.map.totalPath)
        self.gradThread.makeGradSignal.connect(updateGradTunnel)
        self.gradThread.started.connect(disButt)
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
            if iter != tunnelWidth-1:
                self._makeGrad(weight)
                weight += weightStep
            else:
                self._makeGrad(0)   # ставим ограждение


















