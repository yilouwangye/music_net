# !usr/bin/env python
# -*-coding:utf-8 -*-

# @FileName: music.py
# @Author:tian

from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import StaleElementReferenceException,NoSuchElementException
from pymongo import MongoClient
import time
from config import *


class Music():
    def __init__(self):
        '''初始化'''
        self.desired_caps = {
            'platformName': 'Android',
            'deviceName': 'MAR_AL00',
            'appPackage': 'com.netease.cloudmusic',
            'appActivity': '.activity.LoadingActivity'
        }
        self.driver = webdriver.Remote(DRIVER_SERVER,self.desired_caps)
        self.wait = WebDriverWait(self.driver,TIMEOUT)
        self.client = MongoClient(host=HOST,port=PORT)
        self.db = self.client[MONGO_DB]
        self.col = self.db[MONGO_COLLECTION]

    def login(self):
        '''
        登录步骤
        :return:
        '''
        # 同意条款
        agree = self.wait.until(EC.presence_of_element_located((By.ID,'com.netease.cloudmusic:id/ek')))
        agree.click()
        # 授权
        authorize = self.wait.until(EC.presence_of_element_located((By.ID,'com.netease.cloudmusic:id/bl_')))
        authorize.click()
        # 确认读取手机内存信息等
        sure = self.wait.until(EC.element_to_be_clickable((By.ID,'android:id/button1')))
        sure.click()
        # 网易云开场动画，设置等待时间
        time.sleep(30)
        # 勾选同意用户协议,可开启指针获取定位坐标
        self.driver.tap([(168,2231),],1)
        time.sleep(2)
        # 选择登录方式，此处为邮箱
        select_email = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.netease.cloudmusic:id/b2q')))
        select_email.click()
        # 输入账号信息
        user_name = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@resource-id="com.netease.cloudmusic:id/aa2"]')))
        user_name.set_text(USER_NAME)
        # 密码
        pwd = self.wait.until(EC.presence_of_element_located((By.ID, 'com.netease.cloudmusic:id/bkv')))
        pwd.send_keys(USER_PASSWORD)
        # 登录
        login_button = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.netease.cloudmusic:id/b0u')))
        login_button.click()

    def process(self):
        '''
        target:获取用户历史歌单歌曲列表
        step:点击【我的】--最近播放--歌单--选择目标歌单--获取歌曲信息
        :return:
        '''
        # 我的音乐
        my_music = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//android.widget.TextView[@content-desc="我的音乐"]')))
        my_music.click()
        # 找到最近播放，首次登录无法看到【更多】选项，设置下拉操作，使之显示
        time.sleep(2)
        self.driver.swipe(500, 600, 500, 1000, 5000)
        recently_music = self.wait.until(EC.presence_of_element_located((By.ID, 'com.netease.cloudmusic:id/cv8')))
        recently_music.click()
        # 进入歌单,此处设置坐标点击，也可以使用xpath
        time.sleep(2)
        self.driver.tap([(728, 291), ], 100)
        # 选择歌单,若目标不在屏幕范围内，请设置下拉
        target_music_list = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@text="学习用【安静的纯音乐】〈合订版〉"]')))
        target_music_list.click()
        time.sleep(2)

    def crawl(self):
        '''
        获取歌曲信息,写入数据库
        :return:
        '''
        for i in range(20):
            # 这里的i值根据歌单调整
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//*[@resource-id="com.netease.cloudmusic:id/b_2"]')))
            try:
                for item in items:
                    song = item.find_element_by_xpath(
                        '//*[@resource-id="com.netease.cloudmusic:id/cdp"]').get_attribute('text')
                    author = item.find_element_by_xpath(
                        '//*[@resource-id="com.netease.cloudmusic:id/cdl"]').get_attribute('text')

                    data = {
                        'song': song,
                        'author': author
                    }
                    print(data)
                    # 更新到数据库，有则更新，无则写入
                    self.col.update({'song':song,'author':author},{'$set':data},True)
                    time.sleep(5)
            except(StaleElementReferenceException, NoSuchElementException):
                pass
            self.driver.swipe(START_X, START_Y + DISTANCE,START_X,START_Y)
            time.sleep(5)

    def main(self):
        '''
        :return:
        '''
        self.login()
        self.process()
        self.crawl()

if __name__ == '__main__':
    m = Music()
    m.main()






