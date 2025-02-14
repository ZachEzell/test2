# gitintegration.py
import os
from git import Repo
from PyQt5.QtWidgets import QMessageBox

IGNORED_FOLDERS = {".venv", "venv", "node_modules", ".git", "__pycache__"}

class GitIntegration:
    def __init__(self):
        self.repo = None
        self.current_branch = "main"

    def createRepository(self, parent_widget):
        from PyQt5.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(parent_widget, "Select Directory for New Repository")
        if directory:
            try:
                self.repo = Repo.init(directory)
                self.current_branch = "main"
                return directory
            except Exception as e:
                QMessageBox.critical(parent_widget, "Error", f"Error creating repository: {e}")
        return None

    def cloneRepository(self, parent_widget):
        from PyQt5.QtWidgets import QFileDialog, QInputDialog
        url, ok = QInputDialog.getText(parent_widget, "Clone Repository", "Enter repository URL:")
        if ok and url:
            directory = QFileDialog.getExistingDirectory(parent_widget, "Select Directory for Cloned Repository")
            if directory:
                try:
                    self.repo = Repo.clone_from(url, directory)
                    self.current_branch = self.repo.active_branch.name
                    return directory
                except Exception as e:
                    QMessageBox.critical(parent_widget, "Error", f"Error cloning repository: {e}")
        return None

    def loadExistingRepository(self, parent_widget):
        from PyQt5.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(parent_widget, "Select Existing Repository")
        if directory:
            if not os.path.exists(os.path.join(directory, ".git")):
                QMessageBox.critical(parent_widget, "Error", "The selected directory is not a valid Git repository.")
                return None
            try:
                self.repo = Repo(directory)
                self.current_branch = self.repo.active_branch.name
                return directory
            except Exception as e:
                QMessageBox.critical(parent_widget, "Error", f"Error loading repository: {e}")
        return None

    def getAllFiles(self):
        """Return a list of all files (relative paths) in the working tree, excluding ignored folders."""
        file_list = []
        if self.repo and self.repo.working_tree_dir:
            root_dir = self.repo.working_tree_dir
            for root, dirs, files in os.walk(root_dir):
                # Remove ignored directories
                dirs[:] = [d for d in dirs if d not in IGNORED_FOLDERS]
                for f in files:
                    rel_path = os.path.relpath(os.path.join(root, f), root_dir)
                    file_list.append(rel_path)
        return file_list

    def stageFile(self, file):
        if not self.repo:
            return
        try:
            self.repo.index.add([file])
            self.repo.index.write()
        except Exception as e:
            print("Error staging file:", e)

    def unstageFile(self, file):
        if not self.repo:
            return
        try:
            self.repo.git.reset('HEAD', '--', file)
        except Exception as e:
            print("Error unstaging file:", e)

    def commit(self, message):
        if self.repo:
            try:
                new_commit = self.repo.index.commit(message)
                print("Committed:", new_commit.hexsha)
            except Exception as e:
                print("Commit error:", e)

    def listBranches(self):
        if not self.repo:
            return []
        return [str(b) for b in self.repo.branches]

    def createBranch(self, branch_name, commit_sha=None):
        if self.repo:
            try:
                if commit_sha:
                    self.repo.git.branch(branch_name, commit_sha)
                else:
                    self.repo.git.branch(branch_name)
            except Exception as e:
                print("Error creating branch:", e)

    def checkoutBranch(self, branch_name):
        if self.repo:
            try:
                self.repo.git.checkout(branch_name)
                self.current_branch = branch_name
            except Exception as e:
                print("Error checking out branch:", e)

    def pushCurrentBranch(self):
        if not self.repo:
            return
        try:
            branch_name = self.current_branch
            origin = self.repo.remote(name='origin')
            origin.push(refspec=f"{branch_name}:{branch_name}")
            print(f"Pushed {branch_name} to origin.")
        except Exception as e:
            print("Push error:", e)
