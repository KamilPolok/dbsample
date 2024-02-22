from PyQt6.QtWidgets import QToolButton, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSignal, QSize

class StayOpenMenu(QMenu):
    def mouseReleaseEvent(self, event):
        action = self.activeAction()
        if action and action.isCheckable():
            action.trigger()
            return
        super().mouseReleaseEvent(event)

class CheckboxDropdown(QToolButton):
    """
    A custom QToolButton that displays a dropdown menu with checkboxes.
    """
    stateChanged = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.actions = {}

        self.setStyleSheet("""
            * { padding-right: 3px }
            QToolButton::menu-indicator { image: none }                                
            QToolButton {
                background-color: transparent;
                color: white;
                border: 2px solid transparent;
                border-radius: 5px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #c1c9c9;
                border: 1px solid #a9b0b0;
            }
            QToolButton:pressed {
                background-color: #c1c9c9;
                border: 1px solid #a9b0b0;
            }
        """)
        self.setIconSize(QSize(20, 20))
        self.setFixedSize(QSize(35, 35))

        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self._menu = StayOpenMenu(self)
        self._menu.setToolTipsVisible(True)
        self.setMenu(self._menu)

    def addItem(self, id, label, description='', callback=None):
        """
        Add a checkable action to the dropdown menu.
        """
        if id not in self.actions:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setToolTip(description)
            if callback is None:
                action.triggered.connect(self._emitStateChangedSignal)
            else:
                action.triggered.connect(callback)
            self._menu.addAction(action)
            self.actions[id] = action
    
    def enableItem(self, id, enabled=True):
        '''
        Enables or disables checkbox of given id.
        If disables, unchecks it.

        Args:
            id (str): id of checkbox.
            enabled (bool): if enable checkbox.
        '''
        if id in self.actions:
            self.actions[id].setEnabled(enabled)
        if enabled is False:
            self.actions[id].setChecked(enabled)

    def isChecked(self, id):
        '''
        Check if Checkbox is checked.

        Args:
            id: (str): id of checkbox.

        Returns:
            res (bool): If checkobox of given id is checked.
        '''
        if id in self.actions:
            return self.actions[id].isChecked()
        return False
    
    def setIcon(self, icon, tootltip):
        '''
        Set icon of every checkbox.
        '''
        super().setIcon(QIcon(icon))

        self.setToolTip(tootltip)

    def currentOptions(self):
        """
        Return checkboxes that are currently checked

        Returns:
            res (list): List of tuples (id, text) for of every checked checkbox.
        """
        res = []
        for id, action in self.actions.items():
            if action.isChecked():
                res.append((id, action.text()))
        return res

    def _emitStateChangedSignal(self):
        self.stateChanged.emit()
