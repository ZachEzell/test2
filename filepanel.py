# filepanel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QInputDialog, QLabel
)
from PyQt5.QtCore import pyqtSignal, Qt
from functools import partial
from fileitemwidget import FileItemWidget

class FilePanel(QWidget):
    commitRequested = pyqtSignal(str)  # Emitted when user commits staged files

    def __init__(self, git_integration, parent=None):
        super().__init__(parent)
        self.git_integration = git_integration

        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(10)

        # Row 1: Working + Staging
        row1Widget = QWidget()
        row1Layout = QVBoxLayout(row1Widget)
        row1Layout.setSpacing(5)

        # Labels
        topLabels = QHBoxLayout()
        self.workingLabel = QLabel("Working Directory")
        self.workingLabel.setStyleSheet("font-weight: bold; background-color: #2c2c2c; padding: 4px;")
        self.workingLabel.setFixedHeight(25)

        self.stagingLabel = QLabel("Staging Area")
        self.stagingLabel.setStyleSheet("font-weight: bold; background-color: #3a3a1f; padding: 4px;")
        self.stagingLabel.setFixedHeight(25)

        topLabels.addWidget(self.workingLabel)
        topLabels.addWidget(self.stagingLabel)
        row1Layout.addLayout(topLabels)

        # Horizontal layout for the lists
        topListLayout = QHBoxLayout()
        self.workingList = QListWidget()
        self.stagingList = QListWidget()
        topListLayout.addWidget(self.workingList)
        topListLayout.addWidget(self.stagingList)
        row1Layout.addLayout(topListLayout)

        # Commit button
        self.commitButton = QPushButton("Commit Staged")
        self.commitButton.setFixedHeight(30)
        self.commitButton.clicked.connect(self.onCommitButtonClicked)
        row1Layout.addWidget(self.commitButton)

        # Row 2: Committed
        row2Widget = QWidget()
        row2Layout = QVBoxLayout(row2Widget)
        row2Layout.setSpacing(5)

        self.committedLabel = QLabel("Committed")
        self.committedLabel.setStyleSheet("font-weight: bold; background-color: #1f3a1f; padding: 4px;")
        self.committedLabel.setFixedHeight(25)
        row2Layout.addWidget(self.committedLabel)

        self.committedList = QListWidget()
        row2Layout.addWidget(self.committedList)

        mainLayout.addWidget(row1Widget, stretch=3)
        mainLayout.addWidget(row2Widget, stretch=2)

        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
                color: #e0e0e0;
            }
            QListWidget {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
            }
        """)

    def refreshStatus(self):
        # Clear everything
        self.workingList.clear()
        self.stagingList.clear()
        self.committedList.clear()

        repo = self.git_integration.repo
        if not repo or not repo.working_tree_dir:
            return

        all_files = self.git_integration.getAllFiles()

        # Identify modified/untracked
        working_files = set()
        try:
            diff_working = repo.index.diff(None)
            for diff in diff_working:
                working_files.add(diff.a_path)
        except Exception as e:
            print("Error getting working diff:", e)
        for f in repo.untracked_files:
            working_files.add(f)

        # Populate Working Directory
        for f in sorted(all_files):
            if f in working_files:
                icon = "✏️" if f not in repo.untracked_files else "🆕"
            else:
                icon = "✅"
            item = QListWidgetItem()
            widget = FileItemWidget(f, "working", icon, font_size=11)
            widget.stageRequested.connect(partial(self.onStageFile, f))
            item.setSizeHint(widget.sizeHint())
            self.workingList.addItem(item)
            self.workingList.setItemWidget(item, widget)

        # Staging
        staging_files = set()
        if repo.head.is_valid():
            try:
                diff_staged = repo.index.diff("HEAD")
                for diff in diff_staged:
                    staging_files.add(diff.a_path)
            except Exception as e:
                print("Error getting staged diff:", e)
        else:
            staging_files = {key[0] for key in repo.index.entries.keys()}

        diff_from_index = {d.a_path for d in repo.index.diff(None)}
        for f in sorted(staging_files):
            icon = "✏️" if f in diff_from_index else "✔"
            item = QListWidgetItem()
            widget = FileItemWidget(f, "staged", icon, font_size=11)
            widget.unstageRequested.connect(partial(self.onUnstageFile, f))
            item.setSizeHint(widget.sizeHint())
            self.stagingList.addItem(item)
            self.stagingList.setItemWidget(item, widget)

        # Committed (files from last commit)
        committed_files = set()
        if repo.head.is_valid():
            commit = repo.head.commit
            if commit.parents:
                diff_committed = commit.diff(commit.parents[0])
                for diff in diff_committed:
                    committed_files.add(diff.a_path)
            else:
                committed_files = set()
        for f in sorted(committed_files):
            item = QListWidgetItem()
            widget = FileItemWidget(f, "committed", "✓", font_size=11)
            widget.stageButton.setEnabled(False)
            item.setSizeHint(widget.sizeHint())
            self.committedList.addItem(item)
            self.committedList.setItemWidget(item, widget)

    def onStageFile(self, file):
        self.git_integration.stageFile(file)
        self.refreshStatus()

    def onUnstageFile(self, file):
        self.git_integration.unstageFile(file)
        self.refreshStatus()

    def onCommitButtonClicked(self):
        commit_message, ok = QInputDialog.getText(self, "Commit", "Enter commit message:")
        if ok and commit_message:
            self.commitRequested.emit(commit_message)
