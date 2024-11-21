# app/gui/ui_main.py

# This file is typically generated using Qt Designer and pyuic5.
# Below is a simplified example.

from PyQt5.QtWidgets import QMainWindow, QPushButton, QLineEdit, QLabel, QMessageBox
from PyQt5.QtCore import QRect


class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Crypto Price Predictor")
        MainWindow.setGeometry(100, 100, 600, 400)

        self.symbolInput = QLineEdit(MainWindow)
        self.symbolInput.setGeometry(QRect(50, 50, 200, 40))
        self.symbolInput.setPlaceholderText("Enter Symbol (e.g., BTC/USD)")

        self.predictButton = QPushButton("Predict", MainWindow)
        self.predictButton.setGeometry(QRect(270, 50, 100, 40))

        self.trainButton = QPushButton("Train Model", MainWindow)
        self.trainButton.setGeometry(QRect(380, 50, 120, 40))

        self.statusLabel = QLabel("Status: Idle", MainWindow)
        self.statusLabel.setGeometry(QRect(50, 100, 450, 30))
