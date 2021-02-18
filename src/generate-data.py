from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import subprocess
import json

if __name__ == "__main__":

    generate_data_params = json.load(open("../config/generate-data-params.json"))

    network_stats = generate_data_params["network_stats_path"]
    interface = generate_data_params["interface"]
    playlist = generate_data_params["playlist"]
    outdir = generate_data_params["outdir"]
    resolutions = generate_data_params["resolutions"]

    PATH = "../web-drivers/chromedriver.exe"
    driver = webdriver.Chrome(PATH)

    ## go to playlist
    driver.get(playlist)
    videos = driver.find_elements_by_id("video-title")
    video_links = [link.get_attribute("href") for link in videos]

    driver_wait = WebDriverWait(driver, 15)

    for target_res in resolutions:

        for link in video_links:
            driver.get(link)

            ## skip ad
            ## check if ad is paused

            player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
            print(player_status, flush=True)

            driver.execute_script("return document.getElementById('movie_player').playVideo()")
            print(player_status, flush=True)

            try:
                video_ad = driver_wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ytp-ad-skip-button-container"))
                )
                video_ad.click()
            
            except (NoSuchElementException, TimeoutException) as e:
                pass

            time.sleep(3)

            ## get resolution
            driver.find_element_by_class_name("ytp-settings-button").click()
            driver.find_element_by_xpath("//div[contains(text(),'Quality')]").click()

            time.sleep(2)
            
            quality = driver.find_element_by_xpath("//span[contains(string(), '{}')]".format(target_res))
            quality.click()

            ## collect data
            collect_data = subprocess.Popen(['python', network_stats, '-i' + interface, '-e' + target_res + '-' + link[-1] + '.csv'])
            
            driver.refresh()

            video_len = driver.execute_script(
                            "return document.getElementById('movie_player').getDuration()"
                        )
            print(video_len, flush=True)
            time.sleep(video_len)

            collect_data.terminate()

    driver.close()



