from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import subprocess
import json

if __name__ == "__main__":

    generate_data_params = json.load(open("../config/stdoan-generate-data-params.json"))

    network_stats = generate_data_params["network_stats_path"]
    interface = generate_data_params["interface"]
    playlist = generate_data_params["playlist"]
    outdir = generate_data_params["outdir"]
    resolutions = generate_data_params["resolutions"]

    PATH = "../web-drivers/chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    driver_wait = WebDriverWait(driver, 30)

    # helper functions
    def enable_video():
      driver.implicitly_wait(3)
      player_state = driver.execute_script(
        "return document.getElementById('movie_player').getPlayerState();")
      print("current state before: " + str(player_state), flush=True)
      
      if player_state in [-1, 2]:
        print("video was paused; resumed now", flush=True)
        driver.execute_script("return document.getElementById('movie_player').playVideo();")

    def skip_ad():
      curr_time = 0
      while curr_time <= 0:

        try:
          video_ad = driver_wait.until(
              EC.element_to_be_clickable((By.CLASS_NAME, "ytp-ad-skip-button-container"))
          )
          video_ad.click()
          print("ad skipped successfully", flush=True)
          break

        except (NoSuchElementException, TimeoutException) as error:
          driver.implicitly_wait(5)
          curr_time = driver.execute_script(
              "return document.getElementById('movie_player').getCurrentTime()"
          )
          if curr_time > 0:
              print("no ad detected", flush=True)
              pass

    def set_quality(resolution):
      quality_changed = False

      while not quality_changed:

          try:
            driver.find_element_by_css_selector('button.ytp-button.ytp-settings-button').click()
            driver.find_element_by_xpath("//div[contains(text(),'Quality')]").click()
            quality = driver.find_element_by_xpath("//span[contains(text(), '{}')]".format(resolution))
            webdriver.ActionChains(driver).move_to_element(quality).click(quality).perform()
            quality_changed = True
            print("Quality changed successfully", flush=True)

          except NoSuchElementException:
            print("Quality button not loaded yet", flush=True)
            time.sleep(15)
  
    # go to playlist
    driver.get(playlist)
    videos = driver.find_elements_by_id("video-title")
    video_links = [link.get_attribute("href") for link in videos]

    for target_res in resolutions:

      preset_resolution = driver.get(video_links[0])
      enable_video()
      skip_ad()
      set_quality(target_res)

      for link in video_links:
        driver.get(link)

        # collect data
        collect_dur = driver.execute_script(
          "return document.getElementById('movie_player').getDuration();"
        )
        buffer = 10
        print("collecting data")
        collect_data = subprocess.Popen(['python', network_stats, '-i' + interface, '-e' + target_res + '-' + link[-1] + '.csv'])
        driver.refresh()
        enable_video()
        skip_ad()
        time.sleep(collect_dur - buffer)

        # ensure that we are actually capturing the video data and not just ads
        while True:
          check_dur = driver.execute_script(
            "return document.getElementById('movie_player').getCurrentTime();"
          )
          # account for ads at beginning and for midroll ads
          remaining = collect_dur - check_dur
          total_collect = collect_dur + remaining

          # check if majority of video has played
          if remaining > buffer:
            time.sleep(remaining - buffer)
          else:
            break
        
        collect_data.terminate()

        print("total collected at " + target_res + " for " + str(total_collect))

    driver.close()






