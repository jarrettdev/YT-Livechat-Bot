#
# This small example shows you how to access JS-based requests via Selenium
# Like this, one can access raw data for scraping, 
# for example on many JS-intensive/React-based websites
#
from time import sleep
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import json
from datetime import datetime
import pandas as pd

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def log_filter(log_):
    return (
        # is an actual response
        log_["method"] == "Network.responseReceived"
        # and json
        and "json" in log_["params"]["response"]["mimeType"]
    )

# make chrome log requests
capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}  # newer: goog:loggingPrefs
driver = webdriver.Chrome(
    desired_capabilities=capabilities
)

# fetch a site that does xhr requests
driver.get("https://www.youtube.com/watch?v=DWcJFNfaw9c")
sleep(60)  # wait for the requests to take place

while True:

    # extract requests from logs
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

    json_list = []
    for log in filter(log_filter, logs):
        request_id = log["params"]["requestId"]
        resp_url = log["params"]["response"]["url"]
        #print(f"Caught {resp_url}")
        if 'https://www.youtube.com/youtubei/v1/live_chat/get_live_chat?key=' in resp_url:
            with open('look.txt', 'a', encoding='utf-8') as text_file:
                body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                text_file.write(str(body))
                json_list.append(body)

    print(len(json_list))

    message_list = []

    for i in range(len(json_list)):
        json_data = json.loads(json_list[i]['body'].replace('\n','').strip())
        try:
            actions = (json_data['continuationContents']['liveChatContinuation']['actions'])
        except:
            continue
        for j in range(len(actions)):
            try:
                item = actions[j]['addChatItemAction']['item']['liveChatTextMessageRenderer']
                author_channel_id = item['authorExternalChannelId']
                author_name = item['authorName']['simpleText']
                text = item['message']['runs'][0]['text']
                post_time = item['timestampUsec']
                post_time = post_time[0:10]
                post_time = int(post_time)
                author_photo = item['authorPhoto']['thumbnails'][0]['url']
                post_time = datetime.utcfromtimestamp(post_time)

                post_item = {
                    "Author" : author_name,
                    "Message" : text,
                    "Date" : post_time,
                    "Channel" : f'https://youtube.com/channel/{author_channel_id}'
                }
                message_list.append(post_item)
                #print(post_item)
            except Exception as e:
                print(str(e))
                continue

    #message_list = list(set(message_list))
    df = pd.DataFrame(message_list)
    df = df.drop_duplicates()
    #print(df)

    df.to_csv('./data/youtube_lofi/test_run.csv', index=False, mode='a')
    sleep(30)

driver.quit()

