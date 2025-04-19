# standard
from datetime import datetime
from typing import Optional

# Self-define module
import module.utils as utils
from module.crawler import Crawler
from module.dc_stock_channel import DcStockChannel
from module.excel_handler import ExcelHandler
from module.plot_handler import PlotHandler
from config.config import ConfigManager

class Stock:
    def __init__(self, stock_code: int):
        # variable
        self.stock_code:str = str(stock_code)
        self.price:Optional[str] = None
        self.balance_yest:Optional[str] = None
        self.selling_today:Optional[str] = None
        self.return_today:Optional[str] = None
        self.balance_today:Optional[str] = None
        self.update_time:Optional[str] = None
        # object
        self.excel_handler:"ExcelHandler" = ExcelHandler.create_file(self.stock_code)
    
    def fetch_price(self) -> None:
        self.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.price = Crawler.crawl_price(self.stock_code)
    
    def fetch_lending(self) -> None:
        results:list[str] = Crawler.crawl_lending(self.stock_code)
        self.balance_yest = results[0]
        self.selling_today = results[1]
        self.return_today = results[2]
        self.balance_today = results[3]
        self.update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def json_to_dc_stock(self) -> None:
        """ Send json to dc stock channel """
        data = vars(self).copy()
        data.pop("excel_handler", None)

        if utils.all_key_not_none(data):
            DcStockChannel.send_json(data)

    def save_to_excel(self) -> None:
        # 1) Create ExcelHandler object
        stock_dict = self.__dict__

        # 2) Update Excel file
        self.excel_handler = ExcelHandler.create_file(self.stock_code)

        # 3) ExcelHandler.save_file(data:dict)
        self.excel_handler.save_file(stock_dict)

    def plot_grid_price_ss(self) -> None:
        """ price vs short selling"""
        stock_dict = self.__dict__
        # 1) Get x,y axis data
        x, y = self.excel_handler.read_all_records()

        # 2) Plot & save to local
        PlotHandler.plot_grid(x, y, stock_dict)

    def image_to_dc_stock(self) -> None:
        DcStockChannel.send_image(self.stock_code)

if __name__ == "__main__":
    config = ConfigManager()

    stocks_dict = config.get("stock_code")

    stocks:list["Stock"] = [Stock(stocks_dict[key]) for key in stocks_dict]
    print(stocks)

    # # 1) Testing crawl function
    # stock2317 = Stock(2317)
    # stock2317.fetch_price()
    # stock2317.fetch_lending()
    #
    # # 2) Testing save file
    # stock2317.save_to_excel()
    #
    # # 3) Testing plot
    # stock2317.plot_grid_price_ss()
    #
    # # 4) send json
    # stock2317.json_to_dc_stock()
    #
    # # 5) send image to dc channel
    # stock2317.image_to_dc_stock()