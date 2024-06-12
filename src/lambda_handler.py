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
    '''
    AWS Lambda handler to process Guardian API content and push results to Kinesis stream.

    Parameters:
    event (dict): Event data passed to the function, containing:
        - date_from (str): The start date for the Guardian content search, expected in 'YYYY-MM-DD' format.
        - search_term (str): The term to search for in the Guardian content.
        - stream_id (str): The ID of the Kinesis stream to which the results will be pushed.
    context (dict): AWS Lambda context object, providing runtime information to the handler.

    Function Workflow:
    1. Extracts 'date_from', 'search_term', and 'stream_id' from the event dictionary.
    2. Validates 'date_from' to ensure it is a correctly formatted date and prior to the current date.
    3. Validates 'search_term' and 'stream_id' to ensure they are non-empty and do not contain only whitespace.
    4. Establishes connections to AWS services.
    5. Retrieves the Guardian API key from AWS credentials.
    6. Fetches content from the Guardian API based on the search term and date.
    7. Filters the response to obtain relevant results.
    8. Checks if the Kinesis stream exists; if not, creates a new stream.
    9. Adds the filtered results to the Kinesis stream.
    10. Logs the number of records added to the stream.

    Exception Handling:
    - TypeError: Logs an error if an input parameter has an invalid type, extracting the parameter name from the error message.
    - ValueError: Logs specific error messages based on the nature of the value error, such as empty input, whitespace-only input, invalid date format, or invalid date value.

    Logs:
    - Logs the creation of a new Kinesis stream if applicable.
    - Logs the number of records added to the Kinesis stream.

    Raises:
    - TypeError: If the input parameters are of incorrect types.
    - ValueError: If the input parameters have invalid values.
    '''

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
    except ClientError as err:
        log_responses = {}
        match err.response['Error']['Code']:
            case 'ResourceNotFoundException':
                log_responses = {
                    'GetSecretValue': 'Failed to retrieve Guardian ' +
                    'API key from AWS Secrets Manager.',
                }
        for message in log_responses.keys():
            if re.search(rf'{message}', str(err)) is not None:
                logger.error(log_responses[message])