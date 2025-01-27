from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time


def checker(email: str, proxy: str = None) -> Optional[bool]:
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("accept-lang=en")
    chrome_options.add_argument("--headless=new")

    if proxy:
        proxy_type = "http" if "http" in proxy else "socks5"
        chrome_options.add_argument(f"--proxy-server={proxy_type}://{proxy.split('://')[-1]}")

    service = Service(ChromeDriverManager().install())

    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get("https://appleid.apple.com/account#!&page=create")

        wait = WebDriverWait(driver, 60)
        iframe = wait.until(EC.presence_of_element_located((By.ID, "aid-create-widget-iFrame")))
        driver.switch_to.frame(iframe)

        email_field_container = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//label[text()='name@example.com']/preceding-sibling::input[@type='email']")
            )
        )

        email_field_container.click()
        for char in email:
            email_field_container.send_keys(char)

        driver.execute_script(
            """
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            email_field_container,
        )

        try:
            another_field = driver.find_element(By.XPATH, "//input[@type='text']")
            another_field.click()
        except Exception:
            pass

        try:
            result_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[@class='form-message']"))
            )
            result_text = result_container.text.strip().lower()

            if "not available" in result_text:
                return True
            elif "available" in result_text:
                return False
            else:
                return None
        except TimeoutException:
            return False

    except (WebDriverException, TimeoutException):
        return None

    finally:
        time.sleep(3)
        driver.quit()


if __name__ == "__main__":
    print(checker("ivan@mail.com", proxy="socks5://Fm8TZZ6mKdKfegEAlvs9:RNW78Fm5@185.162.130.86:10002"))  # True использованная почта
    print(checker("lumisje19@gmail.com", proxy="http://0gO1dIGMdOks1qnmw8rt:RNW78Fm5@185.162.130.86:10001"))  # False неиспользованная почта
    print(checker("lumsdfdfaa.com", proxy="http://0gO1dIGMdOks1qnmw8rt:RNW78Fm5@185.162.130.86:10002"))  # None некорректная почта
