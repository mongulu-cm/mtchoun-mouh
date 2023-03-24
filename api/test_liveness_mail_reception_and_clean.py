import pytest
import os
import time
import json
import requests
from datetime import datetime,timedelta
 
class TestLivenessNonUi():
  def setup_method(self, method):
    self.vars = {}
  
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
