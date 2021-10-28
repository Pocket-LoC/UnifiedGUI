from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
from Views import EncoderView, DecoderView, DataView, ToolbarView


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

        self.toolbar = ToolbarView.ToolbarView()
        self.addToolBar(self.toolbar)

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
        # TODO
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.update_values)
        self.timer.start()

    def update_values(self):
        received = self.controller.get_received()
        if received is not None:
            self.data_view.update_values(received)

        symbol_intervals = self.controller.get_symbol_intervals()
        if symbol_intervals is not None:
            self.data_view.update_symbol_intervals(symbol_intervals)

        symbol_values = self.controller.get_symbol_values()
        if symbol_intervals is not None and symbol_values is not None:
            self.data_view.update_symbol_values(symbol_intervals, symbol_values)

    def decoder_added(self, receiver_info):
        # TODO: Update decoder view
        # Update data view
        self.data_view.add_receivers(receiver_info)

    def decoder_removed(self):
        # TODO
        pass

    def closeEvent(self, close_event: QCloseEvent):
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