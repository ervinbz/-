import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver):
    """ 登录微博 """
    driver.get("https://passport.weibo.cn/signin/login")
    print("Please scan QR code to login.")
    input("Press Enter after you have logged in...")

def search_topic(driver, keyword):
    """ 在微博搜索特定话题并允许时间手动选择需要的标签 """
    search_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
    )
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.ENTER)
    print("Please manually select the tab and press Enter to continue...")
    input("After choosing the tab you want, press Enter to continue...")
    time.sleep(3)  # Wait for additional time to manually click 'Hot'

def get_weibo_data(driver, max_weibos=1000):
    """ 爬取微博数据 """
    data = []
    wait = WebDriverWait(driver, 10)
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while len(data) < max_weibos:
        weibos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.card.m-panel.card9')))
        for weibo in weibos[len(data):]:
            try:
                username = weibo.find_element(By.CSS_SELECTOR, 'h3.m-text-cut').text
                content = weibo.find_element(By.CSS_SELECTOR, 'div.weibo-text').text
                post_time = weibo.find_element(By.CSS_SELECTOR, 'span.time').text
                shares = weibo.find_element(By.CSS_SELECTOR, 'i.m-font.m-font-forward + h4').text
                comments = weibo.find_element(By.CSS_SELECTOR, 'i.m-font.m-font-comment + h4').text
                likes = weibo.find_element(By.CSS_SELECTOR, 'i.m-icon.m-icon-like + h4').text
                data.append([username, content, post_time, shares, comments, likes])
                if len(data) >= max_weibos:
                    return data
            except Exception as e:
                print(f"Error extracting data from weibo: {e}")
                continue
        # Scroll down to load more posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.body.scrollHeight") > last_height)
        last_height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(2) 
    return data

def main():
    """ 主函数 """
    driver = webdriver.Chrome()
    try:
        login(driver)
        search_topic(driver, "#小米su7#")
        weibo_data = get_weibo_data(driver, max_weibos=1000)
        df = pd.DataFrame(weibo_data, columns=['Username', 'Content', 'Post Time', 'Shares', 'Comments', 'Likes'])
        df.to_csv('热门话题数据.csv', index=False)
        print("Data has been saved to '热门话题数据.csv'.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
