import requests


def get_guardian_content(
        api_key: str, search_term: str, date_from: str
) -> list[dict]:
    '''Retrieve article data from the Guardian content API.

    Submits a request to the Guardian API to get content based on the
    search and returns a list of 10 dictionaries containing the only
    required fields.

    Args:
        api_key:
            str containing the API key.
        search_term:
            str containing the search term.
        date_from:
            str containing the date from which to search.

    Returns:
        list of dictionaries containing the following fields:
            - webPublicationDate
            - webTitle
            - webUrl
        For example:

        [
            {
                "webPublicationDate": "2024-01-01T00:00:00Z",
                "webTitle": "Title 1",
                "webUrl": "https://www.theguardian.com/uk-news/..."
            },
            {
            "webPublicationDate": "2024-02-02T00:00:00Z",
            "webTitle": "Title 2",
            "webUrl": "https://www.theguardian.com/football/..."
            }
        ]
    '''
    base_url = 'https://content.guardianapis.com/search'
    params = {
        'api-key': api_key,
        'q': search_term,
        'from-date': date_from,
        'page': 1,
        'page-size': 10,
        'order-by': 'newest',
        'show-fields': 'webPublicationData,webTitle,webUrl'
    }
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()


def filter_response(
        response: dict,
        fields: list[str] = ['webPublicationDate', 'webTitle', 'webUrl']
) -> list[dict]:
    '''Filter guardian response json to keep only the required fields.

    Args:
        response:
            dict containing json response from the Guardian API.
        fields:
            list contiaining names of fields to be kept.

    Returns:
        list of dictionaries containing only the entries specified in the
        fields argument. If the response is empty, an empty list is returned.
    '''
    if not response:
        return []
    records = response['response']['results']
    return [{key: value for key, value in record.items()
            if key in fields} for record in records]
