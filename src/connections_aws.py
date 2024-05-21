import boto3


class connections_aws:

    _current_region = 'eu-west-2'

    @classmethod
    def get_credentials(
            cls, secret_id: str) -> str:
        conn = boto3.client('secretsmanager', region_name=cls._current_region)
        response = conn.get_secret_value(SecretId=secret_id)
        return response['SecretString']
