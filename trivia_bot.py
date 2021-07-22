#
# This small example shows you how to access JS-based requests via Selenium
# Like this, one can access raw data for scraping, 
# for example on many JS-intensive/React-based websites
#
import time
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import json
from datetime import datetime
import pandas as pd
import os
import random

class YoutubeTriviaCrack:
    
    def __init__(self):
        self.PROFILE_PATH = './home/.mozilla/firefox/ur_profile'
        self.QUESTION = None
        self.ANSWER = None
        self.REWARD = None
        #firefox initialization
        options = Options()
        #options.headless = True
        #options.add_argument(f'user-agent={user_agent}')
        profile = webdriver.FirefoxProfile(self.PROFILE_PATH)
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference('useAutomationExtension', False)
        profile.update_preferences()
        desired = webdriver.DesiredCapabilities.FIREFOX.copy()
        self.ff_driver = webdriver.Firefox(options=options, firefox_profile=profile, desired_capabilities=desired)
        self.ff_driver.get("https://www.youtube.com/watch?v=DWcJFNfaw9c")
        main_content_wait = WebDriverWait(self.ff_driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[@id="chatframe"]'))
        )
        time.sleep(3)
        video_box = self.ff_driver.find_element_by_xpath('//div[@id="movie_player"]')
        video_box.click()
        print(len(self.ff_driver.find_elements_by_xpath('//ytd-live-chat-frame[@id="chat"]')))
        frame = self.ff_driver.find_elements_by_xpath('//iframe[@id="chatframe"]')
        # switch the webdriver object to the iframe.
        print(len(frame))
        self.ff_driver.switch_to.frame(frame[0])
        #enable 'all' livechat
        self.ff_driver.find_element_by_xpath('//div[@id="label-text"][@class="style-scope yt-dropdown-menu"]').click()
        time.sleep(2.1)
        self.ff_driver.find_element_by_xpath('//a[@class="yt-simple-endpoint style-scope yt-dropdown-menu"][@tabindex="-1"]').click()
        main_content_wait = WebDriverWait(self.ff_driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="style-scope yt-live-chat-text-input-field-renderer"][@id="input"]'))
        )

    def reset_question(self):
        self.QUESTION = None
        self.ANSWER = None
        self.REWARD = None
        
    def set_question(self):
        json_data = None
        with open('./data/youtube_lofi/questions.json') as json_file:
            json_data = json.load(json_file)
            question_count = len(json_data)
            print(question_count)
            random_num = random.randint(0, question_count-1)
            #print(random_num)
            random_question = json_data[random_num]['question']
            answer = json_data[random_num]['answer']
            reward = json_data[random_num]['reward']
            self.QUESTION = random_question
            self.ANSWER = answer
            self.REWARD = reward
            self.announce_question()
            
    def announce_question(self):
        try:
            print(f'sending question')
            chat_box = self.ff_driver.find_element_by_xpath('//div[@class="style-scope yt-live-chat-text-input-field-renderer"][@id="input"]')
            chat_box.click()
            chat_box.send_keys(f'{self.QUESTION}')
            chat_box.send_keys('\ue007')
            time.sleep(1)
            chat_box.send_keys('\ue007')
        except:
            self.announce_question()
        
    
    def question_answered(self, channel_id : str, author : str):
        #see if channel id already in csv
        df = pd.read_csv('./data/youtube_lofi/user_data/user_balances.csv')
        balance = 0.00
        if len(df.loc[df['channel_id'] == f'{channel_id}']) > 0:
            #csv here
            balance = float(df.loc[df['channel_id'] == f'{channel_id}']['balance'].iloc[0])
            balance += self.REWARD
            row = df.loc[df['channel_id']== f'{channel_id}'].index[0]
            df.at[row,'balance'] = balance
            os.remove('./data/youtube_lofi/user_data/user_balances.csv')
            df.to_csv('./data/youtube_lofi/user_data/user_balances.csv', index=False)
        else:
            balance += self.REWARD
            df = df.append({'channel_id':channel_id,'balance':balance}, ignore_index=True)
            df.to_csv('./data/youtube_lofi/user_data/user_balances.csv', index=False)
            
        self.send_msg(f'Congrats, your current earnings are : ${balance:.2f}. Type \'biss earnings\' for more info', author)
            
        self.reset_question()
        
    def set_user_wallet(self, channel_id : str, wallet_addr : str, author : str):
        #see if channel id already in csv
        df = pd.read_csv('./data/youtube_lofi/user_data/user_balances.csv')
        wallet = 'None'
        balance = 0.0
        if len(df.loc[df['channel_id'] == f'{channel_id}']) > 0:
            #csv here
            balance = df.loc[df['channel_id'] == f'{channel_id}']['balance'].iloc[0]
            df.loc[(df['channel_id']==f'{channel_id}')] = [[f'{channel_id}',f'{balance}', f'{wallet_addr}']]
            os.remove('./data/youtube_lofi/user_data/user_balances.csv')
            df.to_csv('./data/youtube_lofi/user_data/user_balances.csv', index=False)
        else:
            df = df.append({'channel_id':channel_id,'balance':balance,'wallet_address':wallet_addr}, ignore_index=True)
            df.to_csv('./data/youtube_lofi/user_data/user_balances.csv', index=False)
            
        self.send_msg(f'Your wallet has been updated to {wallet_addr}', author)
        


    def get_user_balance(self, channel_id : str):
        df = pd.read_csv('./data/youtube_lofi/user_data/user_balances.csv')
        try:
            user_balance = df.loc[df['channel_id'] == f'{channel_id}']['balance'].iloc[0]
        except:
            user_balance = 0.00
        return user_balance

    def send_msg(self, message : str, user : str):
        try:
            print(f'sending {message}')
            chat_box = self.ff_driver.find_element_by_xpath('//div[@class="style-scope yt-live-chat-text-input-field-renderer"][@id="input"]')
            chat_box.click()
            time.sleep(1.3)
            #Clear previous input
            for i in range(50):
                chat_box.send_keys('\ue003')
            chat_box.send_keys(f'{message} @{user}')
            chat_box.send_keys('\ue007')
            time.sleep(1)
            chat_box.send_keys('\ue007')
        except:
            self.send_msg(message, user)

    def combine_message(self, author : str, message : str, channel_id : str):
        return {
            "author" : author,
            "message" : message,
            "channel_id" : channel_id
        }

    def message_logic(self, message : dict):
        if self.QUESTION:
            for word in message['message'].lower().strip().split(' '):
                if word == self.ANSWER:
                    self.question_answered(message['channel_id'], message['author'])
                    break
            '''
            if message['message'].lower().strip() == self.ANSWER:
                self.question_answered(message['channel_id'], message['author'])
            '''
        if message['message'].lower().strip() == 'balance' or message['message'].lower().strip() == 'earnings':
            print('balance!')
            user_balance = self.get_user_balance(message['channel_id'])
            self.send_msg(f'${user_balance:.2f}. you can add an XMR wallet for payout by saying \'biss update wallet\'', message['author'])
        elif 'update wallet' in message['message'].strip():
            print('wallet update!')
            wallet_addr = message['message'].lower().strip().split('update wallet')[1].strip()
            try:
                self.set_user_wallet(message['channel_id'], wallet_addr, message['author'])
            except:
                pass
            
        else:
            pass
    
    def run_loop(self):
        blank_inc = 0
        while True:
            if blank_inc == 200:
                self.set_question()
                blank_inc = 0
            if not self.QUESTION:
                random_num = random.randint(0,100)
                if random_num >= 98:
                    self.set_question()
                    blank_inc = 0
            try:
                df = pd.read_csv('./data/youtube_lofi/reply_runs.csv')
            except: 
                print('no file!')
                blank_inc += 1
                time.sleep(5)
                continue
            try:
                df = df[df['Channel ID'].str.contains('Channel ID') == False]
            except:
                print('no data!')
                time.sleep(5)
                continue
            combined_msgs = [self.combine_message(x, y, z) for x, y, z in zip(df['Author'], df['Message'], df['Channel ID'])]

            for msg in combined_msgs:
                msg_str = msg['message'].lower().replace('biss', '').replace('@', '').replace('#', '')
                msg['message'] = msg_str
                if msg['author'].lower() != 'biss':
                    print(msg_str)
                    self.message_logic(msg)
                    time.sleep(5)
            df = pd.DataFrame()
            os.remove('./data/youtube_lofi/reply_runs.csv')

ytc = YoutubeTriviaCrack()
ytc.set_question()
print(ytc.ANSWER)
ytc.run_loop()
