# graphpanel.py

from PyQt5.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsObject,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QRectF, QTimer, QLineF
from PyQt5.QtGui import QPen, QColor, QFont, QPainter
import math

class CommitNodeItem(QGraphicsObject):
    """A clickable commit node with a plus-button for branch creation."""
    def __init__(self, commit_sha, commit_msg, is_head=False, parent=None):
        super().__init__(parent)
        self.commit_sha = commit_sha
        self.commit_msg = commit_msg
        self.is_head = is_head
        self.rect = QRectF(0, 0, 140, 60)
        # 'Plus' button in the top-right corner
        self.plusRect = QRectF(self.rect.right() - 20, self.rect.top(), 20, 20)
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget):
        # Node background: green if HEAD, gray otherwise
        color = QColor("green") if self.is_head else QColor("gray")
        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRoundedRect(self.rect, 8, 8)

        # Commit text: short SHA + snippet of commit message
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 8))
        short_msg = self.commit_msg.splitlines()[0]
        text = f"{self.commit_sha[:7]}\n{short_msg[:20]}..."
        painter.drawText(self.rect.adjusted(5, 5, -5, -5), Qt.AlignLeft | Qt.AlignTop, text)

        # Draw the '+' button as a small circle
        painter.setBrush(QColor("darkblue"))
        painter.drawEllipse(self.plusRect)
        painter.setPen(Qt.white)
        painter.drawText(self.plusRect, Qt.AlignCenter, "+")

    def hoverEnterEvent(self, event):
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if self.plusRect.contains(event.pos()):
            # Clicking '+' => request branch creation from this commit
            if self.scene() and hasattr(self.scene(), "branchCreationRequestedFn") and self.scene().branchCreationRequestedFn:
                self.scene().branchCreationRequestedFn(self.commit_sha)
        else:
            super().mousePressEvent(event)

class GraphScene(QGraphicsScene):
    """Scene that draws a grid background and holds commit nodes."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(230, 230, 230))
        self.branchCreationRequestedFn = None

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        # Draw a dotted grid
        pen = QPen(QColor(200, 200, 200), 1, Qt.DotLine)
        painter.setPen(pen)
        step = 50
        left = int(rect.left()) - (int(rect.left()) % step)
        top = int(rect.top()) - (int(rect.top()) % step)
        for x in range(left, int(rect.right()), step):
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
        for y in range(top, int(rect.bottom()), step):
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

class GraphPanel(QWidget):
    """
    A QGraphicsView-based DAG panel:
    - Lays commits in a simple grid (3 columns).
    - Draws edges from each commit to its parent(s).
    - A plus-button on each commit for creating new branches.
    - Highlights the HEAD commit in green.
    """
    def __init__(self, git_integration, parent=None):
        super().__init__(parent)
        self.git_integration = git_integration

        self.view = QGraphicsView(self)
        self.scene = GraphScene(self)
        self.view.setScene(self.scene)
        self.scene.branchCreationRequestedFn = self.onBranchCreationRequested

        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Auto-refresh every 5 seconds (optional)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)

        self.refresh()

    def refresh(self):
        """Rebuilds the DAG for the current branch in a grid layout, drawing edges to parents."""
        self.scene.clear()
        repo = self.git_integration.repo
        if not repo:
            return

        # If no commits exist, show a placeholder
        if not repo.head.is_valid():
            textItem = self.scene.addText("No commits yet. Create your first commit!")
            textItem.setDefaultTextColor(QColor(150, 150, 150))
            textItem.setPos(50, 50)
            return

        branch = self.git_integration.current_branch
        try:
            commits = list(repo.iter_commits(branch))
            commits.reverse()  # oldest first
        except Exception:
            textItem = self.scene.addText("Error retrieving commits.")
            textItem.setDefaultTextColor(QColor(200, 0, 0))
            textItem.setPos(50, 50)
            return

        if not commits:
            textItem = self.scene.addText("No commits found on this branch.")
            textItem.setDefaultTextColor(QColor(150, 150, 150))
            textItem.setPos(50, 50)
            return

        # Lay out commits in a grid: 3 columns
        cols = 3
        spacing_x = 200
        spacing_y = 120

        # We'll store node references in a dict keyed by commit object
        commit_nodes = {}

        for idx, c in enumerate(commits):
            row = idx // cols
            col = idx % cols
            x = col * spacing_x
            y = row * spacing_y
            is_head = (c == repo.head.commit)
            nodeItem = CommitNodeItem(c.hexsha, c.message, is_head)
            nodeItem.setPos(x, y)
            self.scene.addItem(nodeItem)
            commit_nodes[c] = nodeItem

        # Now draw edges from child -> parent
        penEdges = QPen(QColor(50, 50, 50), 2)
        for c in commits:
            childNode = commit_nodes[c]
            # Center of the child node
            childCenter = childNode.pos() + childNode.boundingRect().center()
            for parent in c.parents:
                # If parent is in the same branch history, it should appear in commit_nodes
                if parent in commit_nodes:
                    parentNode = commit_nodes[parent]
                    parentCenter = parentNode.pos() + parentNode.boundingRect().center()
                    line = self.scene.addLine(
                        childCenter.x(), childCenter.y(),
                        parentCenter.x(), parentCenter.y(),
                        penEdges
                    )
                    # Optional: you could add an arrow or direction indicator.

    def onBranchCreationRequested(self, commit_sha):
        """Called when user clicks '+' on a commit node to create a new branch."""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        branch_name, ok = QInputDialog.getText(self, "Create Branch", f"Create new branch from {commit_sha[:7]}:")
        if ok and branch_name:
            try:
                self.git_integration.repo.git.branch(branch_name, commit_sha)
                QMessageBox.information(self, "Branch Created", f"Branch '{branch_name}' created from {commit_sha[:7]}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error creating branch: {e}")
        self.refresh()
