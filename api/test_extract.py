import boto3
import botocore
import pytest as pytest
from boto3 import client
from config import stopWords, images_url_path
from moto import mock_s3
from extract import Images_in_Bucket,Empty_Bucket, Delete_Image

@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv('REGION','eu-central-1')

@mock_s3
def test_images_in_bucket():
    #with mock_s3():
        conn = boto3.resource('s3',region_name='us-east-1')
        conn.create_bucket(Bucket='bucket_fabiola')
        assert Images_in_Bucket('bucket_fabiola') == []

        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(Bucket='bucket_fabiola', Key='toto', Body='tata')
        assert Images_in_Bucket('bucket_fabiola') == ['toto']


@mock_s3
def test_Empty_Bucket():
    #with mock_s3():
        s3 = boto3.client('s3',region_name='us-east-1')
        s3.create_bucket(Bucket='bucket_fabiola')
        s3.put_object(Bucket='bucket_fabiola', Key='toto')
        Empty_Bucket('bucket_fabiola')
        response = s3.list_objects(Bucket='bucket_fabiola')
        assert "Contents" not in response.keys()


@mock_s3
def test_Delete_Image():
    s3 = boto3.client('s3')
    conn = boto3.resource('s3', region_name='us-east-1')
    conn.create_bucket(Bucket='bucket_fabiola')
    s3.put_object(Bucket='bucket_fabiola', Key='toto')
    s3.put_object(Bucket='bucket_fabiola', Key='tata')
    Delete_Image('bucket_fabiola', 'toto')
    response=s3.list_objects(Bucket='bucket_fabiola')
    assert len(response["Contents"])==1
    assert response["Contents"][0]["Key"]=="tata"



