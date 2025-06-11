import scrapy
from ..items import LaptopItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import random
import time

class LaptopSpiderSpider(scrapy.Spider):
    name = "laptop_spider"
    start_urls = ["https://hoanghamobile.com/laptop"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)

    def parse(self, response):
        self.logger.info(f"Bắt đầu thu thập từ URL: {response.url}")
        try:
            base_url = "https://hoanghamobile.com/laptop"
            max_pages = 10  # Số trang tối đa để thu thập, điều chỉnh theo nhu cầu

            for page in range(1, max_pages + 1):
                url = f"{base_url}?p={page}" if page > 1 else base_url
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.pj16-item-info"))
                )
                time.sleep(random.uniform(5, 10))  # Chờ ngẫu nhiên để tránh bị chặn

                sel = Selector(text=self.driver.page_source)
                laptops = sel.css("div.pj16-item-info")

                self.logger.info(f"Thu thập được {len(laptops)} sản phẩm trên trang {page}")

                for laptop in laptops:
                    name = laptop.css("h3 a.text-limit::text").get()
                    specs = laptop.css("div.specs ul li.spec-item div span::text").getall()
                    
                    cpu = specs[0].strip() if len(specs) > 0 and specs[0].strip() else None
                    ram = specs[1].strip() if len(specs) > 1 and specs[1].strip() else None
                    rom = specs[2].strip() if len(specs) > 2 and specs[2].strip() else None

                    price_raw = laptop.css("div.price strong::text").get()
                    price = None
                    if price_raw:
                        price_clean = price_raw.strip().replace('.', '').replace('₫', '').strip()
                        try:
                            price = int(price_clean)
                        except ValueError:
                            price = price_clean  # Giữ nguyên nếu không phải số (ví dụ: "Liên hệ")

                    if name and price_raw:
                        item = LaptopItem()
                        item['name'] = name.strip()
                        item['cpu'] = cpu
                        item['ram'] = ram
                        item['rom'] = rom
                        item['price'] = price
                        yield item

                # Kiểm tra nếu không còn sản phẩm trên trang tiếp theo để dừng
                if len(laptops) == 0:
                    self.logger.info(f"Không còn sản phẩm trên trang {page}, dừng thu thập.")
                    break

        except Exception as e:
            self.logger.error(f"Lỗi khi thu thập: {e}")
        finally:
            self.driver.quit()
            self.logger.info("Đã hoàn thành và đóng driver.")

# Hàm click_see_more_loop được giữ lại nhưng hiện không sử dụng do dùng phân trang
def click_see_more_loop(driver, click_selector, wait_for_selector, max_clicks=20, delay=3, logger=None):
    click_count = 0
    while click_count < max_clicks:
        try:
            if logger:
                logger.info(f"[CLICK {click_count + 1}] Đang tìm nút 'Xem thêm'...")
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, click_selector))
            )
            previous_count = len(driver.find_elements(By.CSS_SELECTOR, wait_for_selector))
            driver.execute_script("arguments[0].click();", see_more_button)
            time.sleep(random.uniform(1, delay))
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, wait_for_selector)) > previous_count
            )
            click_count += 1
        except (TimeoutException, ElementClickInterceptedException) as e:
            if logger:
                logger.info(f"[DỪNG] Không còn nút hoặc lỗi khi click: {e}")
            break
        except Exception as e:
            if logger:
                logger.error(f"[LỖI] Lỗi không xác định: {e}")
            break

if __name__ == "__main__":
    # Chạy spider (dùng khi test trực tiếp)
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'INFO',
        'ITEM_PIPELINES': {},
    })
    process.crawl(LaptopSpiderSpider)
    process.start()