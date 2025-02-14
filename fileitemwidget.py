# fileitemwidget.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont

class FileItemWidget(QWidget):
    stageRequested = pyqtSignal(str)
    unstageRequested = pyqtSignal(str)

    def __init__(self, file_name, state="working", icon="", font_size=10, parent=None):
        super().__init__(parent)
        self.file_name = file_name
        self.state = state
        self.icon = icon

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)

        self.label = QLabel(f"{icon} {file_name}")
        self.label.setFont(QFont("Segoe UI Emoji", font_size))
        layout.addWidget(self.label)

        self.stageButton = QPushButton()
        self.stageButton.setFixedSize(24, 24)
        layout.addWidget(self.stageButton)
        self.stageButton.clicked.connect(self.onButtonClicked)
        self.updateStyle()

    def onButtonClicked(self):
        if self.state == "working":
            self.stageRequested.emit(self.file_name)
        elif self.state == "staged":
            self.unstageRequested.emit(self.file_name)

    def updateState(self, new_state, new_icon=""):
        self.state = new_state
        if new_icon:
            self.icon = new_icon
            self.label.setText(f"{self.icon} {self.file_name}")
        self.updateStyle()

    def updateStyle(self):
        if self.state == "working":
            self.stageButton.setText("+")
            self.stageButton.setEnabled(True)
        elif self.state == "staged":
            self.stageButton.setText("-")
            self.stageButton.setEnabled(True)
        else:
            self.stageButton.setText("")
            self.stageButton.setEnabled(False)
        # Additional styling if needed
