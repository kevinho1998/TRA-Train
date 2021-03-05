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
    print("[INFO] Recaptcha Passcode: ",key)
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
    browser.find_element_by_name(field_name).send_keys(value)

def send_key2(field_name,value):
    browser.find_element_by_id(field_name).send_keys(value)

def get_user_info(pinfo):
    pinfo.append(input("Enter start station id :"))
    pinfo.append(input("Enter end station id :"))
    pinfo.append(input("Enter date (yyyy/mm/dd) :"))
    pinfo.append(input("Enter train NO. :"))
    pinfo.append(input("Enter tickit num (1-6):"))
    pinfo.append(input("Enter your id :"))
    return pinfo

#pinfo=[]
#get_user_info(pinfo)
pinfo=["7000","1000","2021/04/01","273","1","J122899733"]
#pinfo=["1210","7000","2021/03/23","288","1","U192053442"]
options=webdriver.ChromeOptions()
options.add_argument('disable-infobars')
options.add_argument('headless')
options.add_argument('defaultViewport:null')
browser=webdriver.Chrome("C:/webdrivers/chromedriver",chrome_options=options)
browser.get('https://tip.railway.gov.tw/tra-tip-web/tip/tip001/tip122/tripOne/byTrainNo')
send_key('pid',pinfo[5])
send_key('ticketOrderParamList[0].startStation',pinfo[0])
send_key('ticketOrderParamList[0].endStation',pinfo[1])
send_key('ticketOrderParamList[0].rideDate',pinfo[2])
send_key('ticketOrderParamList[0].trainNoList[0]',pinfo[3])
send_key('ticketOrderParamList[0].normalQty',pinfo[4])

frames=browser.find_elements_by_tag_name("iframe")
browser.switch_to.frame(frames[0])
delay()
browser.find_element_by_class_name("recaptcha-checkbox-border").click()

#switch to recaptcha audio control frame
browser.switch_to.default_content()
frames=browser.find_element_by_xpath("/html/body/div[6]/div[4]").find_elements_by_tag_name("iframe")
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
    send_key2("audio-response",solve_speech(src).lower())
    browser.find_element_by_xpath("/html/body/div/div/div[7]/div[2]/div[1]/div[2]/button").click()
    delay()
    browser.find_element_by_id("recaptcha-verify-button")
    src2 = browser.find_element_by_id("audio-source").get_attribute("src")
    if src==src2:
        break
#switch back from recaptcha frame
browser.switch_to.default_content()
browser.find_element_by_xpath("/html/body/div[2]/form/div[2]/div[2]/button").click()

soup=BeautifulSoup(browser.page_source,"html.parser")
bookingCode=soup.select("div.float-left span")
booknum =''.join([x for x in str(bookingCode) if x.isdigit()])
print("訂票代碼為:",booknum)

import email.message
import pandas as pd
import smtplib

msg=email.message.EmailMessage()
msg["From"]="610921212@gms.ndhu.edu.com"
msg["To"]='610921212@gms.ndhu.edu.tw'
msg["Subject"]="台鐵訂票-成功"


server=smtplib.SMTP_SSL("smtp.gmail.com",465)
server.login("forkevintesting@gmail.com","ufzxlqbggomjbdzl")
msg.set_content("乘車資訊:\n起站 : "+pinfo[0]+"\n訖站 : "+pinfo[1]+"\n日期 : "+pinfo[2]+"\n車次 : "+pinfo[3]+"\n票數 : "+pinfo[4]+"\n身分證 : "+pinfo[5]+"\n訂票代碼 : "+booknum)
server.send_message(msg)
print("執行完畢!")