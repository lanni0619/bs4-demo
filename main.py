# Package
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd

# Module
import json
from datetime import datetime
import os
import threading
import sys
import time
from module.matplotlib_demo import plot_short_selling
from logger import logging

# Global variable
info_2317 = None

class CreditLine:
    def __init__(self, created_at, balance_yest, selling_today, return_today, balance_today, price):
        self.created_at = created_at
        self.balance_yest = balance_yest
        self.selling_today = selling_today
        self.return_today = return_today
        self.balance_today = balance_today
        self.price = price
        self.unit = "share"
    def toJson(self):
        #  https://stackoverflow.com/questions/7408647/convert-dynamic-python-object-to-json
         return json.dumps(
              self,
              default=lambda o: o.__dict__,
              sort_keys=False,
              indent=4
         )

def crawl_2317():
    logging.info("crawler function")
    
    global info_2317
    short_selling_url = 'https://www.twse.com.tw/rwd/zh/marginTrading/TWT93U?response=html'
    price_url = "https://tw.stock.yahoo.com/quote/2317.TW"

    web1 = requests.get(short_selling_url)
    web2 = requests.get(price_url)

    soup1 = BeautifulSoup(web1.text, "html5lib")
    soup2 = BeautifulSoup(web2.text, "html5lib")

    data_array1 = soup1.find_all('tr', attrs={"align":"center", "style":"font-size:14px;"})
    data2 = soup2.find('span', class_="Fz(32px) Fw(b) Lh(1) Mend(16px) D(f) Ai(c) C($c-trend-up)")
    
    for short_selling in data_array1:
        if short_selling.find('td').get_text() == "2317":
            stock_2317 = short_selling.find_all('td')

            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            balance_yest = stock_2317[8].get_text()  # 前日餘額
            selling_today = stock_2317[9].get_text() # 當日賣出
            return_today = stock_2317[10].get_text()  # 當日還券
            balance_today = stock_2317[12].get_text() # 今日餘額
            price = data2.get_text()

            if not created_at or not balance_today or not selling_today or not return_today or not balance_today or not price:
                logging.error("crawler function - data incomplete.")
                return

            info_2317 = CreditLine(created_at, balance_yest, selling_today, return_today, balance_today, price)

def send_json_discord(info):
    logging.info(f"send_json_discord - info={info}")
    # Preliminary
    if not info:
        logging.error("send_json_discord - info undefined")
        return

    info_json = info.toJson()

    url = "https://discord.com/api/webhooks/1356484738029719573/9GNCPHfl7gcz9BpkkO1xYEYqZ9_D2tWd0dx5sZqx3RTN3HgLFLql47TEgWYEsz0Q4x8g"   
    headers = {"Content-Type": "application/json"}
    data = {"content": info_json, "username": "newmanBot"}

    # Write to log
    save_to_excel(info_2317, 2317)

    # Send data to discord
    res = requests.post(url, headers = headers, json = data)
    
    # Read the response
    if res.status_code in (200, 204):
            print(f"✅ Request fulfilled with response code {res.status_code}")
    else:
            print(f"❌ Request failed with response: {res.status_code}-{res.text}")
    print("")

def send_jpg_discord(stock_number):
    logging.info(f"send_jpg_discord - stock_number={stock_number}")
    # draw new chart
    plot_short_selling(stock_number)

    # Path to the JPG file
    today = datetime.today()
    jpg_file_path = f"C:/temp/stock-log/{stock_number}_{today.strftime('%Y-%m')}.jpg"  # Replace with your actual file name

    # Discord webhook URL
    url = "https://discord.com/api/webhooks/1356484738029719573/9GNCPHfl7gcz9BpkkO1xYEYqZ9_D2tWd0dx5sZqx3RTN3HgLFLql47TEgWYEsz0Q4x8g"

    # Check if the file exists
    if not os.path.exists(jpg_file_path):
        logging.info(f"send_jpg_discord - ❌ File not found: {jpg_file_path}")
        return

    # Prepare the file and payload
    with open(jpg_file_path, "rb") as file:
        files = {"file": (os.path.basename(jpg_file_path), file, "image/jpeg")}
        payload = {"username": "newmanBot"}

        # Send the request
        res = requests.post(url, data=payload, files=files)

    # Read the response
    if res.status_code in (200, 204):
        logging.info(f"send_jpg_discord - ✅ JPG file sent successfully with response code {res.status_code}")
    else:
        logging.info(f"send_jpg_discord - ❌ Failed to send JPG file: {res.status_code} - {res.text}")

def save_to_logFile(info, stock_number):
    root_path = "C:/temp/stock-log"

    file_path = os.path.join(root_path, f"{stock_number}-file.txt")

    with open(file_path, 'a') as file:
         file.write('Date: ' + info.created_at + '\n')
         file.write('balance_yest: ' + info.balance_yest + '\n')
         file.write('selling_today: ' + info.selling_today + '\n')
         file.write('return_today: ' + info.return_today + '\n')
         file.write('balance_today: ' + info.balance_today + '\n')

def save_to_excel(info, stock_number):
    logging.info(f"save_to_excel - info={info} - stock_number={stock_number}")
    
    today = datetime.today()
    root_path = "C:/temp/stock-log"
    filename = os.path.join(root_path, f"{stock_number}_{today.strftime('%Y-%m')}.xlsx")

    new_entry = {
        "date": info.created_at,
        "balance_yest": int(info.balance_yest.replace(",", "")),
        "selling_today": int(info.selling_today.replace(",", "")),
        "return_today": int(info.return_today.replace(",", "")),
        "balance_today": int(info.balance_today.replace(",", "")),
        "price": float(info.price.replace(",", ""))
    }

    # 檢查檔案是否存在
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    else:
        df = pd.DataFrame([new_entry])

    df.to_excel(filename, index=False)
    logging.info(f"save_to_excel - ✅ {info.created_at} 紀錄已存入 {filename}")

def build_allData_2317():
    # Preliminary
    global info_2317
    hour = 23
    min = 6
    
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")
    
    # Non blocking Schedule
    scheduler.add_job(crawl_2317, 'cron', day_of_week='1-5', hour=hour, minute=00, second=00)
    scheduler.add_job(lambda: send_json_discord(info_2317), 'cron', day_of_week='1-5', hour=hour, minute=min, second=10)
    print(f"Schedule send_json_discord at {hour}:00:00 on Monday to Friday ...")
    
    scheduler.add_job(lambda: send_jpg_discord(2317), 'cron', day_of_week='fri', hour=hour, minute=min, second=15)
    print(f"Schedule send_jpg_discord at {hour}:00:30 on Friday !")

    scheduler.start()

def user_input_loop():
    while True:
        print('👍 Process is running ...')
        cmd = input("🔔 Command: ")
        
        if cmd == "0":
            print("Exiting...")
            break
        
        elif cmd == "1":
            crawl_2317()
            send_json_discord(info_2317)
        
        elif cmd == "2":
            send_jpg_discord(2317)

        elif cmd == "3":
            print("info_2317 = ", info_2317)


def main():
    logging.info("Start main ...")
    scheduler_thread = threading.Thread(target=build_allData_2317)
    scheduler_thread.start()

    time.sleep(1)
    user_input_loop()

if __name__ == "__main__":
     main()