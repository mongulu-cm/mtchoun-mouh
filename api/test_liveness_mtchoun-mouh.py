# Generated by Selenium IDE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
from datetime import datetime,timedelta
import boto3
import os

class TestLiveness():
  def setup_method(self, method):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    self.driver = webdriver.Chrome(chrome_options=chrome_options)
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_liveness(self):
    WEBSITE_URL_MAIL_NAMESPACE =  os.environ["WEBSITE_URL_MAIL_NAMESPACE"]

    # Test name: liveness
    # Step # | name | target | value | comment 
    # 1 | open | / |  | 
    self.driver.get(WEBSITE_URL_MAIL_NAMESPACE)
    # 2 | setWindowSize | 976x1016 |  | 
    self.driver.set_window_size(976, 1016)
    # 3 | click | id=name-input |  | 
    self.driver.find_element(By.ID, "name-input").click()
    self.driver.find_element(By.ID, "name-input").send_keys("MONGULU Liveness")
    self.driver.find_element(By.ID, "email-input").send_keys("hsk6n.mtchoun-mouh.mongulu-cm.hsk6n@inbox.testmail.app")
    # 6 | click | css=.btn-primary |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
    # 7 | click | css=.col-4 |  | 
    self.driver.find_element(By.CSS_SELECTOR, ".col-4").click()
    time.sleep(10)
  

  def test_check_mail_reception(self):

    print("Current date:",datetime.utcnow())
    date= datetime.utcnow()+timedelta( minutes = -3) - datetime(1970, 1, 1)
    milliseconds = round(date.total_seconds()*1000)

    API_KEY_TEST_MAIL = os.environ["API_KEY_TEST_MAIL"]   
    TEST_MAIL_NAMESPACE = os.environ["TEST_MAIL_NAMESPACE"]

    url = "https://api.testmail.app/api/json?apikey={}&namespace={}&pretty=true&timestamp_from={}".format(API_KEY_TEST_MAIL, TEST_MAIL_NAMESPACE, milliseconds)

    # A GET request to the API
    response = requests.get(url)
    response_json = response.json()
    # we should have at leat one mail receive with in 3 past minutes
    assert response_json['count'] > 0


  def test_remove_liveness_user(self):
    """
    remove user previously created from the liveness check
    """
    AWS_REGION = os.environ["AWS_REGION"]
    TABLE = os.environ["REGISTERS_TABLE"]	
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

    LIVENESS_USER="mongulu liveness" 

    table = dynamodb.Table(TABLE)

    response = table.delete_item(
        Key={
            'Name':LIVENESS_USER
        }
    )

    status_code = response['ResponseMetadata']['HTTPStatusCode']
    assert "200" == str(status_code)
