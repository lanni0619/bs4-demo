# 3rd-party package
import matplotlib # type: ignore
import matplotlib.pyplot as plt # type: ignore

# Standard
from os import path

# Self-define
import utils

matplotlib.use("Agg")

class PlotHandlerConfig:
    GRID_WIDTH = 10
    GRID_HEIGHT = 5
    IMAGE_STORE_PATH = "C:/temp/stock-log"
    IMAGE_FILE_NAME = "{0}_{1}.jpg"

class PlotHandler:

    @staticmethod
    @utils.tic_tok
    @utils.handle_errors
    def plot_grid(data_x:list, data_y:list, stock_dict:dict) -> None:
        """ data_y = [[data1], [data2], ...] """

        plt.figure(figsize=(PlotHandlerConfig.GRID_WIDTH, PlotHandlerConfig.GRID_HEIGHT))
        for index, data in enumerate(data_y):
            label = "short selling (unit - 1k lot)" if index == 0 else "price (unit - NTD)"
            plt.plot(data_x, data, label=label)

        plt.xlabel("date")
        plt.ylabel("shares")
        plt.title(f"{stock_dict['stock_code']} - PRICE VS SHORT SELLING")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid()

        yy_mm = stock_dict["update_time"][0:7]
        print(yy_mm)

        img_filename = PlotHandlerConfig.IMAGE_FILE_NAME.format(stock_dict['stock_code'], yy_mm)
        save_path = path.join(PlotHandlerConfig.IMAGE_STORE_PATH, img_filename)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()