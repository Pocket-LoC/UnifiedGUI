from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class ParameterDialog(QDialog):
    def __init__(self, parameters, current_values=None):
        super(ParameterDialog, self).__init__()

        self.setWindowTitle("Parameters")
        self.setWindowIcon(QIcon('./Views/Icons/tune.png'))

        self.values = {}
        self.widgets = []
        self.labels = []

        layout = QFormLayout()
        for i in range(len(parameters)):
            param = parameters[i]
            description = param['description']
            label = QLabel(description)
            type_ = param['dtype']
            w = None
            if type_ == 'bool':
                w = QCheckBox()
                w.setChecked(current_values[i] if current_values else param['default'])
            elif type_ == 'int':
                w = QSpinBox()
                w.setRange(param['min'], param['max'])
                w.setValue(current_values[i] if current_values else param['default'])
            elif type_ == 'float':
                w = QDoubleSpinBox()
                w.setRange(param['min'], param['max'])
                w.setValue(current_values[i] if current_values else param['default'])
                w.setDecimals(param['decimals'])
            elif type_ == 'item':
                w = QComboBox()
                w.addItems(param['items'])
                w.setCurrentIndex(param['items'].index(current_values[i] if current_values else param['default']))
            elif type_ == 'string':
                w = QLineEdit()
                w.setMaxLength(param['max_length'])
                w.setText(current_values[i] if current_values else param['default'])
            self.widgets.append((w, type_, description))
            if current_values is not None and 'editable' in list(param.keys()):
                w.setEnabled(param['editable'])
            if 'conversion_function' in list(param.keys()):
                label_text = description + " [" + str(param['conversion_function'](w.value())) + "]"
                label.setText(label_text)

                def lambda_value_changed(index, conversion_function):
                    return lambda: self.value_changed(index, conversion_function)

                w.valueChanged.connect(lambda_value_changed(i, param['conversion_function']))
            self.labels.append((description, label))
            layout.addRow(label, w)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def accept_(self):
        for w, t, description in self.widgets:
            value = None
            if t == 'bool':
                value = w.isChecked()
            elif t == 'int' or t == 'float':
                value = w.value()
            elif t == 'item':
                value = w.currentText()
            elif t == 'string':
                value = w.text()
            self.values[description] = value
        self.accept()

    def value_changed(self, index, conversion_function):
        current_value = self.widgets[index][0].value()
        conversion_result = str(conversion_function(current_value))

        description, label = self.labels[index]
        label.setText(description + " [" + conversion_result + "]")