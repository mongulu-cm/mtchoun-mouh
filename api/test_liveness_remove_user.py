import boto3
 
class TestLivenessRmoveLivenessUser():

  
  def test_remove_liveness_user(self):
    """
    remove user previously created from the liveness check
    """
    dynamodb = boto3.resource('dynamodb')

    LIVENESS_USER="mongulu liveness"
    TABLE="Register" 
    
    table = dynamodb.Table(TABLE)

    response = table.delete_item(
        Key={
            'Name':LIVENESS_USER
        }
    )
    
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    assert 200 == str(status_code)
	
