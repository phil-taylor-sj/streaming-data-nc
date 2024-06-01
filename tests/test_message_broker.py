from moto import mock_aws
import boto3
import pytest
import os
import json
from src.message_broker import create_stream, add_records


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope='function')
def mock_broker(aws_credentials):
    with mock_aws():
        yield boto3.client('kinesis', region_name='eu-west-2')


class TestCreateStream:
    def test_creates_stream_if_not_exists(self, mock_broker):
        stream_name = 'test-stream'
        response = create_stream(mock_broker, stream_name)
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200

    def test_returns_none_if_stream_exists(self, mock_broker):
        stream_name = 'test-stream'
        create_stream(mock_broker, stream_name)
        response = create_stream(mock_broker, stream_name)
        assert response is None


class TestAddRecords:

    test_records = json.load(open(
            './tests/data/api_content_2/formatted_results.json')
            )['results']

    def test_adds_records_to_stream(self, mock_broker):
        stream_name = 'test-stream'
        create_stream(mock_broker, stream_name)
        add_records(mock_broker, stream_name, 'test-term', self.test_records)

        # Assert
        output = []
        response = mock_broker.describe_stream(StreamName=stream_name)
        for shard in response['StreamDescription']['Shards']:
            shard_id = shard['ShardId']
            shard_iterator_response = mock_broker.get_shard_iterator(
                StreamName=stream_name,
                ShardId=shard_id,
                ShardIteratorType='TRIM_HORIZON',
            )
            shard_iterator = shard_iterator_response['ShardIterator']
            record_response = mock_broker.get_records(
                ShardIterator=shard_iterator, Limit=15)
            for record in record_response['Records']:
                output.append(json.loads(record['Data'].decode('utf-8')))

        for i in range(len(output)):
            expect = self.test_records[i]
            for key in expect.keys():
                assert expect[key] == output[i][key]
