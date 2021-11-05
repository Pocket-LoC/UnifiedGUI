from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import time
from Views import EncoderView, DecoderView, DataView, MenuBarView, ToolbarView, StatusBarView


class View(QMainWindow):
    def __init__(self, controller):
        super(View, self).__init__()

        self.controller = controller

        # Window Title and icon
        self.setWindowTitle("UnifiedGUI")
        icon_window = self.style().standardIcon(getattr(QStyle, 'SP_TitleBarMenuButton'))
        self.setWindowIcon(icon_window)

        # Set window size to maximum
        self.setWindowState(Qt.WindowMaximized)

        # Menu bar
        self.menu_bar = MenuBarView.MenuBarView(self)
        self.setMenuBar(self.menu_bar)

        self.toolbar = ToolbarView.ToolbarView()
        self.addToolBar(self.toolbar)

        self.status_bar = StatusBarView.StatusBarView()
        self.setStatusBar(self.status_bar)

        central_widget = QWidget(self)

        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        self.encoder_view = EncoderView.EncoderView()
        self.data_view = DataView.DataView()
        self.decoder_view = DecoderView.DecoderView(self)

        splitter.addWidget(self.encoder_view)
        splitter.addWidget(self.data_view)
        splitter.addWidget(self.decoder_view)

        layout.addWidget(splitter)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.timer = QTimer()
        # A QTimer with a timeout of 0 will time out as soon as possible.
        self.timer.setInterval(0)
        self.timer.timeout.connect(self.update_values)
        self.timer.start()

        self.last_time = time.time()
        self.last_fps = []

    def update_values(self):
        decoded = self.controller.get_decoded()
        if decoded is not None:
            received, landmarks, symbol_intervals, symbol_values, sequence = decoded['received'], decoded['landmarks'], decoded['symbol_intervals'], decoded['symbol_values'], decoded['sequence']

            self.data_view.update_values(received)
            self.data_view.update_landmarks(landmarks)
            self.data_view.update_symbol_intervals(symbol_intervals)
            self.data_view.update_symbol_values(symbol_intervals, symbol_values)

            self.decoder_view.update_symbol_values(symbol_values)
            self.decoder_view.update_sequence(sequence)

        # TODO: FPS calculation
        time_ = time.time()
        time_difference = time_ - self.last_time + 0.0000001
        fps = 1 / time_difference
        self.last_fps.append(fps)
        if len(self.last_fps) == 10:
            fps_avg = int(np.round(sum(self.last_fps) / len(self.last_fps)))
            self.status_bar.set_fps(fps_avg)
            self.last_fps = []
        self.last_time = time_

    def decoder_added(self, decoder_type, receiver_info, landmark_info):
        # Update decoder view
        self.decoder_view.decoder_added(decoder_type)

        # Update data view
        self.data_view.decoder_added(receiver_info, landmark_info)

    def decoder_removed(self):
        self.data_view.decoder_removed()
        self.decoder_view.decoder_removed()

    def closeEvent(self, close_event: QCloseEvent):
        # TODO: Refactor
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        icon_msg = self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxQuestion'))
        msg.setWindowIcon(icon_msg)
        msg.setText("Are you sure you want to exit?")
        msg.setWindowTitle("Exit?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        ret = msg.exec()
        if ret == QMessageBox.Yes:
            self.controller.close()
            close_event.accept()
        else:
            close_event.ignore()