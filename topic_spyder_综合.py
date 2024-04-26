import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def transfer_clicks(browser):
    """Scroll down to load more data on the page."""
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Give time for page to load

def get_weibo_data(driver, max_weibos=2000):
    """Extract weibo data until a maximum number of weibos is reached."""
    data = []
    previous_length = 0
    no_new_posts = 0

    while len(data) < max_weibos and no_new_posts < 3:
        weibos = driver.find_elements(By.CSS_SELECTOR, 'div.card.m-panel.card9')
        if previous_length == len(weibos):
            no_new_posts += 1  # Increment if no new posts are loaded
        else:
            no_new_posts = 0  # Reset counter if new posts are found

        for weibo in weibos[previous_length:]:
            try:
                content = weibo.find_element(By.CSS_SELECTOR, 'div.weibo-text').text
                username = weibo.find_element(By.CSS_SELECTOR, 'h3.m-text-cut').text
                post_time = weibo.find_element(By.CSS_SELECTOR, 'span.time').text
                shares = weibo.find_element(By.CSS_SELECTOR, 'i.m-font.m-font-forward + h4').text
                comments = weibo.find_element(By.CSS_SELECTOR, 'i.m-font.m-font-comment + h4').text
                likes = weibo.find_element(By.CSS_SELECTOR, 'i.m-icon.m-icon-like + h4').text
                data.append([username, content, post_time, shares, comments, likes])
                if len(data) >= max_weibos:
                    return data
            except Exception as e:
                print(f"Error extracting data: {e}")
                continue

        previous_length = len(weibos)
        transfer_clicks(driver)  # Scroll down to load more posts

    return data

def auto_search_and_fetch_data(keyword):
    driver = webdriver.Chrome()
    driver.get("https://passport.weibo.cn/signin/login")
    input("Please scan QR code to login and press Enter after you have logged in...")

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[type='search']")))
    search_box = driver.find_element(By.CSS_SELECTOR, "[type='search']")
    search_box.send_keys(keyword + Keys.ENTER)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card.m-panel.card9')))

    weibo_data = get_weibo_data(driver, max_weibos=2000)
    
    driver.quit()

    df = pd.DataFrame(weibo_data, columns=['Username', 'Content', 'Post Time', 'Shares', 'Comments', 'Likes'])
    df.to_csv('综合话题数据.csv', index=False)
    print("Data has been saved to '综合话题数据.csv'.")

if __name__ == "__main__":
    keyword = "#小米su7#"
    auto_search_and_fetch_data(keyword)
