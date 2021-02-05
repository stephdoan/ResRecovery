from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time

resolutions = [
    '240p',
    '480p'
]

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
video_links = [link.get_attribute("href") for link in videos]

for link in video_links:
    driver.get(link)
    print(driver.title)

    ## skip ad

    time.sleep(10)
    
    try:
        skip_ad = driver.find_element_by_class_name("ytp-ad-skip-button-container")
        skip_ad.click()
    
    except NoSuchElementException:
        pass

    ## mute
    mute_btn = driver.find_element_by_class_name("ytp-mute-button")
    volume_status = mute_btn.get_attribute("title")

    if "Mute" in volume_status:
        mute_btn.click()

    time.sleep(2)
    print(volume_status)

    ## iterate through resolutions

    for curr_res in resolutions:
        playback_settings = driver.find_element_by_class_name("ytp-settings-button")
        playback_settings.click()
        
        time.sleep(2)
        
        driver.find_element_by_xpath("//div[contains(text(),'Quality')]").click()
        
        time.sleep(2)
        
        quality = driver.find_element_by_xpath("//span[contains(string(), '{}')]".format(curr_res))
        quality.click()

    ## get video duration
    time.sleep(2)
    video_dur = driver.execute_script(
                    "return document.getElementById('movie_player').getCurrentTime()"
                    )

    video_len = driver.execute_script(
                    "return document.getElementById('movie_player').getDuration()"
                    )

    print(video_len)

    time.sleep(5)

driver.close()

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
