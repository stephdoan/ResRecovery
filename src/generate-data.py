from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

PATH = "../web-drivers/chromedriver.exe"
# driver_options = Options()
# driver_options.headless = True
driver = webdriver.Chrome(PATH)#, options=driver_options)

## users need to supply a playlist of videos to watch from

## or should this iterate through resolutions and then an outer
## wrapper function iterates through a playlist?

## go to playlist
driver.get("https://youtube.com/playlist?list=PL51jetv1tnxncETYqCffQTfyOyES9YOVx")

videos = driver.find_elements_by_id("video-title")
video_links = [link.get_attribute('href') for link in videos]

for link in video_links:
    driver.get(link)
    print(driver.title)
    time.sleep(10)

driver.close()
## click a video
# videos = driver.find_element_by_id("thumbnail")
# videos.click()
#
# # wait & skip ad
# time.sleep(10)
#
# skip_ad = driver.find_elements_by_class_name("ytp-ad-skip-button-container")
#
# if len(skip_ad) > 0:
#     skip_ad[0].click()
#
# playback_settings = driver.find_element_by_class_name("ytp-settings-button")
# playback_settings.click()
#
# time.sleep(2)
#
# driver.find_element_by_xpath("//div[contains(text(),'Quality')]").click()
#
# time.sleep(2)
#
# quality = driver.find_element_by_xpath("//span[contains(string(),'144p')]")
# quality.click()
# print("Element is visible? " + str(quality.is_displayed()))
#
# driver.close()
