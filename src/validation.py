from datetime import datetime


def check_date_is_valid(date: str) -> bool:
    '''
    Args:
        date: string value of date parameter to validate.

    Returns:
        True if no exception is thrown.
    '''
    date_from = datetime(1, 1, 1)
    if not isinstance(date, str):
        raise TypeError('date_from parameter must be of type string.')
    try:
        date_from = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError('date_from parameter must be formatted as %Y-%m-%d.')

    if date_from >= datetime.now():
        raise ValueError('date_from parameter must be before current date.')
    return True
