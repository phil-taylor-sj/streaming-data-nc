import boto3


class connections_aws:

    _current_region = 'eu-west-2'

    @classmethod
    def get_credentials(
            cls, secret_id: str) -> str:
        '''
        Args:
            secret_id:
                str containing the secret id.

        Returns:
            str containing the secret value.

        Raises:
            ClientError: If the secret_id is not found.
            ParamValidationError: If the secret_id is not a string.
        '''
        conn = boto3.client('secretsmanager', region_name=cls._current_region)
        response = conn.get_secret_value(SecretId=secret_id)
        return response['SecretString']

    @classmethod
    def get_message_broker(cls):
        '''
        Returns:
            Kinesis client object.
        '''
        return boto3.client('kinesis', region_name=cls._current_region)
