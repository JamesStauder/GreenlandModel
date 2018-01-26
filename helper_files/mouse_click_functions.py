import numpy as np
from scipy.integrate import ode

# LOCAL IMPORTS
from math_functions import *
from pens import *
from gui import *
from dataset_objects import *
from data_functions import *
from classes.Marker import *
from velocity_functions import *
from classes.StaticPlotter import *


def shiftPressedMarkerClicked(linePressed, i):
    '''
        Integrate line if marker clicked
    '''

    x0p, y0p = colorToProj(markers[i].cx, markers[i].cy)
    y0 = np.array([x0p, y0p])
    t0, t1, dt = 0, 80, .1
    r = ode(getProfile).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t0)
    ox = [markers[i].cx]
    oy = [markers[i].cy]
    try:
        segLength = float(intResInput.text())
        while r.successful() and r.t < t1:
            ai = r.integrate(r.t + dt)
            xi, yi = colorCoord(ai[0], ai[1])
            if np.sqrt((xi - ox[-1]) ** 2 + (yi - oy[-1]) ** 2) > segLength / 150:
                ox.append(np.real(xi))
                oy.append(np.real(yi))
        print 'len(ox), len(oy)', len(ox), len(oy)
        print ox
        print oy
        intLines.append([pg.PlotDataItem(ox, oy, pen=whitePlotPen), markers[i]])
        intLines[-1][0].curve.setClickable(True)
        intLines[-1][0].curve.opts[
            'mouseWidth'] = 20  # Makes the clickable part of the line wider so it is easier to select
        intLines[-1][0].sigClicked.connect(linePressed)
        iiContainer.currentWidget().addItem(intLines[-1][0])
    except ValueError:
        textOut.append(('\nMust enter valid number for integration line resolution!'))


def ctrlPressedMarkerClicked(i):
    '''
        Ctrl+click will delete marker or line
    '''
    if i > 0:
        if i + 1 < len(markers):
            # connect line from previous node to next point
            markers[i - 1].lines[1] = pg.PlotDataItem([markers[i - 1].cx, markers[i + 1].cx],
                                                      [markers[i - 1].cy, markers[i + 1].cy], connect='all',
                                                      pen=skinnyBlackPlotPen)
            markers[i + 1].lines[0] = markers[i - 1].lines[1]
            iiContainer.currentWidget().addItem(markers[i - 1].lines[1])
            pg.QtGui.QApplication.processEvents()
        else:  # delete line because there is no next point
            iiContainer.currentWidget().removeItem(markers[i - 1].lines[1])
            markers[i - 1].lines[1] = None
    elif i == 0 and len(markers) > 1:  # point is the first so delete line from first to second
        iiContainer.currentWidget().removeItem(markers[1].lines[0])
        markers[1].lines[0] = None
    for k in range(i, len(markers) - 1):
        markers[k] = markers[k + 1]
    del markers[-1]
    if len(markers) < 2:
        modelButton.setEnabled(False)
        cProfButton.setEnabled(False)
        meshButton.setEnabled(False)
    print 'Number of markers is ', len(markers)

# def checkDeleteIntLine(e):
#     '''
#         See if an integration line is being deleted.
#     '''
#     print 'control clicked'
#     for m in range(len(intLines)):
#         cData = intLines[m][0].curve.getData()
#         imin = curveDistance(e.pos().x(), e.pos().y(), cData)
#         found = False
#         if imin != -1:
#             # snap the cross to the line
#             iiContainer.currentWidget().removeItem(intLines[m])
#             del (intLines[m])
#             found = True
#         if found:
#             break