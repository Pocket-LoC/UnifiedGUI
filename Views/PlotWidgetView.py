from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph.GraphicsScene import exportDialog
from datetime import datetime
import numpy as np
import time

from Utils.Settings import SettingsStore


class PlotWidgetView(pg.PlotWidget):
    def __init__(self, plot_view):
        super().__init__(axisItems={'bottom': pg.DateAxisItem(orientation='bottom')})

        self.plot_view = plot_view

        # Set background color to white
        self.setBackground('w')

        # Axis labels left and bottom
        self.setLabel('left', "Value")
        self.setLabel('bottom', "Time")

        #self.setMouseEnabled(x=True, y=False)
        self.setMouseEnabled(x=False, y=True)

        # Legend
        self.legend = pg.LegendItem(offset=(50, 5))
        self.legend.setParentItem(self.getPlotItem())

        self.additional_datalines = []
        self.datalines = []
        self.landmarks = []
        self.text_items = []
        self.vertical_lines = []

    @property
    def autoscroll(self):
        return self.getViewBox().getState()['autoRange'][0]

    def add_additional_datalines(self, dataline_info):
        """
        Add additional datalines to the plot.
        :param dataline_info: Info about additional datalines (num + names).
        """
        for dataline_index in range(dataline_info['num']):
            pen = pg.mkPen(color=QColor(self.plot_view.settings['additional_datalines_color'][dataline_index]),
                           style=getattr(Qt, self.plot_view.settings['additional_datalines_style'][dataline_index]),
                           width=self.plot_view.settings['additional_datalines_width'])
            data_line = self.plot([], [], name=dataline_info['names'][dataline_index], pen=pen)
            self.additional_datalines.append(data_line)
            if self.plot_view.settings['additional_datalines_active'][dataline_index]:
                self.legend.addItem(data_line, data_line.name())

    def add_datalines(self, receiver_info):
        """
        Adds new datalines to the plot.
        :param receiver_info: Info about receivers (num + receiver name + sensor desciptions).
        """
        for receiver_index in range(receiver_info['num']):
            name, sensor_names = receiver_info['names'][receiver_index], receiver_info['sensor_names'][receiver_index]
            datalines_ = []
            for sensor_index in range(len(sensor_names)):
                pen = pg.mkPen(color=QColor(self.plot_view.settings['datalines_color'][receiver_index][sensor_index]),
                               style=getattr(Qt, self.plot_view.settings['datalines_style'][receiver_index][sensor_index]),
                               width=self.plot_view.settings['datalines_width'])
                data_line = self.plot([], [], name=name + ": " + sensor_names[sensor_index], pen=pen)
                datalines_.append(data_line)
                if self.plot_view.settings['datalines_active'][receiver_index][sensor_index]:
                    self.legend.addItem(data_line, data_line.name())
            self.datalines.append(datalines_)

    def add_landmarks(self, landmark_info):
        """
        Adds new landmarks to the plot.
        :param landmark_info: Info about landmarks (name + symbols).
        """
        for landmark_index in range(landmark_info['num']):
            landmark_ = self.plot([], [],
                                  pen=None,
                                  symbol=self.plot_view.settings['landmarks_symbols'][landmark_index],
                                  name=landmark_info['names'][landmark_index],
                                  symbolBrush=self.plot_view.settings['landmarks_color'][landmark_index],
                                  symbolSize=self.plot_view.settings['landmarks_size'])
            self.landmarks.append(landmark_)
            if self.plot_view.settings['landmarks_active'][landmark_index]:
                self.legend.addItem(landmark_, landmark_.name())

    def clear_(self):
        """
        Clears all data lines and landmark, removes all text items (symbol values) and vertical lines (symbol intervals).
        """
        for i in range(len(self.datalines)):
            for j in range(len(self.datalines[i])):
                self.datalines[i][j].clear()
        for i in range(len(self.additional_datalines)):
            self.additional_datalines[i].clear()
        for i in range(len(self.landmarks)):
            self.landmarks[i].clear()
        self.clear_symbol_intervals()
        self.clear_symbol_values()
        self.repaint_plot()

    def clear_additional_dataline(self, dataline_index):
        """
        Clears a given dataline.
        :param dataline_index: Index of the additional dataline to be cleared.
        """
        self.additional_datalines[dataline_index].clear()
        self.repaint_plot()

    def clear_dataline(self, receiver_index, sensor_index):
        """
        Clears a given dataline.
        :param receiver_index: Receiver index of the dataline to be cleared.
        :param sensor_index: Sensor index of the dataline to be cleared.
        """
        self.datalines[receiver_index][sensor_index].clear()
        self.repaint_plot()

    def clear_landmark(self, landmark_index):
        """
        Clears  a given landmark.
        :param landmark_index: Index of the landmark to be cleared.
        """
        self.landmarks[landmark_index].clear()
        self.repaint_plot()

    def clear_symbol_intervals(self):
        """
        Clears all symbol intervals (vertical lines) from the plot.
        """
        for i in self.vertical_lines:
            self.removeItem(i)
        self.vertical_lines = []

    def clear_symbol_values(self):
        """
        Clears all symbol values from the plot.
        """
        for text_item in self.text_items:
            self.removeItem(text_item)
        self.text_items = []

    def decoder_started(self):
        """
        Do stuff when decoder is (re-)started.
        """
        self.enableAutoRange()

    def export_plot(self):
        """
        Opens the export dialog.
        """
        self.e = exportDialog.ExportDialog(self.plotItem.scene())
        self.e.show(self.plotItem)

    def repaint_plot(self):
        """
        Repaints the plot.
        In some cases, the plot does not update its content, especially when elements are removed and the plot is not the focused window.
        In this case, the plot has to be updated manually.
        Note:   This is pretty ugly, potentially there is a more elegant way to do this.
                Using update, repaint, resize or QApplication.processEvents did not work.
        """
        self.hide()
        self.show()

    def reset_plot(self):
        """
        Clears the complete plot and resets variables.
        This function should be called before the starting of a decoder.
        """
        self.clear_()
        for i in range(len(self.datalines)):
            for j in range(len(self.datalines[i])):
                self.legend.removeItem(self.datalines[i][j])
        self.datalines = []
        for i in range(len(self.additional_datalines)):
            self.legend.removeItem(self.additional_datalines[i])
        self.additional_datalines = []
        for i in range(len(self.landmarks)):
            self.legend.removeItem(self.landmarks[i])
        self.landmarks = []
        self.repaint_plot()

    def set_additional_dataline_pen(self, dataline_index):
        """
        Sets a new pen for a given additional dataline based on the settings.
        :param dataline_index: Index of the additional dataline.
        """
        pen = pg.mkPen(color=self.plot_view.settings['additional_datalines_color'][dataline_index],
                       style=getattr(Qt, self.plot_view.settings['additional_datalines_style'][dataline_index]),
                       width=self.plot_view.settings['additional_datalines_width'])
        self.additional_datalines[dataline_index].setPen(pen)

    def set_additional_dataline_pens(self):
        """
        Updates the pens for all additional datalines.
        """
        for dataline_index in range(len(self.additional_datalines)):
            self.set_additional_dataline_pen(dataline_index)

    def set_landmark_pen(self, landmark_index):
        """
        Updates the pen for given landmark.
        :param landmark_index: Index of the landmark pen to be updated.
        """
        symbol = self.plot_view.settings['landmarks_symbols'][landmark_index]
        self.landmarks[landmark_index].setSymbol(symbol)
        self.landmarks[landmark_index].setSymbolSize(self.plot_view.settings['landmarks_size'])
        self.landmarks[landmark_index].setSymbolBrush(self.plot_view.settings['landmarks_color'][landmark_index])
        self.repaint_plot()

    def set_landmark_pens(self):
        """
        Updates all landmark pens.
        """
        for landmark_index in range(len(self.landmarks)):
            self.set_landmark_pen(landmark_index)

    def set_dataline_pen(self, receiver_index, sensor_index):
        """
        Sets a new pen for a given dataline based on the settings.
        :param receiver_index: Receiver index of the dataline.
        :param sensor_index: Sensor index of the dataline.
        """
        pen = pg.mkPen(color=self.plot_view.settings['datalines_color'][receiver_index][sensor_index],
                       style=getattr(Qt, self.plot_view.settings['datalines_style'][receiver_index][sensor_index]),
                       width=self.plot_view.settings['datalines_width'])
        self.datalines[receiver_index][sensor_index].setPen(pen)

    def set_dataline_pens(self):
        """
        Updates the pens for all datalines.
        """
        for receiver_index in range(len(self.datalines)):
            for sensor_index in range(len(self.datalines[receiver_index])):
                self.set_dataline_pen(receiver_index, sensor_index)

    def set_symbol_intervals_pen(self):
        """
        Updates the pen for the symbol intervals.
        """
        pen = pg.mkPen(color=self.plot_view.settings['symbol_intervals_color'], width=self.plot_view.settings['symbol_intervals_width'])
        for vertical_line in self.vertical_lines:
            vertical_line.setPen(pen)

    def set_symbol_values_size(self):
        """
        Updates the size of the symbol value text items.
        """
        font = QFont('MS Shell Dlg 2', self.plot_view.settings['symbol_values_size'])
        for text_item in self.text_items:
            text_item.setFont(font)

    def settings_updated(self):
        """
        Updates style elements according to the settings.
        This function is called after the plot settings have been reset to default.
        """
        self.set_dataline_pens()
        self.set_landmark_pens()
        self.set_symbol_intervals_pen()
        self.update_legend()

    def update_(self, decoded):
        """
        Updates this widget with new information from the decoder.
        :param decoded: Decoder value updates.
        """
        if self.autoscroll:
            diff = decoded['max_timestamp'] - decoded['min_timestamp'] - self.plot_view.settings['x_range_value']
            pos = int(round(SettingsStore.settings['SCROLLBAR_GRANULARITY'] * diff))
            self.plot_view.scrollbar.setSliderPosition(pos)

        received = decoded['received']
        additional_datalines = decoded['additional_datalines']
        landmarks = decoded['landmarks']
        symbol_intervals = decoded['symbol_intervals']
        symbol_values = decoded['symbol_values']
        self.update_datalines(received)
        self.update_additional_datalines(additional_datalines)
        self.update_landmarks(landmarks)
        self.update_symbol_intervals(symbol_intervals)
        self.update_symbol_values(received, symbol_intervals, symbol_values)

    def update_additional_datalines(self, additional_datalines):
        """
        Updates the additional datalines with new values from the decoder.
        :param additional_datalines: List of additional datalines.
        """
        for data_line_index in range(len(additional_datalines)):
            data_line = additional_datalines[data_line_index]
            if data_line is not None and self.plot_view.settings['additional_datalines_active'][data_line_index]:
                length = data_line['length']
                if length > 0:
                    timestamps = data_line['timestamps'][:length:self.plot_view.settings['step_size']]
                    values = data_line['values'][:length:self.plot_view.settings['step_size']]
                    self.additional_datalines[data_line_index].setData(timestamps, values)

    def update_datalines(self, received):
        """
        Updates the datalines with new values from the decoder.
        :param received: Measurement values from the receivers.
        """
        lengths, timestamps, values = received['lengths'], received['timestamps'], received['values']
        for receiver_index in range(len(values)):
            if lengths[receiver_index] > 0:
                for sensor_index in range(values[receiver_index].shape[1]):
                    if self.plot_view.settings['datalines_active'][receiver_index][sensor_index]:
                        length = lengths[receiver_index]
                        x = timestamps[receiver_index][:length:self.plot_view.settings['step_size']]
                        y = values[receiver_index][:length:self.plot_view.settings['step_size'], sensor_index]
                        self.datalines[receiver_index][sensor_index].setData(x, y)

    def update_landmarks(self, landmarks):
        """
        Updates the landmarks with new values from the decoder.
        :param landmarks: Landmark coordinates.
        """
        for landmark_index in range(len(landmarks)):
            if landmarks[landmark_index] is not None and self.plot_view.settings['landmarks_active'][landmark_index]:
                x, y = landmarks[landmark_index]['x'], landmarks[landmark_index]['y']
                self.landmarks[landmark_index].setData(x, y)

    def update_legend(self):
        """
        Updates the legend.
        This is usually necessary after a dataline or landmark set has been activated/deactivated.
        """
        self.legend.clear()
        for receiver_index in range(len(self.datalines)):
            for sensor_index in range(len(self.datalines[receiver_index])):
                if self.plot_view.settings['datalines_active'][receiver_index][sensor_index]:
                    self.legend.addItem(self.datalines[receiver_index][sensor_index], self.datalines[receiver_index][sensor_index].name())
        for landmark_index in range(len(self.landmarks)):
            if self.plot_view.settings['landmarks_active'][landmark_index]:
                self.legend.addItem(self.landmarks[landmark_index], self.landmarks[landmark_index].name())
        for dataline_index in range(len(self.additional_datalines)):
            if self.plot_view.settings['additional_datalines_active'][dataline_index]:
                self.legend.addItem(self.additional_datalines[dataline_index], self.additional_datalines[dataline_index].name())

    def update_symbol_intervals(self, symbol_intervals):
        """
        Updates the symbol intervals (vertical lines) with new values from the decoder.
        :param symbol_intervals: Symbol interval positions.
        """
        if self.plot_view.settings['symbol_intervals']:
            for timestamp in symbol_intervals[len(self.vertical_lines):]:
                #print("1")
                pen = pg.mkPen(color=self.plot_view.settings['symbol_intervals_color'],
                               width=self.plot_view.settings['symbol_intervals_width'])
                vertical = pg.InfiniteLine(pos=timestamp, angle=90, movable=False, pen=pen)
                self.addItem(vertical)
                self.vertical_lines.append(vertical)

    def update_symbol_values(self, vals, symbol_intervals, symbol_values):
        """
        Updates the symbol values with new values from the decoder.
        :param vals: Measurement values from the receivers (relevant for the y-position of the symbol values).
        :param symbol_intervals: Symbol interval positions (relevant for the x-position of the symbol values).
        :param symbol_values: Symbol values.
        """
        # This is necessary (for now), because symbol_values/symbol_intervals are not updated atomically
        symbol_values = symbol_values[:len(symbol_intervals) - 1]

        if self.plot_view.settings['symbol_values']:
            for i in range(len(self.text_items), len(symbol_values)):
                x_pos = 0.5 * (symbol_intervals[i] + symbol_intervals[i+1])

                if self.plot_view.settings['symbol_values_position'] in ['Above', 'Below']:
                    timestamps, values = vals['timestamps'], vals['values']
                    minimum_values, maximum_values = [], []
                    for receiver_index in range(len(timestamps)):

                        start_time = symbol_intervals[i]
                        end_time = symbol_intervals[i+1]

                        start_index = np.argmax(timestamps[receiver_index] > start_time)
                        end_index = np.argmax(timestamps[receiver_index] > end_time)

                        if start_index == end_index:
                            max_tmp = values[receiver_index][start_index]
                            min_tmp = values[receiver_index][start_index]
                        else:
                            max_tmp = np.max(values[receiver_index][start_index:end_index])
                            min_tmp = np.min(values[receiver_index][start_index:end_index])
                        maximum_values.append(max_tmp)
                        minimum_values.append(min_tmp)
                    maximum_interval_value = max(maximum_values)
                    minimum_interval_value = min(minimum_values)

                    if self.plot_view.settings['symbol_values_position'] == 'Above':
                        y_pos = maximum_interval_value + (0.1 + 0.001 * self.plot_view.settings['symbol_values_size']) #* np.abs(maximum_interval_value)
                    else:
                        y_pos = minimum_interval_value - (0.1 + 0.001 * self.plot_view.settings['symbol_values_size']) #* np.abs(minimum_interval_value)
                else:
                    y_pos = self.plot_view.settings['symbol_values_fixed_height']
                text = pg.TextItem(str(symbol_values[i]), color='k')
                text.setPos(x_pos, y_pos)
                text.setFont(QFont('MS Shell Dlg 2', self.plot_view.settings['symbol_values_size']))
                self.addItem(text)
                self.text_items.append(text)

    def update_x_range(self, scrollbar_value, enable_autoscroll):
        """
        Updates the X range of the plot.
        This function is called whenever the user moves the scrollbar or modifies the X range.
        :param scrollbar_value: Current value of the scrollbar.
        :param enable_autoscroll: Whether autoscroll should be resumed after updating the X range.
        """
        decoded = self.plot_view.data_view.view.controller.get_decoded()
        # Decoded may be None if there is no decoder yet or the decoder is not initialized yet
        if decoded is None:
            return
        # Disable the x range (which might still be active because of autoscroll)
        self.plotItem.setLimits(maxXRange=None, xMin=None)
        val = scrollbar_value / SettingsStore.settings['SCROLLBAR_GRANULARITY']
        min_timestamp = decoded['min_timestamp']
        left_ = min_timestamp + val
        self.setXRange(left_, left_ + self.plot_view.settings['x_range_value'])
        if enable_autoscroll:
            self.enableAutoRange()
        else:
            self.disableAutoRange()