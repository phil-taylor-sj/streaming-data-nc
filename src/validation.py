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
        raise TypeError('Parameter (date_from) must be of type string.')
    try:
        date_from = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError(
            'Parameter (date_from) must be formatted as %Y-%m-%d.'
            )

    if date_from >= datetime.now():
        raise ValueError(
            'Parameter (date_from) must be before current date.'
            )
    return True


def check_id_string_is_valid(id: str, param_name: str) -> bool:
    if not isinstance(id, str):
        raise TypeError(f'Parameter ({param_name}) must be of type string.')
    if len(id) == 0:
        raise ValueError(f'Parameter ({param_name}) cannot be '
                         'an empty string.')
    if len(id.strip()) == 0:
        raise ValueError(f'Parameter ({param_name}) cannot contain ' +
                         'only whitespace.')
    return True
