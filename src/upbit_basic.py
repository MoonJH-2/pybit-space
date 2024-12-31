import os
import pyupbit
from dotenv import load_dotenv
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor


class UpbitDataFetcher(QThread):
    """
    Worker thread to fetch cryptocurrency balances and real-time prices.
    """

    data_fetched = pyqtSignal(dict, list)  # Emit prices and balances

    def __init__(self, tickers):
        super().__init__()
        self.tickers = tickers
        self.access = None
        self.secret = None
        self.upbit = None

    def run(self):
        # Load API keys
        dotenv_path = os.path.join(os.path.dirname(__file__), "../configs/.env")
        load_dotenv(dotenv_path)
        self.access = os.getenv("UPBIT_ACCESS_KEY")
        self.secret = os.getenv("UPBIT_SECRET_KEY")

        if not self.access or not self.secret:
            raise ValueError("API keys are missing. Check your .env file.")

        self.upbit = pyupbit.Upbit(self.access, self.secret)

        while True:
            # Fetch balances
            balances = self.upbit.get_balances()

            # Fetch prices for tickers
            prices = pyupbit.get_current_price(self.tickers)

            # Emit both balances and prices
            self.data_fetched.emit(prices, balances)
            self.sleep(1)  # Update every 1 second


class App(QWidget):
    """
    PyQt5 application to display balances, real-time prices, and price differences.
    """

    def __init__(self, tickers):
        super().__init__()
        self.tickers = tickers
        self.previous_prices = {}  # Store previous prices
        self.initUI()

        # Worker thread setup
        self.worker = UpbitDataFetcher(tickers)
        self.worker.data_fetched.connect(self.update_data)
        self.worker.start()

    def initUI(self):
        # Set window properties
        self.setWindowTitle("Crypto Viewer")
        self.setGeometry(300, 300, 600, 800)

        # Main layout
        self.layout = QVBoxLayout()
        self.setStyleSheet("background-color: #2C2C2E; color: white;")

        # Cryptocurrency balance list
        self.balance_list = QListWidget(self)
        self.layout.addWidget(QLabel("보유 암호화폐 목록:", self))
        self.layout.addWidget(self.balance_list)

        # Market prices list
        self.price_list = QListWidget(self)
        self.layout.addWidget(QLabel("KRW 시장 암호화폐 목록:", self))
        self.layout.addWidget(self.price_list)

        # Set layout
        self.setLayout(self.layout)

    @pyqtSlot(dict, list)
    def update_data(self, prices, balances):
        """
        Updates the UI with balances and market prices.
        """
        # Update balance list (remove balance count)
        self.balance_list.clear()
        for balance in balances:
            currency = balance["currency"]
            if currency == "KRW":
                continue  # Skip KRW currency

            ticker = f"KRW-{currency}"
            current_price = prices.get(ticker, 0)
            previous_price = self.previous_prices.get(ticker, current_price)
            price_diff = current_price - previous_price if previous_price else 0

            # Format text and color for current price difference
            diff_text = (
                f" (+{price_diff:,.0f} KRW)"
                if price_diff > 0
                else f" ({price_diff:,.0f} KRW)"
            )
            color = (
                QColor("blue")
                if price_diff > 0
                else QColor("red") if price_diff < 0 else QColor("white")
            )

            # Display updated cryptocurrency name, current price, and difference
            item_text = f"{currency}: {current_price:,.0f} KRW{diff_text}"
            list_item = QListWidgetItem(item_text)
            list_item.setForeground(color)
            self.balance_list.addItem(list_item)

            # Update previous price
            self.previous_prices[ticker] = current_price

        # Update price list
        self.price_list.clear()
        for ticker, price in prices.items():
            previous_price = self.previous_prices.get(ticker, price)
            price_diff = price - previous_price if previous_price else 0

            diff_text = (
                f" (+{price_diff:,.0f} KRW)"
                if price_diff > 0
                else f" ({price_diff:,.0f} KRW)"
            )
            color = (
                QColor("blue")
                if price_diff > 0
                else QColor("red") if price_diff < 0 else QColor("white")
            )

            # Display updated price
            item_text = f"{ticker}: {price:,.0f} KRW{diff_text}"
            list_item = QListWidgetItem(item_text)
            list_item.setForeground(color)
            self.price_list.addItem(list_item)

            # Update previous price
            self.previous_prices[ticker] = price


if __name__ == "__main__":
    # Load API keys and fetch tickers
    dotenv_path = os.path.join(os.path.dirname(__file__), "../configs/.env")
    load_dotenv(dotenv_path)

    # Fetch KRW market tickers
    all_tickers = pyupbit.get_tickers(fiat="KRW")
    selected_tickers = all_tickers[:]

    app = QApplication([])
    ex = App(selected_tickers)
    ex.show()
    app.exec_()
