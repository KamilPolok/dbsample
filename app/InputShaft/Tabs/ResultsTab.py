from PyQt6.QtWidgets import QVBoxLayout, QLabel, QScrollArea, QWidget

from .common.ITrackedTab import ITrackedTab
from .common.common_functions import create_data_display_row

class ResultsTab(ITrackedTab):
    def _view_results_section(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        self.main_layout.addWidget(scroll_area)

        content_layout.addWidget(QLabel('Ogólne:'))
        content_layout.addLayout(create_data_display_row(self, self._outputs['nwe'], 'n<sub>we</sub>', 'Wejściowa prędkość obrotowa', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['Mwe'], 'M<sub>we</sub>', 'Wejściowy moment obrotowy', decimal_precision=2))
        content_layout.addWidget(QLabel('Wymiary wału:'))
        content_layout.addLayout(create_data_display_row(self, self._outputs['L'], 'L', 'Długość wału czynnego', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['LA'], 'L<sub>A</sub>', 'Współrzędna podpory przesuwnej', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['LB'], 'L<sub>B</sub>', 'Współrzędna podpory stałej', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['L1'], 'L<sub>1</sub>', 'Współrzędna koła obiegowego nr 1', decimal_precision=2))
        for idx, input in enumerate(self._outputs['Lc'].values()):
            content_layout.addLayout(create_data_display_row(self, input, f'L<sub>{idx+2}</sub>', f'Współrzędna koła obiegowego nr {idx+2}', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['e'], 'e', 'Mimośród', decimal_precision=2))
        content_layout.addWidget(QLabel('Siły i reakcje:'))
        for idx, input in enumerate(self._outputs['Fx'].values()):
            content_layout.addLayout(create_data_display_row(self, input, f'R<sub>{idx+1}</sub>', f'Siła wywierana ze strony koła obiegowego nr {idx+1}', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['Ra'], 'R<sub>A</sub>', 'Reakcja podpory przesuwnej A', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['Rb'], 'R<sub>B</sub>', 'Reakcja podpory stałej B', decimal_precision=2))
        content_layout.addWidget(QLabel('Straty mocy w łożyskach:'))
        content_layout.addLayout(create_data_display_row(self, self._outputs['Bearings']['support_A']['P'], 'P<sub>A</sub>', 'Podpora przesuwna A', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['Bearings']['support_B']['P'], 'P<sub>B</sub>', 'Podpora stała B', decimal_precision=2))
        content_layout.addLayout(create_data_display_row(self, self._outputs['Bearings']['eccentrics']['P'], 'P<sub>c</sub>', 'Wykorbienia', decimal_precision=2))
        super().init_ui()

    def init_ui(self, outputs):
        """
        Initialize the user interface for ResultsTab.

        Args:
            outputs (dict): Outputs
        """
        self._outputs = outputs
        
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self._view_results_section()
        super().init_ui()
