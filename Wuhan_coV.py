'''
Author: Yixiang Wang Email: yixiang.wang@yale.edu 
version: .01	Date: 01/22/2020
WARNING: THIS IS NOT AN APP FOR COMMERCIAL USE!
'''
from bs4 import BeautifulSoup
import urllib
from urllib import request, error
from datetime import datetime
import csv
import time
import os
import random

def iterGet(inputBox):
    '''
        Get the stripped text from a list of class 'bs4.element.Tag'
        This function is not used in current version (for potential future application)
    
        Inputs:
            inputBox 			A list of class 'bs4.element.Tag'
        Outputs:
            boxData				A list of plain texts extracted from the inputBox
    '''
    boxData = []
    for item in inputBox:
        boxData.append(item.text.strip())
    #print(len(boxData))
    return boxData





def getFilename(tag):
    '''
        This function is to pull out the date info and return the .csv filename
    '''
    todayStr = str(datetime.today())
    filename = todayStr + '.csv'
    filenameList = list(filename)
    flag = True
    while flag:
        try:
            filenameList.remove(':')
        except:
            flag = False
            filename = ''.join(filenameList)
            
    filename = filename[0:10] 
            
    try:
        filename = filename + tag
    except:
        tag = ''
        filename = filename + tag
            
    
    filename = filename + '.csv'
    return filename



def outputCSV(data, tag):
    '''
        This function is to output the csv file
    '''

    with open(getFilename(tag), 'a', encoding = 'utf-8') as csv_file:
        writer = csv.writer(csv_file)
        # The for loop
        for i in range(len(data)):
            #print(name,price)
            writer.writerow(data[i])
            

def outputCSV_Chinese(data, tag):
    '''
        This function is to output the csv file
    '''

    with open(getFilename(tag), 'a', newline='', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file)
        # The for loop
        for i in range(len(data)):
            #print(name,price)
            writer.writerow(data[i])



def findNext(web_base,soup):
    '''
        This function is to find the hyperlink pointing to the next page
    
        Inputs:
            web_base			A base string shared by all hyperlinks
            soup 				soup data of the current page
    
        Outputs:
            next 				URL of the next page
            flag 				A flag indicate whether it is the last page
    '''	
    flag = True
    next = []
    try:
        next_box = soup.find('a', attrs={'title': 'next page'})['href']
        next = web_base + next_box
    except TypeError:
        flag = False
    
    return (next, flag)



def getSoup(quote_page):
    '''
        This function is to get the soup data with current URL
    '''
    head = {}
    #Change the user-agent to a popular one. To cheat the anti-scraping mechanisms
    head['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36'

    # Not using proxy here but can be modified in the future
    #proxy = {'http':'111.155.116.239'}
    #proxy_support = request.ProxyHandler(proxy)
    #opener = request.build_opener(proxy_support)
    #opener.addheaders = [('Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36')]
    #request.install_opener(opener)
    #print(soup.encode("utf-8")) 

    page_req = request.Request(quote_page, headers = head)
    page_resp = request.urlopen(page_req)
    page_resp = page_resp.read()
    soup = BeautifulSoup(page_resp,"html.parser")
    
    return soup

def pullOutNumber(curStr, tag):
    '''
        Get the number given certain tags and strings
    '''
    
    # Use tag to identify the index to start examination
    if (curStr.find(tag)> 0):
        testIdx = curStr.find(tag)
        
        # Record the initial index
        while not curStr[testIdx].isdigit():
            testIdx = testIdx + 1
        iniIdx = testIdx
        
        # Record the last index
        while curStr[testIdx].isdigit():
            testIdx = testIdx + 1
        endIdx = testIdx
        
        outputNum = int(curStr[iniIdx:endIdx])
    else:
        
        outputNum = 0
    
    return outputNum


def pullOutInfo(ListData):
    '''
        Get useful infomation from the ListData
    '''
    Confirmed = 0
    Suspected = 0
    Cured = 0
    Dead = 0
    curData = []
    
    n = len(ListData)
    for i in range(n):
    
        # Get current string
        curStr = ListData[i]
        
        # Get numbers of differenct cases
        Confirmed = Confirmed + pullOutNumber(curStr, '确诊')
        Suspected = Suspected + pullOutNumber(curStr, '疑似')
        Cured = Cured + pullOutNumber(curStr, '治愈')
        Dead = Dead + pullOutNumber(curStr, '死亡')
    
    # construct current data for storage
    curData.append((Confirmed,Suspected,Cured,Dead,str(datetime.today())))
    return curData
            
        
    

def runCrawler(quote_page):
    '''
        Scraping the first 5 pages starting from the input page  
    '''
    data = []
    
    soup = getSoup(quote_page)
    time_out = time.time() + 60 #For breaking the while loop if the scraping is blocked or delayed
    
    li_box = soup.find_all('p', attrs={'class': 'descList___3iOuI'})
    ListData = iterGet(li_box)
    if ListData is not None:
        data.extend(pullOutInfo(ListData))
            #print(str(pullOutInfo(li_box))[:100])

        #For breaking the while loop if the scraping is blocked or delayed
    if time.time() > time_out:
        print("Session time out")
    
    # Output summary data
    if data is not None:			
        outputCSV(data, "_all")
        
    # Output data by provinces
    if ListData is not None:
        outputCSV_Chinese(ListData, "_byProvinces")




'''
Main function
'''		
print("Author: Yixiang_Wang   Versioin:.02   Email:yixiang.wang@yale.edu")
print("FOR STUDY PURPOSE ONLY. NOT FOR COMMERCIAL USE!") 
print("\n")

try:
    # Store the url that the user input at the first time as the default url
    print("Default URL: https://3g.dxy.cn/newh5/view/pneumonia")
    if os.path.isfile("Default_URL.txt"):
        file = open('Default_URL.txt','r')
        quote_page = file.read()
        file.close()
        renewFlag = input("Renew URL? (Y/N):\n")
        if (renewFlag == 'Y') or (renewFlag == 'y'):
            os.remove('Default_URL.txt')
            quote_page = input('Please paste the URL here:\n')
            with open('Default_URL.txt','w') as f:
                f.write(quote_page)
                f.close()
        else:
            print("Continue with default URL \n")
    else:
        quote_page = input('Please paste the URL here:\n')
        with open('Default_URL.txt','w') as f:
            f.write(quote_page)
            f.close()
    
    #Specify update frequency
    cycleLength = int(input('Update every ? minutes:\n'))
    print("Program is running...")
except ValueError:
    print("Something wrong with the input, retry please...\n")

# Keep updating if the program is on
while True:
    
    # Generate a random delay
    
    try:
        runCrawler(quote_page) 
        print('Successfully scrape the data ' + str(datetime.today()))
        
    except urllib.error.HTTPError as err:
        if err.code == 403:
            print("Shoot! Seems that we are blocked by the website...How dare they...Sorry but you have to restart your modem and wait 24h until the IP address is renewed :)")
            os.remove('Default_URL.txt')
            #os.remove(getFilename())
    
    except ConnectionResetError:
        print("Emmm...The host forcibly end the request, the program will wait 30mins then try again")
        time.sleep(1800)

    except:
        print("Something wrong, could be an invalid URL input. Restart in ")
        x = random.randint(1,10) + random.random()
        print(str(x) + "sec")
        time.sleep(x) # Try again shortly
        continue
        #os.remove('Default_URL.txt')
        #os.remove(getFilename())
        
    # Randomize sleep time for the next run. Roughly keep the frequency specified by the user
    x = random.randint(1,10) + random.random()
    time.sleep(cycleLength*60 + x)	



