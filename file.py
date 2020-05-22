import os
import sys
import csv

from bs4 import BeautifulSoup
from selenium import webdriver

CSV_FILE=os.path.join(sys.path[0],"itemsDatabase","DB.csv")

class FileData():

    def __init__(self, URL):
        try:
            driver = webdriver.Firefox()
            driver.get(URL)
            driver.implicitly_wait(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            self.soup = soup
            driver.quit()
        except Exception:
            print('Invalid URL!')
            exit()

        self.URL = URL

    def checkItemIfExists(self):
        with open(CSV_FILE, "r") as csv_file:
            reader = csv.reader(csv_file)
            for line in reader:
                if self.URL in line[0]:
                    return True

    def findTargetPrice(self):
        with open(CSV_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            for line in csv_reader:
                if self.URL == line[0]:
                    return line[2]

    def delFile(self):
        url = self.URL
        temp_csv = os.path.join(sys.path[0], 'itemsDatabase', 'temp_data.csv')

        with open(CSV_FILE, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            for line in csv_reader:

                if url == line[0]:

                    with open(temp_csv, 'w') as copier:
                        csv_file.seek(0)

                        for line in csv_reader:
                            if url != line[0]:
                                copier.write(f"{','.join(line)}\n")

        os.remove(CSV_FILE)
        os.rename(temp_csv, CSV_FILE)

        return True