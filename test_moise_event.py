import numpy,sys
from heapq import *
import map_event_test
from PyQt5.QtWidgets import QApplication



if __name__ == '__main__':

    f = open('/home/nikolay/Рабочий стол/2 ISTU_Digital_1,0_Digital_5,0.txt', 'r')
    mapmap = f.readlines()
    mapmap = [i.replace("100", "0") for i in mapmap]        # меняем значения препятсвий
    mapmap = [i.replace("50", "0") for i in mapmap]     # меняем значение зоны
    f.close()

    mapmap = [line.split() for line in mapmap]
    int_mapmap = []
    for line in mapmap:
        line = [int(i) for i in line]
        int_mapmap.append(line)
    int_mapmap = [i[::-1] for i in int_mapmap]  #отзеркаливаем
    int_mapmap = numpy.rot90(int_mapmap) # поворачиваем

    f = open('/home/nikolay/Рабочий стол/2 ISTU_Digital_1,0_Digital_5,0_coord.txt', 'r')
    coord = f.readlines()
    coord = [i.split() for i in coord]
    print (len(coord))
    f.close()
    print(coord)
    '''int_mapmap = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]'''
    app = QApplication(sys.argv)
    ex = map_event_test.MapWidget(int_mapmap)
    sys.exit(app.exec_())