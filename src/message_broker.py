import json
import time

def create_stream(kinesis, stream_name: str) -> dict:
    '''
    Creates a new Kinesis stream if specified stream does not exist.

    This function attemps to create a new Kinesis stream within the boto3
    client. If the create_stream operation fails, i.e. a stream with the 
    provided name already exists, then the function returns None. If there
    operation is successful, the function will increase the retention period
    to three days. This operation will fail unless the stream creation has
    been compelted. Hence, there latter operation is looped until successful. 

    Args:
        stream_name: string specifying data stream to write records to
        e.g. guardian_content.

    Returns:
        dict containing the response from the create_stream method.
    '''
    try:
        response = kinesis.create_stream(
            StreamName=stream_name,
            ShardCount=15
        )
    except kinesis.exceptions.ResourceInUseException:
        return None
    
    is_unchanged = True
    while (is_unchanged):
        try:
            kinesis.increase_stream_retention_period(
                StreamName=stream_name,
                RetentionPeriodHours=72
            )
            is_unchanged = False
        except kinesis.exceptions.ResourceNotFoundException:
            time.sleep(0.1)
        except kinesis.exceptions.ResourceInUseException:
            time.sleep(0.1)
    return response

def add_records(
        kinesis, stream_name: str,
        search_term: str, records: list[dict]
        ) -> str:
    '''
    Adds records to a Kinesis stream.

    This function adds records to a Kinesis stream using the boto3 client.

    Args:
        stream_name: string specifying data stream to write records to
        e.g. guardian_content.
        search_term: string specifying the search term used to filter records.
        records: list of dictionaries containing the filtered results.
    '''

    shard_id = 'None'
    for record in records:
        record_bytes = json.dumps(record).encode('utf-8')
        response = kinesis.put_record(
            StreamName=stream_name,
            Data=record_bytes,
            PartitionKey=search_term
        )
        shard_id = response['ShardId']
    return shard_id
