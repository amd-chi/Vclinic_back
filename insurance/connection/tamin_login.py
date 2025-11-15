from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import uuid
from selenium.common.exceptions import NoSuchElementException
from insurance.connection.tamin_connection import TaminClient


class LoadTimeLimitExceeded(Exception):
    pass


class UnexpectedProblem(Exception):
    pass


class PasscodeIncorrect(Exception):
    pass


class UsernamePasswordIncorrect(Exception):
    pass


class TaminLogin:
    _instance = None  # for singleton

    @staticmethod
    def get_instance():
        if TaminLogin._instance is None:
            TaminLogin._instance = TaminLogin()
        elif TaminLogin._instance.start_time + 300 < time.time():
            TaminLogin._instance.stop()
            TaminLogin._instance = TaminLogin()
        return TaminLogin._instance

    def __init__(
        self,
        debug: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.debug = debug
        self.start_time = time.time()
        options = self.get_options()
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)

    def get_options(self):
        opts = Options()
        opts.ignore_local_proxy_environment_variables()
        opts.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
        )
        opts.add_argument("--incognito")
        if not self.debug:
            opts.add_argument("--headless")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
        # opts.add_argument("--disable-gpu")
        # opts.add_argument(
        #     "--remote-debugging-port=9222"
        # )  # Necessary to prevent DevToolsActivePort error
        return opts

    def wait_load(self):
        while True:
            page_state = self.driver.execute_script("return document.readyState;")
            if page_state == "complete":
                break
            time.sleep(0.5)

    def wait_exists(self, by, value, max_wait=15):
        while True and max_wait > 0:
            try:
                return self.driver.find_element(by=by, value=value)
            except Exception:
                max_wait -= 1
                time.sleep(0.5)
        raise LoadTimeLimitExceeded("Element not found in time limit")

    def send_slow(self, element, text):
        from random import randint

        for i in range(len(text)):
            element.send_keys(text[i])
            time.sleep(randint(1, 3) * 0.1)

    def login_phase1(self, username: str, password: str) -> None:
        try:
            self.driver.get("https://ep.tamin.ir")
            # self.wait_load()
            # print("ready")
            self.wait_exists(
                by=By.XPATH, value='//*[@id="top-id"]/div/div[2]/div[3]/ul/li[1]/button'
            ).click()
            form = self.wait_exists(By.TAG_NAME, "form")
            # form = self.driver.find_element(by=By.TAG_NAME, value="form")
            self.send_slow(
                form.find_element(by=By.CLASS_NAME, value="username"), username
            )
            self.send_slow(
                form.find_element(by=By.CLASS_NAME, value="password"), password
            )
            form.find_element(by=By.CLASS_NAME, value="login-button").click()
            self.wait_load()
            time.sleep(1)
            try:
                notif = self.driver.find_element(
                    by=By.CLASS_NAME, value="my-notify-error"
                )
                if (
                    notif.text
                    == "به دلیل عدم تطابق نام کاربری با گذرواژه امکان ورود به سیستم وجود ندارد"
                ):
                    raise UsernamePasswordIncorrect("Username or password is incorrect")

            except NoSuchElementException:
                pass
            except UsernamePasswordIncorrect:
                raise UsernamePasswordIncorrect("Username or password is incorrect")

            token = self.driver.execute_script(
                'return localStorage.getItem("access_token")'
            )
            if token:
                self.stop()
                taminClient = TaminClient(token)
                taminClient.setOffice()
            return token

        except UsernamePasswordIncorrect:
            self.stop()
            raise UsernamePasswordIncorrect("Username or password is incorrect")
        except Exception as e:
            self.stop()
            raise UnexpectedProblem(e)

    def login_phase2(self, passcode: str) -> str:
        try:
            self.wait_load()
            form = self.driver.find_element(by=By.TAG_NAME, value="form")
            from random import randint

            for i in range(6):
                form.find_elements(by=By.TAG_NAME, value="input")[i].send_keys(
                    passcode[i]
                )
                time.sleep(randint(1, 3) * 0.1)
            form.find_element(by=By.ID, value="submitBtn").click()

            self.wait_load()
            if self.driver.current_url == "https://account.tamin.ir/auth/otp":
                raise PasscodeIncorrect("Passcode is incorrect")
            token = self.driver.execute_script(
                'return localStorage.getItem("access_token")'
            )
            self.stop()
            tamin = TaminClient(token)
            tamin.setOffice()
            return token
        except PasscodeIncorrect:
            raise PasscodeIncorrect("Passcode is incorrect")
        except Exception as e:
            # self.stop()
            raise UnexpectedProblem(e)

    def stop(self):
        self.driver.quit()
        TaminLogin._instance = None

    def load_page_test(self):
        self.driver.get("https://google.com")
        self.wait_load()
        return self.driver.page_source

    def test_connection(self):
        return self.driver.page_source


# class LoginManager:
#     def __init__(self):
#         self.threads = {}

#     def create_thread(self, debug=False, timeout=300) -> TaminLogin:
#         thread = TaminLogin(debug=debug)
#         self.threads[thread.thread_id] = thread
#         thread.start()

#         threading.Timer(timeout, lambda: self.stop_thread(thread.thread_id)).start()
#         return thread

#     def get_thread(self, thread_id) -> TaminLogin:
#         return self.threads.get(thread_id)

#     def stop_thread(self, thread_id):
#         thread = self.get_thread(thread_id)
#         if thread:
#             thread.stop()
#             thread.join()
#             del self.threads[thread_id]
