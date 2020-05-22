import os
import sys
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import json
from priceDropEmail import Email
import csv
import multiprocessing
from file import FileData

with open('settings.json','r') as file:
    settings = json.load(file)

with open(os.path.join(sys.path[0], "password.key"), "r") as f:
    sender_password = f.read()

CSV_FILE=os.path.join(sys.path[0],"itemsDatabase","DB.csv")



def getPrice(url):
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(5)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    title = soup.find(id="productTitle").get_text().strip()
    try:
        productPrice = soup.find(id="priceblock_ourprice").get_text()
    except AttributeError:
        try:
            productPrice = soup.find(id="priceblock_dealprice").get_text()
        except AttributeError:
            print("The item is either out of stock or does not ship to your location")
            driver.quit()
            return

    driver.quit()
    return productPrice


def getTitle(url):
    driver = webdriver.Firefox()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    try:
        title = soup.find(id="productTitle").get_text().strip()
        driver.quit()
        return title
    except Exception:
        print("Invalid URL")


def Tracker():
    if len(displayItems()) == 0:
        print("The tracking file is empty")
        return
    while True:

        p = multiprocessing.Pool()
        urls = []
        print("The website will be checked every {} seconds".format(settings['remind-time']))
        with open(CSV_FILE, 'r') as file:
                csv_reader = csv.reader(file)

                for line in csv_reader:
                    url = line[0]

                    urls.append(url)

        p.map(trackPrice, urls)
        p.close()

        time.sleep(settings['remind-time'])


def trackPrice(url):
    curPrice=getPrice(url)
    if curPrice==None:
        return
    curPrice=curPrice.replace(",","")
    Currency=curPrice[0:1]
    price=float(curPrice[1:])
    itemName=getTitle(url)
    WANTED_PRICE=float(FileData(url).findTargetPrice())
    if price>WANTED_PRICE:
        diff=round(price-WANTED_PRICE,2)
        print("{} is still {}{} over your budget".format(itemName,Currency,diff))
    else:
        print("{} is now priced below your budget!!".format(itemName))
        print("An email has been sent to the provided email address")
        comm=Email(itemName,url,curPrice,Currency+str(WANTED_PRICE))
        comm.sendEmail()

def addNewItem():
    url=input('Enter the URL of the item to add to the tracking list: ')
    if (FileData(url).checkItemIfExists()):
        print("The item is already being tracked")
    else:
        desired_price=input("Enter your budget for this price: ")
        name =getTitle(url).strip()
        try:
            with open(CSV_FILE,"a") as file:
                file.write('{},"{}",{}\n'.format(url,name,float(desired_price)))
                print("{} has been added to the tracking list".format(name))

        except Exception:
            print("Invalid target price")
            exit()



def deleteItem():
    url=input("Enter the url to be deleted: ")
    response=input("Are you sure?(Y/N): ".lower())
    if response == 'y':
        result = FileData(url).delFile()

        if result:
            print('Your item was removed from the tracking list.')
        else:
            print('Invalid URL!')
    else:
        print('Item was not deleted.')


def displayItems():
    items = dict()

    with open(CSV_FILE, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        for line in csv_reader:
            items.update({line[1]: line[0]})

    return items

def main():

    while True:
        option = input("""
          -----------------------------------------------
          | Price Tracker for Amazon                     |
          |                                              |
          | Select an option                             |
          |                                              |
          | 1. Run tracker                               | 
          | 2. Add new item                              |
          | 3. Delete an item                            |
          | 4. Check all items you are currently tracking|
          | 5. Exit                                      |
          |                                              |   
          -----------------------------------------------

               Option: """)

        if (option=='1'):
            Tracker()

        elif (option=='2'):
            addNewItem()
        elif (option=='3'):
            deleteItem()
        elif (option=='4'):
            if len(displayItems())==0:
                print("Your tracking list is currently empty")
            else:
                for product,url in displayItems().items():
                    print('{}:{}'.format(product,url))
        elif option=='5':
            exit()
        else:
            print("Not a valid option. Choose an option between 1-5")



if __name__=='__main__':
    main()










