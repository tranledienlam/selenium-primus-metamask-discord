import re
import argparse
from pathlib import Path
from browser_automation import BrowserManager

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.common.keys import Keys

from browser_automation import Node
from utils import Utility


class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get("profile_name")
        self.password = profile.get("password")
        self.url_wallet = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn"
        self.url_primus = "chrome-extension://oeiomhmbaapihbilkfkhmlajkeegnjhe"
        self.url_discord = "https://discord.com"

    def click_button_popup(self, selector: str, text: str = ''):
        Utility.wait_time(5)
        try:
            js = f'''
            Array.from(document.querySelectorAll('{selector}')).find(el => el.textContent.trim() === "{text}").click();
            '''
            self.driver.execute_script(js)
            self.node.log(f'click  ({selector}, {text})')
            
            return True
        except NoSuchWindowException:
            self.node.log(f'Không thể click ({selector}, {text}). Cửa sổ đã đóng')
        except Exception as e:
            if 'undefined' in str(e):
                self.node.log(f'Không tìm thấy ({selector}, {text})')
            else:
                self.node.log(f'{e}')

        return False
    
    def unlock_wallet(self):
        actions = [
            (self.node.go_to, f"{self.url_wallet}/home.html", "get"),
            (
                self.node.find_and_input,
                By.CSS_SELECTOR,
                'input[id="password"]',
                self.password,
                None,
                0.1,
            ),
            (self.node.find_and_click, By.XPATH, '//button[text()="Unlock"]'),
        ]

        return self.node.execute_chain(actions=actions, message_error="Unlock wallet failed")
    
    def connect_wallet(self):
        self.node.reload_tab(5)
        text = self.node.get_text(By.CSS_SELECTOR, 'div.pConnect span', wait=10)
        if text and ('Connect' in text):
            self.node.find_and_click(By.CSS_SELECTOR, 'div.pConnect span.btnText')
            self.node.find_and_click(By.XPATH, '//div[@class="name"][text()="MetaMask"]')
            self.node.switch_tab(self.url_wallet)
            self.click_button_popup('button', 'Connect')
            self.click_button_popup('button', 'Confirm')
        else:
            self.node.log('Wallet already connected')
        
        return True

    def check_discord_login(self):
        self.node.reload_tab()
        login_btn = self.node.find(By.CSS_SELECTOR, '.login-button-js', wait=15)
        if login_btn:
            href = login_btn.get_attribute('href')
            if 'me' in href:
                self.node.log('Discord login success')
                return True
            elif 'login' in href:
                self.node.log('Discord not login')
                return False
        else:
            return False

    def gm_discord(self):
        self.node.new_tab(self.url_discord)
        
        if not self.check_discord_login():
            self.node.snapshot(f'[Primus] Discord not login', stop=False)
            return False
            
        self.node.go_to(f'{self.url_discord}/channels/1125704047085760595/1257875620365471830', wait=5)
        actions = [
            (self.node.find_and_input, By.CSS_SELECTOR, 'span[data-slate-leaf="true"]', 'gm'),
            (self.node.find_and_input, By.CSS_SELECTOR, 'span[data-slate-leaf="true"]', Keys.ENTER),
        ]

        if not self.node.execute_chain(actions=actions, message_error="Gm discord failed"):
            self.node.snapshot(f'[Primus] Gm discord failed', stop=False)
            return False
        
        return True

    def check_achievement(self):
        is_gm = self.gm_discord()
        self.node.switch_tab(self.url_primus)
        self.node.find_and_click(By.XPATH, '//li[div[text()="Achievements"]]')
        self.node.reload_tab()

        Utility.wait_time(10)
        if not self.node.find_and_click(By.XPATH, '//div[div[div[text()="Daily check-in"]]]//button'):
            self.node.log('Daily check-in success')
        if is_gm:
            if not self.node.find_and_click(By.XPATH, '//div[div[div[text()="Daily Discord GM"]]]//button'):
                self.node.log('Daily Discord GM success')

    def _run(self):
        self.unlock_wallet()
        self.node.go_to(f"{self.url_primus}/home.html",'get')
        if not self.connect_wallet():
            self.node.snapshot(f'[Primus] connect wallet failed')
        self.check_achievement()


class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile

    def _run(self):
        # code 8KIAEJR
        self.node.go_to(f'chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html', 'get')
        self.node.new_tab(f'chrome-extension://oeiomhmbaapihbilkfkhmlajkeegnjhe/home.html', 'get')
        self.node.new_tab(f'https://discord.gg')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Chạy ở chế độ tự động")
    parser.add_argument("--headless", action="store_true", help="Chạy trình duyệt ẩn")
    args = parser.parse_args()

    DATA_DIR = Path(__file__).parent / "data.txt"

    if not DATA_DIR.exists():
        print(f"File {DATA_DIR} không tồn tại. Dừng mã.")
        exit()

    proxy_re = re.compile(r"^(?:\w+:\w+@)?\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}$")
    PROFILES = []
    num_parts = 2  # số dữ liệu, không bao gồm proxy

    with open(DATA_DIR, "r") as file:
        data = file.readlines()

    for line in data:
        parts = [part.strip() for part in line.strip().split("|")]

        proxy_re = re.compile(r"^(?:\w+:\w+@)?\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}$")
        proxy_info = parts[-1] if proxy_re.match(parts[-1]) else None
        if proxy_info:
            parts = parts[:-1]

        if len(parts) < num_parts:
            print(f"Warning: Dữ liệu không hợp lệ - {line}")
            continue

        profile_name, password, *_ = (parts + [None] * num_parts)[:num_parts]

        PROFILES.append(
            {
                "profile_name": profile_name,
                # 'username': username,
                "password": password,
                "proxy_info": proxy_info,
            }
        )

    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    browser_manager.config_extension("meta-wallet-*.crx")
    browser_manager.config_extension("Primus-*.crx")
    # browser_manager.run_browser(PROFILES[0])
    # browser_manager.run_stop(PROFILES)
    browser_manager.run_terminal(
        profiles=PROFILES,
        max_concurrent_profiles=4,
        auto=args.auto,
        headless=args.headless
    )
