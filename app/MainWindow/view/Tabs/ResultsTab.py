from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QScrollArea

from .TabIf import Tab
from .TabCommon import create_data_display_row, format_value
from .ChartView import Chart

class ResultsTab(Tab):
    def init_ui(self):
        """
        Initialize the user interface for ResultsTab.
        """
        self.setLayout(QVBoxLayout())
        
        self._subtab_widget = QTabWidget(self)
        self.layout().addWidget(self._subtab_widget)

        self.add_data_subtab()
        self.add_results_subtab()
        self.add_chart_subtab()

    def add_data_subtab(self):
        """
        Add a subtab for displaying data.
        """
        subtab = QScrollArea()
        subtab.setWidgetResizable(True)
        self._subtab_widget.addTab(subtab, 'Dane')

        content_widget = QWidget()
        self.data_subtab_layout = QVBoxLayout(content_widget)
        subtab.setWidget(content_widget)

        generalDataLabel = QLabel('Ogólne:')
        nwe = create_data_display_row(self, 'nwe', self._window.data['nwe'], 'n<sub>we</sub>', 'Prędkość obrotowa wejściowa')
        mwe = create_data_display_row(self, 'Mwe', self._window.data['Mwe'], 'M<sub>we</sub>', 'Moment obrotowy wejściowy')
        dimensionsLabel = QLabel('Wymiary:')
        length = create_data_display_row(self, 'L',  self._window.data['L'], 'L', 'Długość wału wejściowego',)
        rollerSupport = create_data_display_row(self, 'LA', self._window.data['LA'], 'L<sub>A</sub>', 'Współrzędne podpory przesuwnej',)
        pinSupport = create_data_display_row(self, 'LB', self._window.data['LB'], 'L<sub>B</sub>', 'Współrzędne podpory nieprzesuwnej')
        e = create_data_display_row(self, 'e',  self._window.data['e'], 'e', 'Mimośród')
        cycloDiscCoordinatesLabel = QLabel('Współrzędne kół obiegowych:')
        cycloDisc1 = create_data_display_row(self, 'L1', self._window.data['L1'], 'L<sub>1</sub>', 'Koło obiegowe 1')
        cycloDisc2 = create_data_display_row(self, 'L2', self._window.data['L2'], 'L<sub>2</sub>', 'Koło obiegowe 2')
        materialsLabel = QLabel('Materiał:')
        
        self.data_subtab_layout.addWidget(generalDataLabel)
        self.data_subtab_layout.addLayout(nwe)
        self.data_subtab_layout.addLayout(mwe)
        self.data_subtab_layout.addWidget(dimensionsLabel)
        self.data_subtab_layout.addLayout(length)
        self.data_subtab_layout.addLayout(rollerSupport)
        self.data_subtab_layout.addLayout(pinSupport)
        self.data_subtab_layout.addLayout(e)
        self.data_subtab_layout.addWidget(cycloDiscCoordinatesLabel)
        self.data_subtab_layout.addLayout(cycloDisc1)
        self.data_subtab_layout.addLayout(cycloDisc2)
        self.data_subtab_layout.addWidget(materialsLabel)

    def add_results_subtab(self):
        """
        Add a subtab for displaying results.
        """
        subtab = QScrollArea()
        subtab.setWidgetResizable(True)
        self._subtab_widget.addTab(subtab, 'Wyniki')

        content_widget = QWidget()
        self.results_subtab_layout = QVBoxLayout(content_widget)
        subtab.setWidget(content_widget)

        dimensionsLabel = QLabel('Wymiary')
        ds = create_data_display_row(self, 'ds',  self._window.data['ds'], 'd<sub>s</sub>', 'Średnica wału')
        de = create_data_display_row(self, 'de',  self._window.data['de'], 'd<sub>e</sub>', 'Średnica wykorbienia')

        Łożyska1 = QLabel('Łożyska')

        self.results_subtab_layout.addWidget(dimensionsLabel)
        self.results_subtab_layout.addLayout(ds)
        self.results_subtab_layout.addLayout(de)
        self.results_subtab_layout.addWidget(Łożyska1)

    def add_chart_subtab(self):
        """
        Add a subtab for displaying charts.
        """
        self._chart_tab = Chart()
        self._subtab_widget.addTab(self._chart_tab, 'Wykresy')
    
    def create_plots(self, chart_data):
        """
        Create plots in the chart tab.

        :param chart_data: Data to be used for plotting.
        """
        self._chart_tab.create_plots(chart_data)

    def update_tab(self):

        addData = True 
        for key_tuple, value_label in self.output_values.items():
            # Check if the key is a tuple (indicating a parent-child relationship)
            if isinstance(key_tuple, tuple):
                parent_key, attribute = key_tuple
                if parent_key in self._window.data and attribute in self._window.data[parent_key]:
                    addData = False
                    new_value = self._window.data[parent_key][attribute][0]
                    value_label.setText(format_value(new_value))
            else:
                # Handle keys without a parent
                attribute = key_tuple
                if attribute in self._window.data:
                    new_value = self._window.data[attribute][0]
                    value_label.setText(format_value(new_value))
            
        if addData:
            for key, value in self._window.data['Materiał'].items():
                attribute = create_data_display_row(self, ('Materiał', key), value, key)
                self.data_subtab_layout.addLayout(attribute)
            for key, value in self._window.data['Łożyska_podporowe'].items():
                attribute = create_data_display_row(self, ('Łożyska_podporowe', key), value, key)
                self.results_subtab_layout.addLayout(attribute)
            for key, value in self._window.data['Łożyska_centralne'].items():
                attribute = create_data_display_row(self, ('Łożyska_centralne', key), value, key)
                self.results_subtab_layout.addLayout(attribute)
