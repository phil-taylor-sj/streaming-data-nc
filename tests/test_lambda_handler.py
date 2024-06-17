import pytest
import logging
import os
from dotenv import load_dotenv
import boto3
from moto import mock_aws
from unittest.mock import patch
import json
import responses
from src.lambda_handler import lambda_handler

load_dotenv()

logger = logging.getLogger('TestLogger')
logger.setLevel(logging.INFO)
logger.propagate = True


@pytest.fixture(scope='function')
def aws_credentials():
    '''Mocked AWS Credentials for moto.'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'


@pytest.fixture(scope='function')
def mock_secret(aws_credentials):
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

    @pytest.mark.parametrize('param', [
        '2022-DD01-01', '2024-01-32', '2022-01-01T00:00:00',
    ])
    def test_logs_error_for_invalid_date_format(self, caplog, param):
        '''
        Ensure proper error logging for invalid date formats in 'date_from'.

        This test checks that the appropriate error messages are logged when
        the 'date_from' parameter in the event dictionary contains various
        invalid date formats, ensuring robust input validation and error
        handling.

        Args:
            param (str): A date string in an invalid format to test the
            error handling.

        Expected Log Messages:
            'Invalid date format (date_from).''
        '''
        event = {
            'date_from': param,
            'search_term': 'test_term',
            'stream_id': 'test_stream'
        }
        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = 'Invalid date format (date_from).'
            assert expected in caplog.text

    @pytest.mark.parametrize('param', ['2025-01-01', '2022-00-01'])
    def test_logs_error_for_invalid_date_value(self, caplog, param):
        '''
        Verify that incorrect date values are logged appropriately.

        This test checks that the appropriate error messages are logged when
        the 'date_from' parameter contains dates that are logically
        incorrect, such as a non-existent date or a future date that
        should not be valid in context.

        Args:
            param (str): A date string with a value issue (e.g., future date
                or non-existent date).

        Expected Log Messages:
            'Invalid date value (date_from).'
        '''
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
        '''
        Test error handling for non-string input parameters.

        This test checks that the appropriate error messages are logged when
        parameters expected to be of string type are provided as integers,
        ensuring type checking is enforced correctly.

        Args:
            param (str): The parameter to be tested with an integer input.

        Expected Log Messages:
            'Invalid input parameter type (date_from).'
            'Invalid input parameter type (search_term).'
            'Invalid input parameter type (stream_id).'
        '''
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
        '''
        Ensure errors are logged for empty or whitespace-only 'search_term'.

        This test checks that the appropriate error messages are logged when
        'search_term' is empty or contains only whitespace, which are
        considered invalid inputs.

        Scenarios:
            1. 'search_term' is an empty string.
            2. 'search_term' contains only spaces.

        Expected Log Messages:
            'Empty input parameter (search_term).'
            'Invalid input parameter (search_term).'
        '''
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
        '''
        Validate error logging for an empty or whitespace-only 'stream_id'.

        This test checks that the appropriate error messages are logged when
        'stream_id' is either completely empty or filled only with whitespace
        characters, which are considered invalid inputs.

        Scenarios:
            1. 'stream_id' is an empty string.
            2. 'stream_id' contains only spaces.

        Expected Log Messages:
            'Empty input parameter (stream_id).'
            'Invalid input parameter (stream_id).'
        '''
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


class TestDataProcessing:

    _test_event = {
        'date_from': '2022-01-01',
        'search_term': 'test_term',
        'stream_id': 'test_stream'
    }

    def _read_broker(kinesis, stream_name):
        '''
        Compile all records from shards in a Kinesis stream.

        This internal method describes the process of fetching records from
        a specified Kinesis stream by iterating through all shards and
        reading the data.

        Args:
            kinesis (boto3.client): The Kinesis client used to interact
                with AWS Kinesis.
            stream_name (str): The name of the Kinesis stream from which
                records are read.

        Returns:
            list: A list of data records extracted from the stream.
        '''
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
            mock_broker, caplog):
        '''
        Test that records are correctly uploaded to a Kinesis stream.

        This test verifies that response data retirevied from the Guardian
        API is properly formatted and uploaded to the specified Kinesis
        stream, checking that the final output matches expected data.

        Mocks:
            - Guardian API key retrieval.
            - Guardian content retrieval.
            - AWS Kinesis client.

        Asserts:
            - Correct number of records are uploaded.
            - Data integrity of uploaded records is maintained.
        '''
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
        with caplog.at_level(logging.INFO):
            lambda_handler(event, None)
            expected = f'10 records added to stream: {stream_name}'
            assert expected in caplog.text

        output = self.__class__._read_broker(mock_broker, stream_name)
        assert len(output) == 10
        for i in range(len(test_records)):
            expect = test_records[i]
            assert output[i]['keyword'] == 'test_term'
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
        '''
        Ensure that an absence of records does not raise errors.

        This test checks that the lambda_handler function handles an empty
        result set without raising errors, confirming that no records are
        uploaded to the stream and appropriate messages are logged.

        Mocks:
            - Content retrieval returning no results.
            - Guardian API key retrieval.
            - AWS Kinesis client.

        Asserts:
            - Log message indicates zero records added.
            - No records are found in the stream.
        '''
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
            expected = f'0 records added to stream: {stream_name}'
            assert expected in caplog.text
        output = self.__class__._read_broker(mock_broker, stream_name)
        assert output == []


class TestErrorLogging:

    _test_event = {
        'date_from': '2022-01-01',
        'search_term': 'test_term',
        'stream_id': 'test_stream'
    }

    def test_logs_error_if_credentials_not_found(
            self, mock_secret, caplog):
        '''
        Verify error logging when AWS credentials are not retrieved.

       This test checks that the appropriate error messages are logged
       when the Guardian API key is not found in the AWS Secrets Manager.

        Mocks:
            - AWS secrets manager: parameter retrieval failure.

        Asserts:
            - Appropriate error message is logged.
        '''
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
        '''
        Test handling of HTTP errors from the Guardian API.

        This test checks that the appropriate error messages are logged
        when a GET request to the Guardian API is unsuccessful.

        Mocks:
            - Simulated HTTP error response from the Guardian API.
            - AWS credentials.

        Asserts:
            - Specific HTTP error message is logged.
        '''
        responses.add(responses.GET,
                      'https://content.guardianapis.com/search',
                      json={'error': 'Unauthorized'},
                      status=401)
        with caplog.at_level(logging.INFO):
            lambda_handler(self._test_event, None)
            expected = 'Guardian API request failed with status code 401.'
            assert expected in caplog.text
