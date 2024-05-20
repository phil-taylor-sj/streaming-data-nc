import requests


def get_guardian_content(
        api_key: str, search_term: str, date_from: str):
    # Search for content
    # Returns a list of content
    base_url = 'https://content.guardianapis.com/search'
    params = {
        'api-key': api_key,
        'q': search_term,
        'from-date': date_from,
        'page': 1,
        'page-size': 10,
        'show-fields': 'webPublicationData,webTitle,webUrl'
    }
    response = requests.get(base_url, params=params)
    return response.json


def filter_response(response: dict):
    if not response:
        return []
    records = response['response']['results']
    return [filter_record(record) for record in records]


def filter_record(record: dict):
    records_to_keep = ['webPublicationDate', 'webTitle', 'webUrl']
    return {key: value for key, value in record.items()
            if key in records_to_keep}
