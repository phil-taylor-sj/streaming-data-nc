import boto3
import logging
import re
from botocore.exceptions import ClientError
from src.message_broker import create_stream, add_records
from src.guardian_api import get_guardian_content
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
    except TypeError as err:
        param_name = re.findall(r'\(\w+\)', str(err))[0]
        logger.error(f'Invalid input parameter type {param_name}.')
    except ValueError as err:
        if re.search(
            r'Parameter \(\w+\) cannot be an empty string\.', str(err)
                ) is not None:
            param_name = re.findall(r'\(\w+\)', str(err))[0]
            logger.error(f'Empty input parameter {param_name}.')
        if re.search(
            r'Parameter \(\w+\) cannot contain only whitespace\.', str(err)
                ) is not None:
            param_name = re.findall(r'\(\w+\)', str(err))[0]
            logger.error(f'Invalid input parameter {param_name}.')
