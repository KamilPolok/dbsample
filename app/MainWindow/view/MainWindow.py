from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton

class MainWindow(QMainWindow):
    """
    Main window class for the application.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def set_data(self, data):
        """
        Set data needed for or from GUI.
        """
        self.data = data

    def set_chart_data(self, data):
        """
        Set data for the chart tab.
        """
        self.tabs[2].create_plots(data)

    def init_ui(self):
        """
        Initialize the user interface.
        """
        self.setWindowTitle('CycloDesign')
        self._tab_widget = QTabWidget(self)
        self.setCentralWidget(self._tab_widget)
    
    def init_tabs(self):
        from .Tabs.BearingsTab import BearingsTab
        from .Tabs.PreliminaryDataTab import PreliminaryDataTab
        from .Tabs.ResultsTab import ResultsTab
        """
        Initialize tabs in the main window.
        """
        self.tabs = []

        # Add tabs
        tab1 = PreliminaryDataTab(self, self.update_access_to_next_tabs)
        self.tabs.append(tab1)
        self._tab_widget.addTab(tab1, 'Założenia wstępne')

        tab2 = BearingsTab(self, self.update_access_to_next_tabs)
        self.tabs.append(tab2)
        self._tab_widget.addTab(tab2, 'Dobór łożysk')

        tab3 = ResultsTab(self, self.update_access_to_next_tabs)
        self.tabs.append(tab3)
        self._tab_widget.addTab(tab3, 'Wyniki obliczeń')

        # Disable all tabs except the first one
        for i in range(1, self._tab_widget.count()):
            self._tab_widget.setTabEnabled(i, False)

        self._tab_widget.currentChanged.connect(self.on_tab_change)

        # Add next tab button below the tabs
        self._next_tab_button = QPushButton('Dalej', self)
        self._next_tab_button.clicked.connect(self.next_tab)

        layout = QVBoxLayout()

        layout.addWidget(self._tab_widget)
        layout.addWidget(self._next_tab_button)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Check if the tab is initially filled
        self.tabs[self._tab_widget.currentIndex()].check_state()

    def next_tab(self):
        """
        Move to the next tab.
        """
        current_index = self._tab_widget.currentIndex()
        next_index = current_index + 1

        # Check if current tab is not the last one
        if next_index < self._tab_widget.count():
            # Enable next tab if it wasn't anabled earlier
            if not self._tab_widget.isTabEnabled(next_index):
                self._tab_widget.setTabEnabled(next_index, True)
            # Update data with curret tab data
            self.tabs[current_index].update_data()
            self._tab_widget.setCurrentIndex(next_index)

    def on_tab_change(self, index):
        """
        Handle tab change event.
        """
        # Check if all the inputs are provided
        self.tabs[index].check_state()
        # Update tab GUI
        self.tabs[index].update_tab()
        
    def update_access_to_next_tabs(self, enable_next_tab_button=False, disable_next_tabs=False):
        """
        Check and update the state of the next tab button.
        """
        if enable_next_tab_button:
            self._next_tab_button.setEnabled(True)
        else:
            self._next_tab_button.setEnabled(False)

        if disable_next_tabs:
            self.disable_next_tabs()

    def disable_next_tabs(self):
        """
        Disable all tabs following the current tab.
        """
        for i in range(self._tab_widget.currentIndex() + 1, self._tab_widget.count()):
            self._tab_widget.setTabEnabled(i, False)
