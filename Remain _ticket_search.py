from bs4 import BeautifulSoup
import requests
import time,re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from tkinter import *
from time import sleep
import random
import os
import urllib
import speech_recognition as sr

def solve_speech(src):
    urllib.request.urlretrieve(src, os.getcwd()+"\\sample.mp3")
    os.system("C:/ffmpeg/bin/ffmpeg -i sample.mp3 sample.wav -loglevel quiet")
    sample_audio = sr.AudioFile(os.getcwd()+"\\sample.wav")
    r= sr.Recognizer()
    with sample_audio as source:
        audio = r.record(source)
    key=r.recognize_google(audio)
    print("[INFO] Recaptcha Passcode: %s"%key)
    os.remove("sample.mp3")
    os.remove("sample.wav")
    return key

def get_webpage(url,head):
    html_page=requests.get(url,headers=head)

    if html_page.status_code!=200:
        print("fail!",html_page.status_code)
        return None
    else:
        return html_page.text

def delay (low=3,high=5):
    time.sleep(random.randint(low,high))

def send_key(field_name,value):
    browser.find_element_by_id(field_name).send_keys(value)


def get_user_info(pinfo):
    pinfo.append(input("enter start station id :"))
    pinfo.append(input("enter end station id :"))
    pinfo.append(input("enter date (yyyymmdd) :"))
    pinfo.append(input("enter start time (08:00) :"))
    pinfo.append(input("enter end time (16:00) :"))
    return pinfo

#pinfo=[]
#get_user_info(pinfo)
pinfo=["7000","1000","20210401","12:00","20:00"]
options=webdriver.ChromeOptions()
options.add_argument('disable-infobars')
options.add_argument('headless')
options.add_argument('defaultViewport:null')
browser=webdriver.Chrome("C:/webdrivers/chromedriver",chrome_options=options)
browser.get('https://tip.railway.gov.tw/tra-tip-web/tip/tip001/tip119/queryTime')
browser.find_element_by_id('calendar1').clear()
send_key('calendar1',pinfo[2])
send_key('startStation',pinfo[0])
send_key('endStation',pinfo[1])
send_key('startTime1',pinfo[3])
send_key('endTime1',pinfo[4])
frames=browser.find_elements_by_tag_name("iframe")
browser.switch_to.frame(frames[1])
delay()

browser.find_element_by_class_name("recaptcha-checkbox-border").click()

#switch to recaptcha audio control frame
browser.switch_to.default_content()
frames=browser.find_element_by_xpath("/html/body/div[9]/div[4]").find_elements_by_tag_name("iframe")
browser.switch_to.frame(frames[0])
delay()

browser.find_element_by_id("recaptcha-audio-button").click()

#switch to recaptcha audio challenge frame
browser.switch_to.default_content()
frames= browser.find_elements_by_tag_name("iframe")
browser.switch_to.frame(frames[-1])
delay()
while True:
    src = browser.find_element_by_id("audio-source").get_attribute("src")
    send_key("audio-response",solve_speech(src).lower())
    browser.find_element_by_xpath("/html/body/div/div/div[7]/div[2]/div[1]/div[2]/button").click()
    delay()
    browser.find_element_by_id("recaptcha-verify-button")
    src2 = browser.find_element_by_id("audio-source").get_attribute("src")
    if src==src2:
        break
#switch back from recaptcha frame
browser.switch_to.default_content()
browser.find_element_by_xpath("/html/body/div[5]/form/div[4]/div[2]/div[4]/button").click()

soup=BeautifulSoup(browser.page_source,"html.parser")
traininfo=soup.select("td")
traininfo2=soup.find_all("a",{"title":"火車時刻表(另開新視窗)"})
traininfo3=soup.select("td span")

trainSrart=[]
trainEnd=[]
trainDuring=[]
trainNO=[]
trainMorS=[]
trainSeat=[]
trainPrice=[]
#basic info
for i in range(len(traininfo)):
    count=int((i+1)/11)
    temp=(i+1)%11
    if temp==1:
        trainSrart.append(traininfo[i].text)
    elif temp==2:
        trainEnd.append(traininfo[i].text)
    elif temp==3:
        trainDuring.append(traininfo[i].text)
    elif temp==5:
        trainMorS.append(traininfo[i].text)
    elif temp==7:
        if "check-circle" in str(traininfo[i]):
            trainSeat.append(">30位")
        elif "exclamation-triangle" in str(traininfo[i]):
            trainSeat.append("30~1位")
        elif "times" in str(traininfo[i]):
            trainSeat.append("無座位")
#train no
for i in range(len(traininfo2)):
    trainNO.append(traininfo2[i].text)
#train price
PriceConverter=lambda e: int(e.replace(',','').replace('$',''))
for i in range(len(traininfo3)):
    if (i+1)%4==2:
        trainPrice.append(PriceConverter(traininfo3[i].text))

for i in range(len(trainNO)):
    print(i+1,"車次: ",trainNO[i])
    print("  起始: ",trainSrart[i])
    print("  到達: ",trainEnd[i])
    print("  時長: ",trainDuring[i])
    print("  線路: ",trainMorS[i],"線")
    print("  座位: ",trainSeat[i])
    print("  票價: ",trainPrice[i])
