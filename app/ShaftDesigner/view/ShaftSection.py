
from abc import ABC, ABCMeta, abstractmethod
from ast import literal_eval

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QSizePolicy

from .CommonFunctions import create_data_input_row, format_input
from .ShaftSubsection import ShaftSubsection

class ABCQWidgetMeta(ABCMeta, type(QWidget)):
    pass
class Section(QWidget, metaclass=ABCQWidgetMeta):
    subsection_data_signal = pyqtSignal(tuple)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.subsections = []
        self.subsection_count = 0

        self._init_ui()

    def _init_ui(self):
        # Main layout
        self.main_layout = QVBoxLayout(self)

        self._init_header()
        self._init_subsections()

        # Initially collapse Section widget
        self.expanded = True
        self.toggle(None)
    
    def _init_header(self):
        # Header layout
        self.header_layout = QHBoxLayout()

        # Set header
        self.header = QLabel(self.name)
        self.header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header.setFixedHeight(30)
        self.header.mousePressEvent = self.toggle
        self.header_layout.addWidget(self.header)

        # Add header layout to main layout
        self.main_layout.addLayout(self.header_layout)
    
    def _init_subsections(self):
        # Subsections layout
        self.subsections_layout = QVBoxLayout()
        self.subsections_container = QFrame()
        self.subsections_container.setLayout(self.subsections_layout)
        self.main_layout.addWidget(self.subsections_container)

    def toggle(self, event):
        # Expand or collapse the widget
        self.expanded = not self.expanded
        self.subsections_container.setVisible(self.expanded)

    @abstractmethod
    def handle_subsection_data(self, data):
        pass

class ShaftSection(Section):
    add_subsection_signal = pyqtSignal()
    remove_subsection_plot_signal = pyqtSignal(str, int)
    
    def _init_header(self):
        super()._init_header()
        # Set add subsection button
        self.add_subsection_button = QPushButton("+", self)
        self.add_subsection_button.clicked.connect(self.add_subsection)
        self.add_subsection_button.setFixedWidth(30)
        self.header_layout.addWidget(self.add_subsection_button)

    def add_subsection(self):
        subsection = ShaftSubsection(self.name, self.subsection_count, self)
        subsection.set_attributes([('d', 'Ø'), ('l', 'L')])
        subsection.subsection_data_signal.connect(self.handle_subsection_data)
        subsection.remove_subsection_signal.connect(self.remove_subsection)
        self.subsections.append(subsection)
        self.subsections_layout.addWidget(subsection)
        self.subsection_count += 1
        self.set_add_subsection_button_enabled(False)
        self.add_subsection_signal.emit()

    def remove_subsections(self, subsections_number):
        # Find and remove the specific subsection
        for subsection_number in range(self.subsection_count, subsections_number, -1):
            subsection_to_remove = next((s for s in self.subsections if s.subsection_number == subsection_number), None)
            if subsection_to_remove:
                self.subsections_layout.removeWidget(subsection_to_remove)
                subsection_to_remove.deleteLater()
                self.subsections.pop()
                self.subsection_count -= 1

    def remove_subsection(self, subsection_number):
        # Find and remove the specific subsection
        subsection_to_remove = self.sender()
        self.subsections_layout.removeWidget(subsection_to_remove)
        subsection_to_remove.deleteLater()
        self.subsections = [s for s in self.subsections if s != subsection_to_remove]
    
        # Update the numbers and names of the remaining subsections
        for i, subsection in enumerate(self.subsections):
            subsection.update_subsection_name(i)

        # Update the subsection count
        self.subsection_count -= 1
        
        self.remove_subsection_plot_signal.emit(self.name, subsection_number)

    def set_limits(self, limits):
        for subsection_number, attributes in limits.items():
            self.subsections[subsection_number].set_limits(attributes)
    
    def set_add_subsection_button_enabled(self, enabled):
        self.add_subsection_button.setEnabled(enabled)
    
    def toggle(self, event):
        super().toggle(event)
        self.add_subsection_button.setVisible(self.expanded)

    def handle_subsection_data(self, subsection_data):
        subsection = self.sender()
        common_section_data = None
        data = (self.name, subsection.subsection_number, subsection_data, common_section_data)
        self.subsection_data_signal.emit(data)

class EccentricsSection(Section):
    def _init_subsections(self):
        # Set subsections layout
        self.subsections_layout = QVBoxLayout()
        self.subsections_container = QFrame()
        self.subsections_container.setLayout(self.subsections_layout)
        self.main_layout.addWidget(self.subsections_container)

        # Set data entries
        self.inputs = {}
        
        attribute, symbol = ('d', 'Ø')
        attribute_row, input = create_data_input_row(symbol)
        self.subsections_layout.addLayout(attribute_row)
        
        self.inputs[attribute] = input

    def set_subsections_number(self, sections_number):
        if self.subsection_count != sections_number:
            for _ in range(self.subsection_count, sections_number):
                subsection = ShaftSubsection(self.name, self.subsection_count, self)
                subsection.set_attributes([('l', 'L')])
                for attribute, input in self.inputs.items():
                    subsection.add_input(attribute, input)
                subsection.remove_button.hide()
                subsection.subsection_data_signal.connect(self.handle_subsection_data)
                self.subsections.append(subsection)
                self.subsections_layout.addWidget(subsection)
                self.subsection_count += 1
    
    def set_limits(self, limits):
        for subsection_number, attributes in limits.items():
            self.subsections[subsection_number].set_limits(attributes)

    def handle_subsection_data(self, subsection_data):
        subsection = self.sender()
        common_section_data = {key: literal_eval(input.text()) for key, input in self.inputs.items()}
        data = (self.name, subsection.subsection_number, subsection_data, common_section_data)
        self.subsection_data_signal.emit(data)
