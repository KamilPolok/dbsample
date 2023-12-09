import math
import numpy as np
from sympy import symbols, Piecewise

from MainWindow.view import MainWindow

from DbHandler.controller.DBController import ViewSelectItemController
from DbHandler.model.DatabaseHandler import DatabaseHandler
from DbHandler.view.Window import Window

class MainWindowController:
    """
    Controller for the MainWindow in the application.

    This class handles the interactions between the model (data) and the view (MainWindow),
    including initializing the view with data, connecting signals and slots, and handling
    user interactions.
    """

    def __init__(self, model, view: MainWindow):
        """
        Initialize the MainWindowController.

        :param model: The data model for the application.
        :param view: The MainWindow instance of the application.
        """
        self._window = view
        self._data = model
        self._startup()
        self._connect_signals_and_slots()

    def _startup(self):
        """Initialize the view with necessary data and set up tabs."""
        self._window.set_data(self._data)
        self._window.init_tabs()

    def _connect_signals_and_slots(self):
        """
        Connect signals and slots for interactivity in the application.

        This method sets up connections between UI elements and their corresponding
        actions or handlers.
        """
        self._window.tabs[0].select_material_button.clicked.connect(self._open_materials_db_window)
        self._window.tabs[0].updated_data_signal.connect(self._calculate_input_shaft_attributes)
        self._window.tabs[1].updated_support_bearings_data_signal.connect(self._open_support_bearings_db_window)
        self._window.tabs[1].updated_central_bearings_data_signal.connect(self._open_central_bearings_db_window)
        self._window.tabs[1].updated_data_signal.connect(self._calculate_bearings_attributes)
        self._window.tabs[2].updated_support_bearings_rolling_element_data_signal.connect(self._open_support_bearings_rolling_elements_db_window)
        self._window.tabs[2].updated_central_bearings_rolling_element_data_signal.connect(self._open_central_bearings_rolling_elements_db_window)
        self._window.tabs[2].updated_data_signal.connect(self._calculate_power_loss)

    def _open_materials_db_window(self):
        """
        Open the materials database window.

        This method is triggered when the user wants to select a material from the database.
        """
        db_handler = DatabaseHandler()
        subwindow = Window()
        subwindow.setWindowTitle("Dobór materiału")
        tables_group_name = 'wał wejściowy-materiały'
        available_tables = db_handler.getAvailableTables(tables_group_name)
        limits = db_handler.getTableItemsFilters(tables_group_name)
        view_select_items_ctrl = ViewSelectItemController(db_handler, subwindow, available_tables, limits)
        subwindow.itemDataSignal.connect(self._window.tabs[0].update_viewed_material)
        subwindow.exec()
    
    def _open_support_bearings_db_window(self, data):
        """
        Open the support bearings database _window.

        This method is triggered when the user wants to select a support bearing from the database.
        It first calculates bearing attributes based on provided data.

        :param data: Data used for calculating bearing attributes.
        """
        self._calculate_support_bearings_load_capacity(data)

        # Get acces to the database
        db_handler = DatabaseHandler()
        # Create a subwindow that views GUI for the DatabaseHandler
        subwindow = Window()
        subwindow.setWindowTitle("Dobór łożyska podporowego")
        # Specify the group name of the tables you want to take for consideration
        tables_group_name = 'wał wejściowy-łożyska-podporowe'
        available_tables = db_handler.getAvailableTables(tables_group_name)
        # Specify the limits for the group of tables
        limits = db_handler.getTableItemsFilters(tables_group_name)
        limits['Dw']['min'] = self._data['dsc'][0]
        limits['C']['min'] = self._data['Cr'][0]
        # Setup the controller for the subwindow
        view_select_items_ctrl = ViewSelectItemController(db_handler, subwindow, available_tables, limits)
        subwindow.itemDataSignal.connect(self._window.tabs[1].update_viewed_support_bearings_code)
        subwindow.exec()
    
    def _open_central_bearings_db_window(self, data):
        """
        Open the central bearings database _window.

        This method is triggered when the user wants to select a central bearing from the database.
        It first calculates bearing attributes based on provided data.

        :param data: Data used for calculating bearing attributes.
        """
        self._calculate_central_bearings_load_capacity(data)

        # # Get acces to the database
        db_handler = DatabaseHandler()
        # Create a subwindow that views GUI for the DatabaseHandler
        subwindow = Window()
        subwindow.setWindowTitle("Dobór łożyska centralnego")
        # Specify the group name of the tables you want to take for consideration
        tables_group_name = 'wał wejściowy-łożyska-centralne'
        available_tables = db_handler.getAvailableTables(tables_group_name)
        # Specify the limits for the group of tables
        limits = db_handler.getTableItemsFilters(tables_group_name)
        limits['Dw']['min'] = self._data['dec'][0]
        limits['C']['min'] = self._data['Cc'][0]
        # Setup the controller for the subwindow
        view_select_items_ctrl = ViewSelectItemController(db_handler, subwindow, available_tables, limits)
        subwindow.itemDataSignal.connect(self._window.tabs[1].update_viewed_central_bearings_code)
        subwindow.exec()

    def _open_support_bearings_rolling_elements_db_window(self, data):
        """
        Open the support bearings rolling_elements database window.

        This method is triggered when the user wants to select rolling elements for a support bearing from the database.
        It first calculates rolling elements attributes based on provided data.

        :param data: Data used for calculating bearing diameter.
        """
        # Get acces to the database
        db_handler = DatabaseHandler()
        # Create a subwindow that views GUI for the DatabaseHandler
        subwindow = Window()
        subwindow.setWindowTitle("Dobór elementu tocznego")
        # Specify the group name of the tables you want to take for consideration
        tables_group_name = f"wał wejściowy-elementy toczne-{self._data['Łożyska_podporowe']['elementy toczne'][0]}"
        available_tables = db_handler.getAvailableTables(tables_group_name)
        # Specify the limits for the group of tables
        limits = db_handler.getTableItemsFilters(tables_group_name)
        limits['D']['min'] = math.floor(self._data['dwpc'][0]) - 1
        limits['D']['max'] = math.ceil(self._data['dwpc'][0]) + 1
        # Setup the controller for the subwindow
        view_select_items_ctrl = ViewSelectItemController(db_handler, subwindow, available_tables, limits)
        subwindow.itemDataSignal.connect(self._window.tabs[2].update_viewed_support_bearings_rolling_element_code)
        subwindow.exec()

    def _open_central_bearings_rolling_elements_db_window(self, data):
        """
        Open the central bearings rolling_elements database window.

        This method is triggered when the user wants to select rolling elements for a central bearing from the database.
        It first calculates rolling elements attributes based on provided data.

        :param data: Data used for calculating bearing diameter.
        """
        # Get acces to the database
        db_handler = DatabaseHandler()
        # Create a subwindow that views GUI for the DatabaseHandler
        subwindow = Window()
        subwindow.setWindowTitle("Dobór elementu tocznego")
        # Specify the group name of the tables you want to take for consideration
        tables_group_name = f"wał wejściowy-elementy toczne-{self._data['Łożyska_centralne']['elementy toczne'][0]}"
        available_tables = db_handler.getAvailableTables(tables_group_name)
        # Specify the limits for the group of tables
        limits = db_handler.getTableItemsFilters(tables_group_name)
        limits['D']['min'] = math.floor(self._data['dwcc'][0]) - 1
        limits['D']['max'] = math.ceil(self._data['dwcc'][0]) + 1
        # Setup the controller for the subwindow
        view_select_items_ctrl = ViewSelectItemController(db_handler, subwindow, available_tables, limits)
        subwindow.itemDataSignal.connect(self._window.tabs[2].update_viewed_central_bearings_rolling_element_code)
        subwindow.exec()

    def _calculate_support_bearings_load_capacity(self, data):
        """
        Calculate load capacity of the support bearings.

        This method calculates the life and capacity of the first set of bearings based on the provided data.

        :param data: Data used for calculating bearing attributes.
        """
        self._update_data(data)

        nwe = self._data['nwe'][0]
        lh = self._data['Lhp'][0]
        fd = self._data['fdp'][0]
        ft = self._data['ftp'][0]
        p = 3.0

        ra = self._data['Ra'][0]

        l = 60 * lh * nwe / np.power(10, 6)
        c = ra * np.power(l, 1 / p) * ft / fd / 1000 # [kN]

        self._data['Lrp'][0] = l
        self._data['Cr'][0] = c
    
    def _calculate_central_bearings_load_capacity(self, data):
        """
        Calculate load capacity of central bearings.

        This method calculates the life and capacity of the second set of bearings based on the provided data.

        :param data: Data used for calculating bearing attributes.
        """
        self._update_data(data)

        nwe = self._data['nwe'][0]
        lh = self._data['Lhc'][0]
        fd = self._data['fdc'][0]
        ft = self._data['ftc'][0]
        p = 3.0

        f = self._data['F'][0]

        l = 60 * lh * nwe / np.power(10, 6)
        c = f * np.power(l, 1 / p) * ft / fd/ 1000 # [kN]

        self._data['Ltc'][0] = l
        self._data['Cc'][0] = c
         
    def _calculate_input_shaft_attributes(self, data):
        """
        Calculate attributes for the input shaft.

        This method updates the model with new data and calculates various attributes
        for the input shaft, including bending moments, torques, and shaft diameters.

        :param data: Data used for calculating input shaft attributes.
        """
        self._update_data(data)

        # Extract necessary data from the model
        L, L1,= self._data['L'][0], self._data['L1'][0]
        x, e, B = self._data['x'][0], self._data['e'][0], self._data['B'][0]
        F, Mwe = self._data['F'][0], self._data['Mwe'][0]
        Zgo, xz = self._data['Materiał']['Zgo'][0], self._data['xz'][0]

        # Calculate coordinate of second cyclo disc
        L2 = L1 + B + x

        # Calculate support reactions
        Rb = (F * (L2 - L1)) / L  # Pin support
        Ra = Rb                   # Roller support

       # Create Force and reaction list
        FVals = [Ra, F, F, Rb]

        # Create z arguments for chart data
        key_points = [0, L1, L2, L]
        z = symbols('z')
        zVals = np.union1d(key_points, np.linspace(0, L, 100))

        # Calculate bending moment Mg [Nm]                           
        MgA_1 = Ra * z * 0.001
        Mg1_2 = (Ra * z - F * (z - L1)) * 0.001
        Mg2_B = ((Ra * z - F * (z - L1)) + F * (z - L2)) * 0.001

        MgFunction = Piecewise(
            (MgA_1, z < L1),
            (Mg1_2, z < L2),
            (Mg2_B, z <= L)
        )
        Mg = np.array([round(float(MgFunction.subs(z, val).evalf()), 2) for val in zVals])

        # Calculate torque Ms
        MsFunction = Piecewise(
            (0, z < L1),
            (Mwe, z <= L),
            
        )
        Ms = np.array([round(float(MsFunction.subs(z, val).evalf()), 2) for val in zVals])

        # Calculate equivalent moment Mz
        reductionFactor = 2 * np.sqrt(3)
        Mz = np.sqrt(np.power(Mg, 2) + np.power(reductionFactor / 2 * Ms, 2))
        Mz = np.array([round(float(val), 2) for val in Mz])

        # Calculate shaft diameter d
        kgo = Zgo / xz
        d = np.power(32 * Mz / (np.pi * kgo * 1000000), 1/3) * 1000
        d = np.array([round(float(val), 2) for val in d])

        # Save the calculated parameters
        self._data['L2'][0] = L2
        self._data['dsc'][0] = max(d)
        self._data['dec'][0] = max(d) + 2 * e
        self._data['Ra'][0] = Ra
        self._data['Rb'][0] = Rb

        # Set chart data for visualization
        self.chartData = {
            'z': zVals, 
            'F': FVals,
            'Mg': Mg, 
            'Ms': Ms,
            'Mz': Mz,
            'd': d
        }
        self._window.set_chart_data(self.chartData)

    def _calculate_bearings_attributes(self, data):
        """
        Calculate attributes of support and central bearings.

        :param data: Data used for calculating bearing attributes.
        """
        self._update_data(data)

        # Calculate support bearings attributes
        Dw = self._data['Łożyska_podporowe']['Dw'][0]
        Dz = self._data['Łożyska_podporowe']['Dz'][0]

        dw = 0.25 * (Dz - Dw)

        self._data['dwpc'][0] = dw

        # Calculate central bearings attributes
        Dw = self._data['Łożyska_centralne']['Dw'][0]
        Dz = self._data['Łożyska_centralne']['E'][0]

        dw = 0.25 * (Dz - Dw)

        self._data['dwcc'][0] = dw

    def _calculate_power_loss(self, data):
        """
        Calculate power loss.

        :param data: Data used for calculating power loss.
        """
        self._update_data(data)

        w0 = self._data['w0'][0]
        e = self._data['e'][0]
        f = self._data['f'][0]
        rw1 = self._data['rw1'][0]
        Ra = self._data['Ra'][0]
        F = self._data['F'][0]

        # Calculate power loss in support bearings
        dw = self._data['Toczne_podporowych']['D'][0]
        Dw = self._data['Łożyska_podporowe']['Dw'][0]

        S = dw / 2
        Np = f * 0.001 * w0 * (1 + (Dw + 2 * S) / dw) * (1 + e / rw1) * 4 * Ra / np.pi

        self._data['Sp'][0] = S
        self._data['Np'][0] = Np

        # Calculate power loss in central bearings
        dw = self._data['Toczne_centralnych']['D'][0]
        Dw = self._data['Łożyska_centralne']['Dw'][0]
        Dz = self._data['Łożyska_centralne']['Dz'][0]

        S = 0.15 * (Dz - Dw)
        Nc = f * 0.001 * w0 * (1 + (Dw + 2 * S) / dw) * (1 + e / rw1) * 4 * F / np.pi

        self._data['Sc'][0] = S
        self._data['Nc'][0] = Nc

    def _update_data(self, data):
        """
        Update bearings data in the model.

        This method is used to update the model with new data for bearings.

        :param data: New data to be updated in the model.
        """
        for key, value in data.items():
            if key in self._data:
                self._data[key] = value 
