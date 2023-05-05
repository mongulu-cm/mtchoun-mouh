import boto3
import os 
 
class TestLivenessRmoveLivenessUser():

  
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
