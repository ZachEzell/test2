# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QSplitter
from overlays import StartupOverlay
from filepanel import FilePanel
from graphpanel import GraphPanel
from advanced import AdvancedPanel
from gitintegration import GitIntegration
from remoteinfo import RemoteInfoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git DAG GUI - Small Repo Edition")
        self.resize(1200, 800)

        self.git_integration = GitIntegration()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Page 0: Startup overlay
        self.startupPage = QWidget()
        from PyQt5.QtWidgets import QVBoxLayout
        startupLayout = QVBoxLayout(self.startupPage)
        self.overlay = StartupOverlay()
        startupLayout.addWidget(self.overlay)
        self.stack.addWidget(self.startupPage)

        # Page 1: Main UI
        self.mainPage = QWidget()
        self.stack.addWidget(self.mainPage)
        self.initMainUI()

        # Connect overlay signals
        self.overlay.createRepositoryRequested.connect(self.createRepo)
        self.overlay.cloneRepositoryRequested.connect(self.cloneRepo)
        self.overlay.loadRepositoryRequested.connect(self.loadRepo)

    def initMainUI(self):
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
        mainLayout = QVBoxLayout(self.mainPage)
        self.mainPage.setLayout(mainLayout)

        # Graph at the top
        self.graphPanel = GraphPanel(self.git_integration)
        mainLayout.addWidget(self.graphPanel)

        # Next row: remote info + splitter
        rowWidget = QWidget()
        rowLayout = QHBoxLayout(rowWidget)
        self.remoteInfo = RemoteInfoWidget(self.git_integration)
        rowLayout.addWidget(self.remoteInfo)

        splitter = QSplitter()
        self.filePanel = FilePanel(self.git_integration)
        self.advancedPanel = AdvancedPanel(self.git_integration)
        splitter.addWidget(self.filePanel)
        splitter.addWidget(self.advancedPanel)
        rowLayout.addWidget(splitter)

        mainLayout.addWidget(rowWidget)

        # Connect signals
        self.filePanel.commitRequested.connect(self.onCommitRequested)

    def createRepo(self):
        directory = self.git_integration.createRepository(self)
        if directory:
            self.afterRepoInitialization()

    def cloneRepo(self):
        directory = self.git_integration.cloneRepository(self)
        if directory:
            self.afterRepoInitialization()

    def loadRepo(self):
        directory = self.git_integration.loadExistingRepository(self)
        if directory:
            self.afterRepoInitialization()

    def afterRepoInitialization(self):
        self.filePanel.refreshStatus()
        self.remoteInfo.refresh()
        self.graphPanel.refresh()
        self.stack.setCurrentIndex(1)

    def onCommitRequested(self, commit_message):
        self.git_integration.commit(commit_message)
        self.filePanel.refreshStatus()
        self.graphPanel.refresh()

def main():
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow { background-color: #202020; color: #e0e0e0; }
        QWidget { background-color: #202020; color: #e0e0e0; }
        QListWidget { background-color: #2c2c2c; color: #e0e0e0; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
