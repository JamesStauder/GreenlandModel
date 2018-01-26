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
from mouse_click_functions import *


'''





'''

def centerVelocityStream(x, y):
    # x,y in color coordinates
    x0p, y0p = colorToProj(x, y)
    y0 = np.array([x0p, y0p])
    t0, t1, dt = 0, 80, .1
    r = ode(getProfile).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t0)
    ox = []
    oy = []
    ind = 0
    while r.successful() and ind < 2:
        '''
        what the fuck was I trying to do here??
        I think, integrate then look perpindicular for the velocity width margins
        '''
        ai = r.integrate(r.t + dt)
        ind += 1
        xi, yi = colorCoord(np.real(ai[0]), np.real(ai[1]))
        ox.append(xi)
        oy.append(yi)
    # iiContainer.currentWidget().addItem(pg.PlotDataItem(ox, oy, pen=blackPlotPen))

    endPoints = [[0, 0], [0, 0]] # either side of the velocity stream
    endPoints[0][0], endPoints[0][1], endPoints[1][0], endPoints[1][1] = calcVelWidth(x, y, ox[-1], oy[-1], True)
    d = (0.5) * np.sqrt((endPoints[0][0] - endPoints[1][0]) ** 2 + (endPoints[0][1] - endPoints[1][1]) ** 2)
    theta = np.arctan2(float(y - oy[-1]), float(x - ox[-1]))
    x, y = endPoints[0][0] + (d * -np.sin(theta)), endPoints[0][1] + (d * np.cos(theta))
    return x, y

def linePressed(e):
    '''
    Check to see if the white int. line was clicked while shift was held, if so:
    1. set int line as data
        -Delete markers past the marker associated with the line
    2. add marker to end of line
        -marker can be dragged back and forth to shorten line
        -marker can be shift+clicked again to create a new int line
        -new int line can then be selected
            MAKE SURE IT CAN BE ADDED TO PATH

    :param e: the plotDataItem
    :return:
    '''
    global vptSel, vptCur
    print "linePressed triggered."

    if vptSel==True:
        print "linePressed triggered and vptSel true"
        del vptCur
        vptSel = False

    if keysPress['shift']:

        # find which marker got clicked
        # delete all markers after clicked one
        i = 0
        while(e is not intLines[i][0] and i < len(intLines) -1):
            i += 1
        print i
        j = 0
        while(intLines[i][1] is not markers[j]):
            j+=1
        for k in range(j,len(markers)-1):
            del markers[j+1]


        for l in range(1,len(e.xData)-2):
            '''
            Doesn't include last marker
            '''
            cx, cy = e.xData[l], e.yData[l]
            dx, dy = colorToData(cx, cy)
            px, py = colorToProj(cx, cy)
            v0 = velocity.interp([px], [py], grid=False)
            markers.append(Marker(cx, cy, dx, dy, v0, iiContainer.currentWidget(), plotCross=False))

        # do last marker seperatly since want an X on the map for it
        cx, cy = e.xData[-1], e.yData[-1]
        dx, dy = colorToData(cx, cy)
        px, py = colorToProj(cx, cy)
        v0 = velocity.interp([px], [py], grid=False)
        markers.append(Marker(cx, cy, dx, dy, v0, iiContainer.currentWidget()))
        iiContainer.currentWidget().addItem(markers[-1].getCross()[0])
        iiContainer.currentWidget().addItem(markers[-1].getCross()[1])
        print '# markers', len(markers)
        print 'last data point\n'
        print 'cx,cy ', markers[-1].cx, markers[-1].cy
        print 'dx,dy ', markers[-1].dx, markers[-1].dy

    elif keysPress['ctrl']:
        print "del line"
        for m in range(len(intLines)):
            cData = intLines[m][0].curve.getData()
            imin = curveDistance(e.pos().x(), e.pos().y(), cData)
            found = False
            if imin != -1:
                # snap the cross to the line
                iiContainer.currentWidget().removeItem(intLines[m])
                del (intLines[m])
                found = True
            if found:
                break


def mouseClick(e):
    '''
    triggers when the colormap is clicked on.  Could probably be put into several functions.

    '''
    global vptSel, vptCur#, integrateLine
    first = False
    if len(markers) == 0:

        first = True
        cx = e.pos().x()
        cy = e.pos().y()
        if autoCorrectVpt.checkState() == 2:
            cx, cy = centerVelocityStream(cx, cy)

    if not vptSel:
        # If there is not a marker selected already
        markerClicked = False
        for i in range(len(markers)):
            if markers[i].checkClicked(e.pos()):
                '''
                Check to see if a marker is clicked
                '''
                markerClicked = True
                # See if you clicked on an already existing point
                if keysPress['shift']:
                    shiftPressedMarkerClicked(linePressed, i)

                elif keysPress['ctrl']:
                    ctrlPressedMarkerClicked(i)

                else:
                    # A marker is clicked on while no buttons are being held - it is selected and can be moved now
                    vptSel = True
                    vptCur = markers[i]
                break # Exit loop if a marker has been clicked on
        # for ln in intLines:
        #     if sqrt((e.pos().x() - ln[0].curve.getData()[0][-1])**2 + (e.pos().y() - ln[0].curve.getData()[1][-1])**2) < 20:
        #         print 'Clicked end of line'
        #         globalConstants['moveLine'] = True
        #         globalConstants['lineData'] = ln[0].curve.getData()
        #         globalConstants['minIndex'] = len(globalConstants['lineData']) - 1


        if not markerClicked and keysPress['ctrl']:
            '''
                See if an integration line is being deleted.
            '''
            print 'control clicked'
            for m in range(len(intLines)):
                cData = intLines[m][0].curve.getData()
                imin = curveDistance(e.pos().x(), e.pos().y(), cData)
                found = False
                if imin != -1:
                    # snap the cross to the line
                    iiContainer.currentWidget().removeItem(intLines[m])
                    del (intLines[m])
                    found = True
                if found:
                    break

        elif not markerClicked and keysPress['shift']: # elif not markerClicked and keysPress['alt']:
            '''
            This allows the user to set the white integration line as the data path!
            '''
            #FIXME finish making
            for m in range(len(intLines)):
                cData = intLines[m][0].curve.getData()
                imin = curveDistance(e.pos().x(), e.pos().y(), cData)
                if imin != -1:
                    # If you clicked within one pixel of the line
                    # FIXME need to make this line into the path data
                    print 'shift clicked line'
                    globalConstants['isPathIntLine'] = True
                    globalConstants['lineData'] = intLines[m][0].curve.getData()
                    globalConstants['lineIndex'] = m
                    globalConstants['minIndex'] = len(globalConstants['lineData']) - 1
                    globalConstants['minValue'] = 99#globalConstants['lineData'][-1]
                    intLines[m][0].setPen(purplePlotPen)
                    break

        elif not markerClicked and not keysPress['shift'] and not globalConstants['moveLine']:
            # no you did not click on a point
            if not first:
                cx = e.pos().x() # in color coordinates
                cy = e.pos().y()
                if autoCorrectVpt.checkState() == 2:
                    cx, cy = centerVelocityStream(cx, cy)


            px, py = colorToProj(cx, cy) # color map to projected
            v0 = velocity.interp([px], [py], grid=False)
            dx, dy = colorToData(cx, cy)
            markers.append(Marker(cx, cy, dx, dy, v0, iiContainer.currentWidget())) # in map coordinates x<10018, y< 17946

            x = int(np.floor(dx))
            y = int(np.floor(dy))
            txt = 'Point ' + str(len(markers) - 1) + \
            ':\n=================\n' + \
            'x: ' + str(cx) + '\n' +\
            'y: ' + str(cy) + '\n' +\
            'v: ' +      "{:.3f}".format(velocity.data[y][x]) + \
            '\nbed: ' +  "{:.3f}".format(bed.data[y][x]) + \
            '\nsurf: ' + "{:.3f}".format(surface.data[y][x]) + \
            '\nSMB: ' +  "{:.3f}".format(smb.data[y][x]*(1.0/1000.0)*(916.7/1000.0)) + \
            '\nSMB: ' +  "{:.3f}".format(smb.data[y][x]) + \
            '\nt2m: ' +  "{:.3f}".format(t2m.data[y][x]) + '\n\n'

            textOut.append(txt)
            iiContainer.currentWidget().addItem(markers[-1].getCross()[0])
            iiContainer.currentWidget().addItem(markers[-1].getCross()[1])
            # vpts[-1].setIntLine(calcProf(None))
            if len(markers) > 1:
                if not modelButton.isEnabled():
                    modelButton.setEnabled(True)
                    cProfButton.setEnabled(True)
                    meshButton.setEnabled(True)
                xa = [markers[-2].cx, markers[-1].cx]
                ya = [markers[-2].cy, markers[-1].cy]
                markers[-1].setLine(pg.PlotDataItem(xa, ya, connect='all', pen=skinnyBlackPlotPen), 0)
                markers[-2].setLine(markers[-1].lines[0], 1)
                iiContainer.currentWidget().addItem(markers[-1].lines[0])  # ,pen=plotPen)
    else:
        #FIXME Why delete vptCur ?? I remember it caused a bug
        print "Clicked while marker already selected"
        del vptCur
        vptSel = False


def changeMap(index):
    '''
    Called when data-set drop down menu is changed.
    :param index:
    :return:
    '''

    # print iiContainer.currentWidget()
    vr = iiContainer.currentWidget().getPlotItem().getViewBox().viewRange()
    maps = [velocity, bed, surface, smb, thickness, t2m]
    global currentMap
    if index != currentMap:
        oldMap = currentMap
        currentMap = index
        # if not colormaps[maps[index].name]:
        #     print 'not colormap'
        #     maps[index].createColorMap()
        #     iiContainer.addWidget(maps[index].plotWidget)
        #     maps[index].imageItem.hoverEvent = mouseMoved

        iiContainer.setCurrentWidget(maps[index].plotWidget)
        maps[index].imageItem.hoverEvent = mouseMoved
        maps[index].imageItem.mouseClickEvent = mouseClick
        maps[index].plotWidget.getPlotItem().getViewBox().setRange(xRange=vr[0], yRange=vr[1], padding=0.0)
        for ln in intLines:
            maps[oldMap].plotWidget.removeItem(ln[0])
            maps[currentMap].plotWidget.addItem(ln[0])
        for pt in markers:
            pt.plotWidget = maps[currentMap]
            maps[oldMap].plotWidget.removeItem(pt.cross[0])
            maps[oldMap].plotWidget.removeItem(pt.cross[1])
            maps[currentMap].plotWidget.addItem(pt.cross[0])
            maps[currentMap].plotWidget.addItem(pt.cross[1])
            if pt.lines[0]:
                maps[oldMap].plotWidget.removeItem(pt.lines[0])
                maps[currentMap].plotWidget.addItem(pt.lines[0])
            if pt.intLine:
                maps[oldMap].plotWidget.removeItem(pt.intLine)
                maps[currentMap].plotWidget.addItem(pt.intLine)



def openStaticPlotter():
    '''
    Calculate the data for bottom plot then populate the plot.
    :return:
    '''
    foo = StaticPlot(mw)


def mouseMoved(e):
    global vptSel, vptCur, integrateLine, currentMap
    if e.isExit() is False:
        if vptSel and len(intLines) != 0 : #integrateLine is not None:  # and integrateLine is not None:
            #
            # Checks to see if you are moving around a point and if it is near a curve
            # which it can be snapped to
            #
            i = 0
            while i < len(intLines):
                cData = intLines[i][0].curve.getData()
                imin = curveDistance(e.pos().x(), e.pos().y(), cData)
                if imin != -1:
                    # snap the cross to the line
                    vptCur.cx = cData[0][imin]
                    vptCur.cy = cData[1][imin]
                    vptCur.updateCross()
                    i = len(intLines) + 5
                else:
                    # just move the cross
                    vptCur.cx = e.pos().x()
                    vptCur.cy = e.pos().y()
                    vptCur.updateCross()
                if vptCur.lines[0] is not None:
                    vptCur.lines[0].setData([vptCur.lines[0].getData()[0][0], vptCur.cx],
                                            [vptCur.lines[0].getData()[1][0], vptCur.cy])  # previous line
                if vptCur.lines[1] is not None:
                    vptCur.lines[1].setData([vptCur.cx, vptCur.lines[1].getData()[0][1]],
                                            [vptCur.cy, vptCur.lines[1].getData()[1][1]])  # next line
                i += 1
        elif vptSel:
            # Moving a marker but not near an integration line
            vptCur.cx = e.pos().x()
            vptCur.cy = e.pos().y()
            vptCur.updateCross()
            if vptCur.lines[0] is not None:
                vptCur.lines[0].setData([vptCur.lines[0].getData()[0][0], vptCur.cx],
                                        [vptCur.lines[0].getData()[1][0], vptCur.cy])  # previous line
            if vptCur.lines[1] is not None:
                vptCur.lines[1].setData([vptCur.cx, vptCur.lines[1].getData()[0][1]],
                                        [vptCur.cy, vptCur.lines[1].getData()[1][1]])  # next

        elif globalConstants['moveLine']:
            mi = len(globalConstants['lineData']) - 1
            mv = globalConstants['minValue'] = globalConstants['lineData'][-1]
            for i in range(len(globalConstants['lineData'][0])):
                # globalConstants['minIndex'] = len(globalConstants['lineData']) - 1
                # globalConstants['minValue'] = globalConstants['lineData'][-1]

                if sqrt((globalConstants['lineData'][0][globalConstants['minIndex']] - e.pos().x())**2 +(globalConstants['lineData'][1][globalConstants['minIndex']] - e.pos().y())**2) < mv:
                    mi = i
                    mv = sqrt((globalConstants['lineData'][0][globalConstants['minIndex']] - e.pos().x())**2 +
                         (globalConstants['lineData'][1][globalConstants['minIndex']] - e.pos().y())**2)
                intLines[globalConstants['lineIndex']][0].curve.setData(globalConstants['lineData'][0][:mi], globalConstants['lineData'][0][:mi])


        x = int(np.floor(e.pos().x()))
        y = int(np.floor(e.pos().y()))
        if np.abs(x) <= map['cmap_x1'] and np.abs(y) <= map['cmap_y1']:
            mouseCoordinates.setText('x: ' + str(x) + '\ty: ' + str(y))# + '\n' + 'th: ' + str(thickness.data[y][x]))# + '\n' + 'oth: ' + str(oldthick.data[y][x]))




def calcProf(e):
    '''
    Calculates the line that shows velocity flow inwards (negative direction).
    :param e:
    :return:
    '''
    global integrateLine
    print 'calcProf'
    x0p, y0p = colorToProj(markers[-1].cx, markers[-1].cy)
    y0 = np.array([x0p, y0p])
    t0, t1, dt = 0, 80, .1

    r = ode(getProfile).set_integrator('zvode', method='bdf')
    r.set_initial_value(y0, t0)
    ox = [markers[-1].cx]
    oy = [markers[-1].cy]
    while r.successful() and r.t < t1:
        # print(r.t+dt, r.integrate(r.t+dt))
        ai = r.integrate(r.t+dt)
        xi, yi = colorCoord(ai[0], ai[1])
        # print 'xi, iy: ', xi, yibe
        ox.append(np.real(xi))
        oy.append(np.real(yi))
    integrateLine = pg.PlotDataItem(ox, oy, pen=whitePlotPen)
    iiContainer.currentWidget().addItem(integrateLine)



def regionIntLine(e):
    '''
    DEPRECATED -> WAS USED FOR TESTING
    Calculates and prints the integrated velocity path for several paths in a velocity stream.
    :param e:
    :return:
    '''
    xp0 = markers[-1].cx
    yp0 = markers[-1].cy
    xp1 = markers[-2].cx
    yp1 = markers[-2].cy
    xril, yril, xrir, yrir = calcVelWidth(xp0, yp0, xp1, yp1, False)  # for vpts[-1]

    theta = np.arctan2((yril - yrir), (xril - xrir))
    d = np.sqrt((yril - yrir) ** 2 + (xril - xrir) ** 2)
    dr = 10
    l = linspace(-d / 2, d / 2, dr, endpoint=True)

    rotMatrix = np.matrix([[np.cos(theta), -1 * np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    lines = []

    for i in range(len(l)):
        '''
            Moves along velocity width line.
            Good spot for parallel programming.
        '''
        trot = rotMatrix * np.matrix([[l[i]], [0.0]])
        x0p, y0p = projCoord((xp1 + trot[0, 0]), (yp1 + trot[1, 0]))
        lines.append(intLine(x0p, y0p))
        iiContainer.currentWidget().addItem(lines[-1])

def ky(e):
    # 16777248 is shift
    # 16777249 is left ctrl
    #6 is press, 7 is release
    if e.type() == 6:
        if e.key() == 16777248:
            keysPress['shift'] = True
        elif e.key() == 16777249:
            keysPress['ctrl'] = True
        elif e.key() == 16777251:
            keysPress['alt'] = True
            print 'pressed alt'
    else:
        keysPress['ctrl'] = False
        keysPress['shift'] = False
        keysPress['alt'] = False
