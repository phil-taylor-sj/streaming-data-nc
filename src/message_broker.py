import json


def create_stream(kinesis, stream_name: str):
    '''
    Creates a Kinesis stream.

    Args:
        stream_name: string specifying data stream to write records to
        e.g. guardian_content.

    Returns:
        dict containing the response from the create_stream method.
    '''
    try:
        response = kinesis.create_stream(
            StreamName=stream_name,
            ShardCount=151
        )
    except kinesis.exceptions.ResourceInUseException:
        return None
    return response


def add_records(
        kinesis, stream_name: str,
        search_term: str, records: list[dict]
        ):
    for record in records:
        record_bytes = json.dumps(record).encode('utf-8')
        kinesis.put_record(
            StreamName=stream_name,
            Data=record_bytes,
            PartitionKey=search_term
        )
