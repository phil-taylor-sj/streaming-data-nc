import boto3
import logging
import re
from botocore.exceptions import ClientError
from src.message_broker import create_stream, add_records
from src.guardian_api import get_guardian_content, filter_response
from src.validation import check_date_is_valid, check_id_string_is_valid
from src.connections_aws import connections_aws

logger = logging.getLogger("GuardianLogger")
logger.setLevel(logging.INFO)


def lambda_handler(event: dict, context: dict):
    date_from = event.get('date_from')
    search_term = event.get('search_term')
    stream_id = event.get('stream_id')

    try:
        check_date_is_valid(date_from)
        check_id_string_is_valid(search_term, 'search_term')
        check_id_string_is_valid(stream_id, 'stream_id')
        connections = connections_aws()
        api_key = connections.get_credentials('Guardian-Key')
        response = get_guardian_content(api_key, search_term, date_from)
        results = filter_response(response)
        kinesis = connections.get_message_broker()
        if (create_stream(kinesis, stream_id) is not None):
            logger.info(f'New stream created: {stream_id}.')
        add_records(kinesis, stream_id, search_term, results)
        logger.info(f'{len(results)} records added to stream: {stream_id}.')
    except TypeError as err:
        param_name = re.findall(r'\(\w+\)', str(err))[0]
        logger.error(f'Invalid input parameter type {param_name}.')
    except ValueError as err:
        log_responses = {
            'cannot be an empty string': 'Empty input parameter',
            'cannot contain only whitespace': 'Invalid input parameter',
            'must be formatted as': 'Invalid date format',
            'must be before current date': 'Invalid date value'
        }
        for message in log_responses.keys():
            if re.search(
                rf'Parameter \(\w+\) {message}', str(err)
            ) is not None:
                param_name = re.findall(r'\(\w+\)', str(err))[0]
                logger.error(f'{log_responses[message]} {param_name}.')
