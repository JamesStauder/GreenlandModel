import pyqtgraph as pg

from ..pens import *

class IntLine:
    def __init__(self, cxArr, cyArr, plotWidget, startMarker, linePressed):
        self.plotWidget = plotWidget
        self.cxArr = cxArr
        self.cyArr = cyArr
        self.plotDataItem = pg.PlotDataItem(self.cxArr, self.cyArr, pen=whitePlotPen)
        self.plotDataItem.setClickable(True)
        self.plotDataItem.curve.opts['mouseWidth'] = 20
        self.plotDataItem.sigClicked.connect(linePressed)
        self.startMarker = startMarker