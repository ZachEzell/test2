# advanced.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AdvancedPanel(QWidget):
    def __init__(self, git_integration, parent=None):
        super().__init__(parent)
        self.git_integration = git_integration

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Advanced Git Options")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)

        # Push Button
        self.pushButton = QPushButton("Push Current Branch")
        self.pushButton.clicked.connect(self.onPushClicked)
        layout.addWidget(self.pushButton)

        # Stash Button
        self.stashButton = QPushButton("Stash Changes")
        self.stashButton.clicked.connect(self.onStashClicked)
        layout.addWidget(self.stashButton)

        # Pop Stash Button
        self.popStashButton = QPushButton("Pop Stash")
        self.popStashButton.clicked.connect(self.onPopStashClicked)
        layout.addWidget(self.popStashButton)

        # Interactive Rebase Button
        self.rebaseButton = QPushButton("Interactive Rebase")
        self.rebaseButton.clicked.connect(self.onRebaseClicked)
        layout.addWidget(self.rebaseButton)

        self.setStyleSheet("""
            QWidget { background-color: #2a2a2a; color: #e0e0e0; }
            QPushButton { background-color: #3c3c3c; border: 1px solid #555; padding: 6px; }
            QPushButton:hover { background-color: #4c4c4c; }
        """)

    def onPushClicked(self):
        self.git_integration.pushCurrentBranch()

    def onStashClicked(self):
        if not self.git_integration.repo:
            print("No repo loaded.")
            return
        try:
            self.git_integration.repo.git.stash("save", "Stash from Advanced Panel")
            print("Stashed changes.")
        except Exception as e:
            print("Stash error:", e)

    def onPopStashClicked(self):
        if not self.git_integration.repo:
            print("No repo loaded.")
            return
        try:
            self.git_integration.repo.git.stash("pop")
            print("Popped stash.")
        except Exception as e:
            print("Pop stash error:", e)

    def onRebaseClicked(self):
        if not self.git_integration.repo:
            print("No repo loaded.")
            return
        base, ok = QInputDialog.getText(self, "Interactive Rebase", "Rebase onto commit/branch:")
        if ok and base:
            try:
                self.git_integration.repo.git.rebase("-i", base)
                print("Interactive rebase initiated.")
            except Exception as e:
                print("Rebase error:", e)
