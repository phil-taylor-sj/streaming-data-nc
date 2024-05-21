from moto import mock_aws
import pytest
import boto3
import os
from botocore.exceptions import ClientError
from src.connections_aws import connections_aws


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope='function')
def mock_credentials(aws_credentials):
    with mock_aws():
        yield boto3.client('secretsmanager', region_name='eu-west-2')


class TestGetGuardianCredentials:

    def test_returns_value_if_credential_found(self, mock_credentials):
        key_name = 'Guardian-Key'
        key_value = '1234567890'
        mock_credentials.create_secret(
            Name=key_name,
            SecretString=key_value
        )
        assert connections_aws.get_credentials(key_name) == key_value

    def test_raises_error_if_value_not_found(mock_credentials):
        with pytest.raises(ClientError) as excinfo:
            connections_aws.get_credentials('test-name')
        assert str(excinfo.value) == (
            'An error occurred (UnrecognizedClientException) '
            + 'when calling the GetSecretValue operation: '
            + 'The security token included in the request is invalid.'
        )
