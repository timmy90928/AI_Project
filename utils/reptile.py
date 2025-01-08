from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# 初始化 WebDriver
options = Options()
# options.add_argument('--headless')  # 無頭模式，不開啟瀏覽器視窗
options.add_argument('--disable-gpu')  # 禁用 GPU，加速運行
options.add_argument('--disable-usb')  # 禁用 GPU，加速運行
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

# 打開 Google Maps 網頁
driver.get("https://www.google.com/maps")

# 等待地圖加載完成
time.sleep(2)  # 可以根據需要調整等待時間

# 嘗試查詢或抓取你需要的元素
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys("阿忠海產羊肉")
search_box.send_keys(Keys.RETURN)

# 等待搜尋結果加載
time.sleep(2)

# 取得地圖資訊或其他資料
# 例如抓取一些文本或地圖上的資訊
# 這裡你可以抓取具體元素的內容
# results = driver.find_elements(By.CLASS_NAME, "g2BVhd eoFzo ")
popular_times_element = driver.find_element(By.XPATH, '//div[@class="b9vadd mwpKpe"]')
print(popular_times_element.text)

# 關閉瀏覽器
driver.quit()
