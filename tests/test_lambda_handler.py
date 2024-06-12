import pytest
import logging
import os
from src.lambda_handler import lambda_handler
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from moto import mock_aws
from unittest.mock import patch
import json
import responses

load_dotenv()

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
logger.propagate = True


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


@pytest.fixture(scope='function')
def mock_broker(aws_credentials):
    with mock_aws():
        yield boto3.client('kinesis', region_name='eu-west-2')


def patch_get_credentials():
    return patch('src.lambda_handler.connections.get_credentials',
                 return_value='1234567890')


class TestInputValidation:

    def test_logs_error_for_invalid_date_format(self, caplog):
        event = {
            'date_from': '2022-DD01-01',
            'search_term': 'test_term',
            'stream_id': 'test_stream'
        }
        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = 'Invalid date format (date_from).'
            assert expected in caplog.text

    def test_logs_error_for_invalid_date_value(self, caplog):
        event = {
            'date_from': '2025-01-01',
            'search_term': 'test_term',
            'stream_id': 'test_stream'
        }
        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = 'Invalid date value (date_from).'
            assert expected in caplog.text

    @pytest.mark.parametrize(
        'param', ['date_from', 'search_term', 'stream_id']
    )
    def test_logs_error_for_non_string_input_parameter(self, caplog, param):
        event = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': 'test_stream'
        }
        event[param] = 123
        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = f'Invalid input parameter type ({param}).'
            assert expected in caplog.text

    def test_logs_error_for_empty_search_term(self, caplog):
        event_1 = {
            'date_from': '2022-01-01',
            'search_term': '',
            'stream_id': 'test_stream'
        }
        event_2 = {
            'date_from': '2022-01-01',
            'search_term': '   ',
            'stream_id': 'test_stream'
        }
        with caplog.at_level(logging.INFO):
            lambda_handler(event_1, None)
            expected = "Empty input parameter (search_term)."
            assert expected in caplog.text
        with caplog.at_level(logging.INFO):
            lambda_handler(event_2, None)
            expected = "Invalid input parameter (search_term)."
            assert expected in caplog.text

    def test_logs_error_for_empty_stream_id(self, caplog):
        event_1 = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': ''
        }
        event_2 = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': '    '
        }
        with caplog.at_level(logging.INFO):
            lambda_handler(event_1, None)
            expected = 'Empty input parameter (stream_id).'
            assert expected in caplog.text
        with caplog.at_level(logging.INFO):
            lambda_handler(event_2, None)
            expected = 'Invalid input parameter (stream_id).'
            assert expected in caplog.text


class TestNewStreamCreation:

    _test_event = {
        'date_from': '2022-01-01',
        'search_term': 'test_term',
        'stream_id': 'test_stream'
    }

    def _read_broker(kinesis, stream_name):
        output = []
        response = kinesis.describe_stream(StreamName=stream_name)
        for shard in response['StreamDescription']['Shards']:
            shard_id = shard['ShardId']
            shard_iterator_response = kinesis.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard_id,
                ShardIteratorType='TRIM_HORIZON',
            )
            shard_iterator = shard_iterator_response['ShardIterator']
            record_response = kinesis.get_records(
                ShardIterator=shard_iterator, Limit=15)
            for record in record_response['Records']:
                output.append(json.loads(record['Data'].decode('utf-8')))
        return output

    @patch('src.lambda_handler.connections_aws.get_message_broker')
    @patch('src.lambda_handler.get_guardian_content')
    @patch('src.lambda_handler.connections_aws.get_credentials',
           return_value='1234567890')
    def test_records_uploaded_to_broker(
            self,
            mock_credentials,
            mock_content,
            mock_kinesis,
            mock_broker):
        test_response = json.load(open(
            './tests/data/api_content_2/raw_response.json'))
        test_records = json.load(open(
            './tests/data/api_content_2/formatted_results.json')
        )['results']
        mock_content.return_value = test_response
        mock_kinesis.return_value = mock_broker

        stream_name = 'test_stream'
        event = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': stream_name
        }
        lambda_handler(event, None)

        output = self.__class__._read_broker(mock_broker, stream_name)
        assert len(output) == 10
        for i in range(len(test_records)):
            expect = test_records[i]
            for key in expect.keys():
                assert output[i][key] == expect[key]

    @patch('src.lambda_handler.connections_aws.get_message_broker')
    @patch('src.lambda_handler.get_guardian_content')
    @patch('src.lambda_handler.connections_aws.get_credentials',
           return_value='1234567890')
    def test_empty_results_doesnt_raise_error(
            self,
            mock_credentials,
            mock_content,
            mock_kinesis,
            mock_broker,
            caplog):
        test_response = json.load(open(
            './tests/data/api_content_2/raw_response.json'))
        test_response['response']['results'] = []
        mock_content.return_value = test_response
        mock_kinesis.return_value = mock_broker
        stream_name = 'test_stream'
        event = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': stream_name
        }

        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = f'0 records added to stream: {stream_name}.'
            assert expected in caplog.text
        output = self.__class__._read_broker(mock_broker, stream_name)
        assert output == []

    def test_logs_error_if_credentials_not_found(
            self, mock_credentials, caplog):
        stream_name = 'test_stream'
        event = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': stream_name
        }
        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = ('Failed to retrieve Guardian API key ' +
                        'from AWS Secrets Manager.')
            assert expected in caplog.text

    @responses.activate
    @patch('src.lambda_handler.connections_aws.get_credentials',
           return_value='1234567890')
    def test_guardian_raises_http_error(
            self, mock_credentials, caplog):
        responses.add(responses.GET,
                      'https://content.guardianapis.com/search',
                      json={'error': 'Unauthorized'},
                      status=401)
        with caplog.at_level(logging.INFO):
            lambda_handler(self._test_event, None)
            expected = 'Guardian API request failed with status code 401.'
            assert expected in caplog.text
