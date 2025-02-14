# overlays.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

class StartupOverlay(QWidget):
    createRepositoryRequested = pyqtSignal()
    cloneRepositoryRequested = pyqtSignal()
    loadRepositoryRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: rgba(0,0,0,0.85);")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        plusLabel = QLabel("+")
        plusLabel.setAlignment(Qt.AlignCenter)
        plusLabel.setStyleSheet("color: #e0e0e0;")
        plusLabel.setFont(QFont("Arial", 72, QFont.Bold))
        layout.addWidget(plusLabel)

        btnLayout = QHBoxLayout()
        createBtn = QPushButton("Create Repository")
        cloneBtn = QPushButton("Clone Repository")
        loadBtn  = QPushButton("Load Existing Repository")
        for btn in (createBtn, cloneBtn, loadBtn):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c2c2c;
                    border: 1px solid #444;
                    padding: 10px 20px;
                    color: #e0e0e0;
                }
                QPushButton:hover {
                    background-color: #3c3c3c;
                }
            """)
            btnLayout.addWidget(btn)
        layout.addLayout(btnLayout)

        createBtn.clicked.connect(lambda: self.createRepositoryRequested.emit())
        cloneBtn.clicked.connect(lambda: self.cloneRepositoryRequested.emit())
        loadBtn.clicked.connect(lambda: self.loadRepositoryRequested.emit())
