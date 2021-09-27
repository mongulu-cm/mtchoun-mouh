import boto3
import pytest as pytest
from boto3 import client
from config import stopWords, bucket_name, Table_Users, images_url_path,region
from moto import mock_s3

@pytest.fixture(autouse=true)
def env_setup(monkeypatch):
    monkeypatch.setenv('REGION','eu-central-1')

@pytest.fixture
def test_Images_in_Bucket():
    with mock_s3():
        s3=client("s3")
        s3.create_bucket(Bucket='bucket_fabiola')
        assert Images_in_Bucket('bucket_fabiola')==[]
