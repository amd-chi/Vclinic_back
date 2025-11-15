from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# import threading
import uuid

# from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException


class LoadTimeLimitExceeded(Exception):
    pass


class ASCVDCalculator:
    _instance = None  # for singleton

    @staticmethod
    def get_instance():
        if ASCVDCalculator._instance is None:
            ASCVDCalculator._instance = ASCVDCalculator()
        return ASCVDCalculator._instance

    def __init__(
        self,
        debug: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.thread_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.debug = False
        self.start_time = time.time()
        options = self.get_options()
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1280, 720)
        self.driver.get(
            "https://tools.acc.org/ascvd-risk-estimator-plus/#!/calculate/estimate/"
        )
        time.sleep(0.3)

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

    def safe_click(self, elem):
        try:
            elem.click()
        except ElementClickInterceptedException:
            pass

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

    def calculate_ascvd(
        self,
        age: str,
        is_male: bool,
        sys_bp: int,
        dias_bp: int,
        total_chol: int,
        hdl: int,
        ldl: int,
        has_diabetes: bool,
        smoking: str,
        on_hypertension: bool,
        on_aspirin: bool,
        on_statin: bool,
    ):
        age_elem = self.wait_exists(
            By.XPATH,
            '//*[@id="estimate-page"]/div[1]/div[5]/div[1]/div/div[2]/div/input',
        )
        age_elem.clear()
        age_elem.send_keys(age)

        if is_male:
            male = self.wait_exists(
                By.XPATH,
                "/html/body/div[1]/div[2]/div[1]/div[5]/div[2]/div[2]/div/div/a[1]",
            )
            self.safe_click(male)
        else:
            female = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[2]/div[2]/div/div/a[2]',
            )
            self.safe_click(female)

        race = self.wait_exists(
            By.XPATH,
            '//*[@id="estimate-page"]/div[1]/div[5]/div[3]/div[2]/div/div/a[3]',
        )
        try:
            race.click()

        except ElementClickInterceptedException:
            pass

        sys_bp_elem = self.wait_exists(
            By.XPATH, '//*[@id="estimate-page"]/div[1]/div[5]/div[6]/div[2]/div/input'
        )

        dias_bp_elem = self.wait_exists(
            By.XPATH, '//*[@id="estimate-page"]/div[1]/div[5]/div[7]/div[2]/div/input'
        )
        sys_bp_elem.clear()
        sys_bp_elem.send_keys(sys_bp)
        dias_bp_elem.clear()
        dias_bp_elem.send_keys(dias_bp)

        total_cholestrol_elem = self.wait_exists(
            By.XPATH, '//*[@id="estimate-page"]/div[1]/div[5]/div[9]/div[2]/div/input'
        )
        hdl_cholestrol_elem = self.wait_exists(
            By.XPATH, '//*[@id="estimate-page"]/div[1]/div[5]/div[10]/div[2]/div/input'
        )
        ldl_cholestrol_elem = self.wait_exists(
            By.XPATH, '//*[@id="estimate-page"]/div[1]/div[5]/div[11]/div[2]/div/input'
        )
        total_cholestrol_elem.clear()
        hdl_cholestrol_elem.clear()
        ldl_cholestrol_elem.clear()
        total_cholestrol_elem.send_keys(total_chol)
        hdl_cholestrol_elem.send_keys(hdl)
        ldl_cholestrol_elem.send_keys(ldl)

        if has_diabetes:
            has_diabetes_yes = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[13]/div[2]/div/div/a[1]',
            )
            self.safe_click(has_diabetes_yes)
        else:
            has_diabetes_no = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[13]/div[2]/div/div/a[2]',
            )
            self.safe_click(has_diabetes_no)

        if smoking == "former":
            smoker_former = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[14]/div[2]/div/div/a[2]',
            )
            smoker_former_time = self.wait_exists(
                By.XPATH, '//*[@id="quitSelect"]/option[2]'
            )
            self.safe_click(smoker_former)
            self.safe_click(smoker_former_time)

        elif smoking == "current":
            smoker_current = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[14]/div[2]/div/div/a[1]',
            )
            self.safe_click(smoker_current)

        else:
            smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[14]/div[2]/div/div/a[3]',
            )
            self.safe_click(smoker_never)

        if on_hypertension:
            on_hypertension_treatment_yes = smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[17]/div[2]/div/div/a[1]',
            )

            self.safe_click(on_hypertension_treatment_yes)
        else:
            on_hypertension_treatment_no = smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[17]/div[2]/div/div/a[2]',
            )
            self.safe_click(on_hypertension_treatment_no)
        if on_statin:
            on_aspirin_yes = smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[18]/div[2]/div/div/a[1]',
            )
            self.safe_click(on_aspirin_yes)
        else:
            on_aspirin_no = smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[18]/div[2]/div/div/a[2]',
            )
            self.safe_click(on_aspirin_no)

        if on_aspirin:
            on_aspirin_yes = smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[19]/div[2]/div/div/a[1]',
            )
            self.safe_click(on_aspirin_yes)
        else:
            on_aspirin_no = smoker_never = self.wait_exists(
                By.XPATH,
                '//*[@id="estimate-page"]/div[1]/div[5]/div[19]/div[2]/div/div/a[2]',
            )
            self.safe_click(on_aspirin_no)

        lifetime_ascvd_elem = self.wait_exists(
            By.XPATH, '//*[@id="scorebar"]/div/div/div/div[2]/div[1]/span[1]/span'
        )

        optimal_ascvd_risk_elem = self.wait_exists(
            By.XPATH, '//*[@id="scorebar"]/div/div/div/div[2]/div[2]/span[1]/span'
        )
        ten_year_elem = self.wait_exists(
            By.XPATH, '//*[@id="scorebar"]/div/div/div/div[1]/div[2]/div[1]/div[1]'
        )

        return {
            "lifetime": lifetime_ascvd_elem.text,
            "optimal": optimal_ascvd_risk_elem.text,
            "tenYear": ten_year_elem.text,
        }


# a = ASCVD()
# print(
#     a.calculate_ascvd(
#         "45", True, 99, 70, 140, 30, 35, False, "never", False, True, False
#     )
# )
