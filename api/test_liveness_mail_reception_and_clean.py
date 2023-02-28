
import pytest
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
    url = "https://api.testmail.app/api/json?apikey=89d25786-0bbb-465a-b1d7-bc0a1d90e05b&namespace=hsk6n&pretty=true&timestamp_from={}".format(milliseconds)
    
    # A GET request to the API
    response = requests.get(url)
    # Print the response
    response_json = response.json()
    assert response_json['count'] > 0
