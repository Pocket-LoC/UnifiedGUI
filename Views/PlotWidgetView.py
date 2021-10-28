from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from datetime import datetime
import numpy as np


class PlotWidgetView(pg.PlotWidget):
    def __init__(self, plot_view):
        super().__init__(axisItems={'bottom': TimeAxisItem(orientation='bottom')})

        self.plot_view = plot_view

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "Value")
        self.setLabel('bottom', "Time")

        # Grid
        self.showGrid(x=True, y=True)

        self.data_lines = []

        self.last_vals = None
        self.last_symbol_intervals = None
        self.last_symbol_values = None
        self.vertical_lines = []
        self.text_items = []

        # TODO?
        # self.setDownsampling(ds=10)

        self.legend = pg.LegendItem()
        self.legend.setParentItem(self.getPlotItem())

    def add_datalines(self, receiver_info):
        for i in range(len(receiver_info)):
            description, sensor_descriptions = receiver_info[i]['description'], receiver_info[i]['sensor_descriptions']
            data_lines_ = []
            for j in range(len(sensor_descriptions)):
                data_line = self.plot([], [], name=description + ": " + sensor_descriptions[j], pen=self.plot_view.settings['pens'][i][j])
                data_lines_.append(data_line)
                self.legend.addItem(data_line, data_line.name())
            self.data_lines.append(data_lines_)

    def update_pens(self, receiver_index, sensor_index):
        pen = self.plot_view.settings['pens'][receiver_index][sensor_index]
        self.data_lines[receiver_index][sensor_index].setPen(pen)

    def remove_datalines(self):
        for i in range(len(self.data_lines)):
            for j in range(len(self.data_lines[i])):
                self.legend.removeItem(self.data_lines[i][j])
                self.data_lines[i][j].clear()
                self.update_()
        self.data_lines = []
        self.last_vals = None
        self.deactivate_symbol_intervals()
        self.last_symbol_intervals = None
        self.deactivate_symbol_values()
        self.last_symbol_values = None

    def update_values(self, vals):
        timestamps, values = vals['timestamps'], vals['values']
        for receiver_index in range(len(timestamps)):
            if timestamps[receiver_index] is not None:
                for sensor_index in range(values[receiver_index].shape[1]):
                    if self.plot_view.settings['active'][receiver_index][sensor_index]:
                        # TODO: Only plot every x-th value, if it is too laggy
                        # self.data_lines[receiver_index][sensor_index].setData(timestamps[receiver_index][::1], values[receiver_index][:, sensor_index][::1])
                        self.data_lines[receiver_index][sensor_index].setData(timestamps[receiver_index], values[receiver_index][:, sensor_index])
        self.last_vals = vals

    def update_symbol_intervals(self, symbol_intervals):
        # TODO: Only plot the new lines, not all of them
        if self.plot_view.settings['symbol_intervals']:
            for timestamp in symbol_intervals[len(self.vertical_lines):]:
                vertical = pg.InfiniteLine(pos=timestamp, angle=90, movable=False, pen=self.plot_view.settings['symbol_intervals_pen'])
                self.addItem(vertical)
                self.vertical_lines.append(vertical)

        self.last_symbol_intervals = symbol_intervals

    def deactivate_symbol_intervals(self):
        for i in self.vertical_lines:
            self.removeItem(i)
        self.vertical_lines = []
        # self.last_symbol_intervals = None

    def activate_symbol_intervals(self):
        self.update_symbol_intervals(self.last_symbol_intervals)

    def update_symbol_values(self, symbol_intervals, symbol_values):
        if self.plot_view.settings['symbol_values']:
            for i in range(len(self.text_items), len(symbol_values)):
                # TODO: Special case for last value
                # x_pos = symbol_intervals[i]
                x_pos = 0.5 * (symbol_intervals[i] + symbol_intervals[i+1])
                text = pg.TextItem(symbol_values[i], color='k')
                # TODO: Place in correct height
                text.setPos(x_pos, 1)
                self.addItem(text)
                self.text_items.append(text)
        self.last_symbol_values = symbol_values

    def deactivate_symbol_values(self):
        for text_item in self.text_items:
            self.removeItem(text_item)
        self.text_items = []

    def activate_symbol_values(self):
        self.update_symbol_values(self.last_symbol_intervals, self.last_symbol_values)

    def deactivate(self, receiver_index, sensor_index):
        self.data_lines[receiver_index][sensor_index].clear()
        self.legend.removeItem(self.data_lines[receiver_index][sensor_index])
        self.update_()

    def update_(self):
        # TODO: Other way possible? update, repaint, resize, QApplication.processEvents do not work
        self.hide()
        self.show()

    def activate(self, receiver_index, sensor_index):
        if self.last_vals is not None:
            timestamps, values = self.last_vals['timestamps'], self.last_vals['values']
            self.data_lines[receiver_index][sensor_index].setData(timestamps[receiver_index], values[receiver_index][:, sensor_index])
        self.legend.addItem(self.data_lines[receiver_index][sensor_index], self.data_lines[receiver_index][sensor_index].name())


class TimeAxisItem(pg.AxisItem):
    """
    Converts the timestamps from a float to a human-readable format for the x-axis ticks.
    """
    def tickStrings(self, values, scale, spacing):
        x = [datetime.fromtimestamp(value) for value in values]
        # x = [datetime.time(value) for value in values]
        return x