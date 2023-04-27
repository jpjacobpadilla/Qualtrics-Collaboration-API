import time
import random
from typing import Union
import scipy.stats as stats # For human sleeping
from getpass import getpass 
import requests
import uuid # Used to generate two of the request headers

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


class CollaborationClient:
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
        
        # The subdomain is the one infront of the Qualtrics url
        self.subdomain = 'nyu'

    def login(self) -> None:
        # If your password has spaces at the begingin or front, remove strip...
        nyu_username: str = input('NYU username:').strip()
        nyu_password: str = getpass('NYU password:').strip()
        print('-' * 30) # Break up the print statments

        self._selenium_login(nyu_username, nyu_password)
        print('-' * 30) # Break up the print statments

    def add_collaborator(self, survey_id: str, collaboration_username: str) -> dict[str, str]:
        """This is the main method of the object which allows you to add collaborators to a survey."""
        
        url = f'https://{self.subdomain}.qualtrics.com/survey-collaboration/v1/shares/{survey_id}'

        # I tried making the payload nicer, but it seems to be very finicky.
        payload = {
            'shareStatus': f'{{"{collaboration_username}":"added"}}',
            'shareType': f'{{"{collaboration_username}":"Invitation"}}',
            'inviteDetails': f'{{"{collaboration_username}":{{}}}}',
            'inviteMessages': '{}',
            'permissions': f'{{"{collaboration_username}":{{"viewSurveys":true,"editSurveys":true,"translateSurveys":true,"copySurveyQuestions":true,"setSurveyOptions":true,"createResponseSets":true,"editQuestions":true,"deleteSurveyQuestions":true,"editSurveyFlow":true,"editTextiQBasic":true,"useBlocks":true,"useAEConjoint":true,"useAETriggers":true,"useScreenouts":true,"useAdvancedQuotas":true,"useTableOfContents":true,"useReferenceBlocks":true,"editResultSets":true,"exportSurveyData":true,"viewSurveyResults":true,"useCrossTabs":true,"useSubgroupAnalysis":true,"viewResponseID":true,"viewPersonalData":true,"viewTextiQBasic":true,"activateSurveys":true,"copySurveys":true,"distributeSurveys":true}}}}',
            'SurveyID': survey_id
        }
        
        headers = self._generate_qualtrics_headers(content_type='application/x-www-form-urlencoded; charset=utf-8')
        
        resp = self.session.post(url, headers=headers, data=payload)
        return resp.text

    def enter_collaboration_code(self, code: str) -> dict[str, str]:
        """
        This method takes in a collaboration code and allows you to 
        programatically enter the collaboration code into Qualtrics 
        so that you can work on a shared survey.
        """
        url = f'https://{self.subdomain}.qualtrics.com/survey-collaboration/v1/invitations/accept'

        payload = f'{{"token":"{code}"}}'
        
        headers = self._generate_qualtrics_headers(content_type='application/json; charset=UTF-8')
        
        resp = self.session.post(url, headers=headers, data=payload)        
        return resp.text

    @property
    def cookies(self) -> dict[str, str]:
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def _generate_qualtrics_headers(self, content_type: str) -> dict:
        return {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': content_type,
            'referer': f'https://{self.subdomain}.qualtrics.com/Q/MyProjectsSection',
            'x-xsrf-token': self.cookies.get('XSRF-TOKEN'),
            'user-agent': self.user_agent,
            'origin': f'https://{self.subdomain}.qualtrics.com',
            'x-request-id': str(uuid.uuid4()),
            'x-transaction-id': str(uuid.uuid4())
        }

    def _selenium_login(self, nyu_username: str, nyu_password: str) -> None:
        # Intial Setup of Selenium options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={self.user_agent}")

        # Path to chromedriver
        service = webdriver.chrome.service.Service("/usr/bin/chromedriver")

        # create an instance of the Chrome browser driver
        driver = webdriver.Chrome(options=options)

        print('Starting...')
        driver.get(f"https://{self.subdomain}.qualtrics.com/ControlPanel/")

        username_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'username')))
        self.human_sleep()
        print('Typing in username...')
        self._human_type(username_input, nyu_username)

        password_input = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'password')))
        self.human_sleep()
        print('Typing in password...')
        self._human_type(password_input, nyu_password)

        login_xpath = '//button[contains(text(), "Login") and @type = "submit"]'
        login_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, login_xpath)))
        self.human_sleep()
        login_button.click()
        print('Logging in - \033[91mYou may need to accept the two-step verification.\033[0m')

        # Now we wait for things to load. The user needs to accept two factor auth and 
        # there may be a pop-up asking if we can trust the browser (from NYU)
        while not self._at_qualtrics(driver):
            if self._check_for_trust_browser_page(driver):
                trust_browser_button = driver.find_element(By.ID, 'trust-browser-button')
                trust_browser_button.click()
                self.human_sleep()

        driver.get(f'https://{self.subdomain}.qualtrics.com/Q/MyProjectsSection')

        # Get Selenium cookies and then put it into a request session.
        cookies = driver.get_cookies()
        for cookie in cookies:
            self.session.cookies.set(cookie["name"], cookie["value"])

        driver.quit()

    @staticmethod
    def human_sleep() -> None:
        """
        A method that models how humans probably click around websites.
        """
        def sleep_len(mu: Union[int, float] = 3.3, sigma: Union[int, float] = 0.9, 
                      lower: Union[int, float] = 2, upper: Union[int, float] = 6
                    ) -> float:
            X = stats.truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
            return round(X.rvs(1)[0], 2)

        time.sleep(sleep_len())

    @staticmethod
    def _human_type(element: WebElement, string: str) -> None:
        for char in string:
            if char in ["!", ".", "?", ","]:
                time.sleep(random.uniform(.6, 1))
            elif char == " ":
                time.sleep(random.uniform(.14, .20))
            else:
                time.sleep(random.uniform(.1, .13))

            element.send_keys(char)

    @staticmethod
    def _at_qualtrics(driver: webdriver) -> bool:
        # This is looking for the footer link
        qualtrics_svg_xpath = '//a[@href="http://www.qualtrics.com"]'
        try:
            driver.find_element(By.XPATH, qualtrics_svg_xpath)
            return True
        except NoSuchElementException:
            return False

    @staticmethod
    def _check_for_trust_browser_page(driver: webdriver) -> bool:
        try:
            driver.find_element(By.ID, 'trust-browser-button')
            return True
        except NoSuchElementException:
            return False
