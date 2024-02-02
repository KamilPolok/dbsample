"""
    This file collects all functions that are common for each ITrackedTab class.
"""

from PyQt6.QtGui import QFocusEvent, QKeyEvent, QRegularExpressionValidator
from PyQt6.QtCore import Qt, QRegularExpression, QTimer, pyqtSignal
from PyQt6.QtWidgets import  QHBoxLayout, QLabel, QLineEdit

from .TabIf import ITrackedTab

def create_data_input_row(tab: ITrackedTab, attribute: str, description: str, symbol: str) -> QHBoxLayout:
    """
    Create a row for data input with description, symbol, and input field.

    :param tab: The tab where the row will be added.
    :param attribute: The attribute name corresponding to the data.
    :param description: The description of the attribute.
    :param symbol: The symbol representing the attribute.
    :return: A QHBoxLayout containing the created widgets.
    """
    layout = QHBoxLayout()

    # Description label
    description_label = QLabel(description)
    description_label.setFixedWidth(150)
    description_label.setWordWrap(True)

    # Symbol label
    symbol_label = QLabel(f'{symbol} = ')
    symbol_label.setFixedWidth(50)

    # Line edit for input
    line_edit = LineEdit()
    line_edit.setFixedWidth(80)
    if (value := tab.tab_data[attribute][0]) is not None:
        line_edit.setText(str(value))

    # Input validation
    regex = QRegularExpression('^(0|[1-9][0-9]{0,6})(\.[0-9]{1,4})?$')
    line_edit.setValidator(QRegularExpressionValidator(regex, line_edit))

    # Units label
    units_label = QLabel(tab.tab_data[attribute][-1])
    units_label.setFixedWidth(50)

    # Assemble the layout
    layout.addWidget(description_label)
    layout.addWidget(symbol_label)
    layout.addWidget(line_edit)
    layout.addWidget(units_label)

    # Save the line_edit for later reference
    tab.input_values[attribute] = line_edit

    return layout

def create_data_display_row(tab: ITrackedTab, attribute: tuple, data: list, symbol: str, description: str = '') -> QHBoxLayout:
    """
    Create a row for displaying data with description, symbol, and a read-only field.

    :param tab: The tab where the row will be added.
    :param attribute: The attribute name corresponding to the data.
    :param data: The data list containing the value and unit.
    :param symbol: The symbol representing the attribute.
    :param description: The description of the attribute.
    :return: A QHBoxLayout containing the created widgets.
    """
    layout = QHBoxLayout()

    # Description label
    description_label = QLabel(description)
    description_label.setFixedWidth(150)
    description_label.setWordWrap(True)

    # Symbol label
    symbol_label = QLabel(f'{symbol} = ')
    symbol_label.setFixedWidth(50)

    # Value label (read-only)
    value_label = QLineEdit(format_value(data[0]) if data[0] is not None else '')
    value_label.setReadOnly(True)
    value_label.setFixedWidth(80)

    # Units label
    units_label = QLabel(data[-1])
    units_label.setFixedWidth(50)

    layout.addWidget(description_label)
    layout.addWidget(symbol_label)
    layout.addWidget(value_label)
    layout.addWidget(units_label)

    # Save the label for later reference
    tab.output_values[attribute] = value_label
    return layout

def format_value(var) -> str:
    """
    Format a variable for display.

    :param var: The variable to format.
    :return: A string representation of the variable.
    """
    return f'{var:.2f}' if isinstance(var, float) else str(var)

class LineEdit(QLineEdit):
    inputConfirmedSignal = pyqtSignal(object)

    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        self.inactivityTimer = QTimer()
        self.inactivityTimer.setInterval(1000)  # Timeout interval in ms
        self.inactivityTimer.setSingleShot(True)
        self.inactivityTimer.timeout.connect(self.on_inactivity)
        self.textEdited.connect(self.reset_inactivity_timer)

    def reset_inactivity_timer(self):
        if self.inactivityTimer.isActive():
            self.inactivityTimer.stop()
        self.inactivityTimer.start()

    def on_inactivity(self):
        self.inputConfirmedSignal.emit(self)

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.emit_inactivity_signal()

    def focusOutEvent(self, event: QFocusEvent):
        super().focusOutEvent(event)
        self.emit_inactivity_signal()

    def emit_inactivity_signal(self):
        if self.inactivityTimer.isActive():
            self.inactivityTimer.stop()
        self.inputConfirmedSignal.emit(self)
