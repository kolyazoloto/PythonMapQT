import numpy,sys
from heapq import *
import map_event_test
from PyQt5.QtWidgets import QApplication



if __name__ == '__main__':


    f = open('/home/nikolay/Рабочий стол/2 ISTU_Digital_1,0_Digital_5,0.txt', 'r')
    mapmap = f.readlines()
    mapmap = [i.replace("100", "0") for i in mapmap]
    mapmap = [i.replace("50", "0") for i in mapmap]
    f.close()

    mapmap = [line.split() for line in mapmap]
    int_mapmap = []
    for line in mapmap:
        line = [int(i) for i in line]
        int_mapmap.append(line)

    '''int_mapmap = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]'''
    app = QApplication(sys.argv)
    ex = map_event_test.MapWidget(int_mapmap)
    sys.exit(app.exec_())