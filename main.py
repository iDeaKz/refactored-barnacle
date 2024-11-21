# app/gui/main.py

import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from app.gui.ui_main import Ui_MainWindow  # Assume a separate UI file
from app.models.predictor import PricePredictor
from app.data.collector import DataCollector
from app.data.processor import DataProcessor
from app.config import load_config
import logging
from app.utils.logger import setup_logger


class PredictionThread(QThread):
    prediction_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, predictor: PricePredictor, collector: DataCollector, processor: DataProcessor, symbol: str):
        super().__init__()
        self.predictor = predictor
        self.collector = collector
        self.processor = processor
        self.symbol = symbol

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            raw_data = loop.run_until_complete(self.collector.collect_all_data())
            processed_data = self.processor.preprocess(raw_data)
            engineered_data = self.processor.feature_engineering(processed_data)

            key = f"binance_{self.symbol.replace('/', '_')}"
            if key not in engineered_data:
                raise ValueError(f"Data for {self.symbol} not found.")

            df = engineered_data[key]
            data = self.predictor.prepare_data(df)

            prediction_input = data['X'][-1].reshape(1, self.predictor.input_steps, data['X'].shape[2])
            predictions = self.predictor.predict(prediction_input).flatten().tolist()

            self.prediction_ready.emit(predictions)
        except Exception as e:
            logging.error(f"PredictionThread error: {e}")
            self.error_occurred.emit(str(e))


class TrainingThread(QThread):
    training_complete = pyqtSignal(float)
    training_error = pyqtSignal(str)

    def __init__(self, predictor: PricePredictor, collector: DataCollector, processor: DataProcessor):
        super().__init__()
        self.predictor = predictor
        self.collector = collector
        self.processor = processor

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            raw_data = loop.run_until_complete(self.collector.collect_all_data())
            processed_data = self.processor.preprocess(raw_data)
            engineered_data = self.processor.feature_engineering(processed_data)

            # Assuming training on all available data or specific symbols
            for key, df in engineered_data.items():
                data = self.predictor.prepare_data(df)
                loss = self.predictor.train(data['X'], data['y'])
                self.predictor.save_model()
                logging.info(f"Trained model for {key} with loss: {loss}")

            self.training_complete.emit(loss)
        except Exception as e:
            logging.error(f"TrainingThread error: {e}")
            self.training_error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Load configuration and initialize components
        self.config = load_config()
        self.logger = setup_logger(self.config, 'gui_logger')
        self.predictor = PricePredictor(self.config)
        try:
            self.predictor.load_model()
        except FileNotFoundError:
            self.logger.warning("Model not found. Please train the model first.")
            QMessageBox.warning(self, "Model Not Found", "The prediction model is not available. Please train the model first.")
        
        self.collector = DataCollector(self.config)
        self.processor = DataProcessor()

        # Connect signals
        self.ui.predictButton.clicked.connect(self.on_predict)
        self.ui.trainButton.clicked.connect(self.on_train)

    def on_predict(self):
        symbol = self.ui.symbolInput.text().strip().upper()
        if not symbol:
            QMessageBox.warning(self, "Input Error", "Please enter a valid symbol (e.g., BTC/USD).")
            return

        self.ui.statusLabel.setText("Fetching data and making prediction...")
        self.ui.predictButton.setEnabled(False)

        self.prediction_thread = PredictionThread(self.predictor, self.collector, self.processor, symbol)
        self.prediction_thread.prediction_ready.connect(self.display_prediction)
        self.prediction_thread.error_occurred.connect(self.handle_error)
        self.prediction_thread.start()

    def display_prediction(self, predictions):
        self.ui.statusLabel.setText("Prediction completed.")
        self.ui.predictButton.setEnabled(True)
        prediction_text = "\n".join([f"Step {i+1}: {price:.2f}" for i, price in enumerate(predictions)])
        QMessageBox.information(self, "Predicted Prices", prediction_text)

    def handle_error(self, error_message):
        self.ui.statusLabel.setText("An error occurred.")
        self.ui.predictButton.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred during prediction:\n{error_message}")

    def on_train(self):
        confirm = QMessageBox.question(self, "Confirm Training", "Are you sure you want to train the model? This may take some time.", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.ui.statusLabel.setText("Training in progress...")
            self.ui.trainButton.setEnabled(False)

            self.training_thread = TrainingThread(self.predictor, self.collector, self.processor)
            self.training_thread.training_complete.connect(self.training_success)
            self.training_thread.training_error.connect(self.training_failure)
            self.training_thread.start()

    def training_success(self, loss):
        self.ui.statusLabel.setText("Training completed successfully.")
        self.ui.trainButton.setEnabled(True)
        QMessageBox.information(self, "Training Complete", f"Model trained successfully with final loss: {loss:.4f}")

    def training_failure(self, error_message):
        self.ui.statusLabel.setText("An error occurred during training.")
        self.ui.trainButton.setEnabled(True)
        QMessageBox.critical(self, "Training Error", f"An error occurred during training:\n{error_message}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
