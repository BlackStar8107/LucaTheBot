import zendriver as zd
from dotenv import load_dotenv
import time, logging, os, datetime

logger = logging.getLogger(__name__)

def log(message, level):
    match level:
        case logging.DEBUG:
            print(datetime.datetime.now(), "|| DEBUG || ", message)
            logger.debug(message)

        case logging.INFO:
            print(datetime.datetime.now(), "|| INFO || ", message)
            logger.info(message)

        case logging.WARNING:
            print(datetime.datetime.now(), "|| WARNING || ", message)
            logger.warning(message)

        case logging.ERROR:
            print(datetime.datetime.now(), "|| ERROR || ", message)
            logger.error(message)

        case logging.CRITICAL:
            print(datetime.datetime.now(), "|| CRITICAL || ", message)
            logger.critical(message)

def likeTheVideo(url):
    LOGIN_URL = "https://accounts.google.com/AddSession?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den-GB%26next%3D%252F&hl=en-GB&passive=false&service=youtube&uilel=0"
    EMAIL = os.getenv("EMAIL")
    PASSW = os.getenv("PASSW")

    driver = zd.Chrome(use_subprocess=True)
    wait = WebDriverWait(driver, 20)
    driver.get(LOGIN_URL)

    wait.until(EC.visibility_of_element_located((By.NAME,'identifier'))).send_keys(EMAIL)
    wait.until(EC.visibility_of_element_located((By.NAME,'Passwd'))).send_keys(PASSW)
    time.sleep(3)

    driver.get(url)
    # Pause The Video
    driver.find_element_by_css_selector('#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-left-controls > button').click()
    time.sleep(1)

    # Click The Like Button
    driver.find_element_by_xpath('/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[4]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[2]/div/div/ytd-menu-renderer/div[1]/segmented-like-dislike-button-view-model/yt-smartimation/div/div/like-button-view-model/toggle-button-view-model/button-view-model/button/yt-touch-feedback-shape/div[2]').click()

    time.sleep(4)

    driver.close()

async def likeTheVideoV2(url):
    LOGIN_URL = "https://accounts.google.com/AddSession?continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den-GB%26next%3D%252F&hl=en-GB&passive=false&service=youtube&uilel=0"
    EMAIL = os.getenv("EMAIL")
    PASSW = os.getenv("PASSW")

    browser = await zd.start(headless=True)

    login_page = await browser.get(LOGIN_URL)

    email_entry = await login_page.find("Email or phone", best_match=True)
    await email_entry.click()

    await email_entry.send_keys(EMAIL)

    next_button = await login_page.find("Next", best_match=True)
    await next_button.click()

    await login_page.sleep(3)

    password_entry = await login_page.find("Enter your password")
    await password_entry.click()

    await password_entry.send_keys(PASSW)
    next_button = await login_page.find("Next", best_match=True)
    await next_button.click()

    if type(url) == list:
        for a_url in url:
            video_page = await browser.get(a_url)
            await video_page.sleep(5)
            like_button = await video_page.select("ytd-menu-renderer.ytd-watch-metadata > div:nth-child(1) > segmented-like-dislike-button-view-model:nth-child(1) > yt-smartimation:nth-child(1) > div:nth-child(1) > div:nth-child(1) > like-button-view-model:nth-child(1) > toggle-button-view-model:nth-child(1) > button-view-model:nth-child(1) > button:nth-child(1) > yt-touch-feedback-shape:nth-child(3) > div:nth-child(2)")
            await like_button.click()
    else:
        video_page = await browser.get(url)
        await video_page.sleep(5)
        like_button = await video_page.select("ytd-menu-renderer.ytd-watch-metadata > div:nth-child(1) > segmented-like-dislike-button-view-model:nth-child(1) > yt-smartimation:nth-child(1) > div:nth-child(1) > div:nth-child(1) > like-button-view-model:nth-child(1) > toggle-button-view-model:nth-child(1) > button-view-model:nth-child(1) > button:nth-child(1) > yt-touch-feedback-shape:nth-child(3) > div:nth-child(2)")
        await like_button.click()

    await video_page.sleep(1)
    await video_page.close()
    await browser.stop()
    
if __name__ == "__main__":
    with open("LucaTheLiker.log", "w"):
        pass
    logging.basicConfig(filename="LucaTheLiker.log", level=logging.DEBUG, format="%(asctime)s || %(levelname)s || %(message)s")

    log("Logging Started", logging.INFO)

    log("Loading DotEnv", logging.INFO)

    load_dotenv()

    log("Loaded DotEnv", logging.INFO)

    URL = "https://www.youtube.com/watch?v=ZQc1VxCfbS8"

    zd.loop().run_until_complete(likeTheVideoV2(URL))

