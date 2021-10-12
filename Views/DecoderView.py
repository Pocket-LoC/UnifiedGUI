from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os


class DecoderView(QWidget):
    def __init__(self, main_view):
        super().__init__()

        self.main_view = main_view

        # Get a list of all available decoders by searching for .py files in the implementations folder
        self.available_decoders = []
        for file in os.listdir('./Models/Implementations/Decoders'):
            name, extension = os.path.splitext(file)
            if extension == '.py':
                self.available_decoders.append(name)

        self.layout = QVBoxLayout()

        self.toolbar = QToolBar()

        self.button_add_decoder = QToolButton()
        self.button_add_decoder.setText("Add Decoder")
        self.button_add_decoder.setIcon(QIcon('./Views/Icons/2x/add.png'))
        self.button_add_decoder.clicked.connect(self.add_decoder)
        self.toolbar.addWidget(self.button_add_decoder)

        self.button_remove_decoder = QToolButton()
        self.button_remove_decoder.setText("Remove Decoder")
        self.button_remove_decoder.setEnabled(False)
        self.button_remove_decoder.clicked.connect(self.remove_decoder)
        self.toolbar.addWidget(self.button_remove_decoder)

        self.button_start_decoder = QToolButton()
        self.button_start_decoder.setText("Start Decoder")
        self.button_start_decoder.setEnabled(False)
        self.button_start_decoder.clicked.connect(self.start_decoder)
        self.toolbar.addWidget(self.button_start_decoder)

        self.button_stop_decoder = QToolButton()
        self.button_stop_decoder.setText("Stop Decoder")
        self.button_stop_decoder.setEnabled(False)
        self.button_stop_decoder.clicked.connect(self.stop_decoder)
        self.toolbar.addWidget(self.button_stop_decoder)

        label = QLabel("Decoder")
        self.layout.addWidget(self.toolbar)
        self.layout.addStretch(1)
        self.layout.addWidget(label)

        self.setLayout(self.layout)

    def add_decoder(self):
        decoder_type, ok = QInputDialog.getItem(self, "Add Decoder", "Decoder type", self.available_decoders, 0, False)
        if ok:
            self.main_view.controller.add_decoder(decoder_type)

    def remove_decoder(self):
        self.main_view.controller.remove_decoder()

    def start_decoder(self):
        self.main_view.controller.start_decoder()

    def stop_decoder(self):
        # TODO: Confirmation window
        self.main_view.controller.stop_decoder()

    def decoder_added(self):
        # TODO: Add information about decoder and receivers in the GUI
        self.label = QLabel("Blabla")
        self.layout.addWidget(self.label)

        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(True)
        self.button_stop_decoder.setEnabled(False)

    def decoder_removed(self):
        self.button_add_decoder.setEnabled(True)
        self.button_remove_decoder.setEnabled(False)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(False)

    def decoder_started(self):
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(False)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(True)

    def decoder_stopped(self):
        self.button_add_decoder.setEnabled(False)
        self.button_remove_decoder.setEnabled(True)
        self.button_start_decoder.setEnabled(False)
        self.button_stop_decoder.setEnabled(False)