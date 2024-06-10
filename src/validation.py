from datetime import datetime


def check_date_is_valid(date: str) -> bool:
    '''
    Validate that a given date string meets specific criteria.

    This function checks whether the provided `date` parameter is a string
    formatted as `YYYY-MM-DD` and represents a date that is before the current date.
    If the `date` does not meet these criteria, an appropriate exception is raised.

    Parameters:
        date (str): The date string to be validated, formatted as `YYYY-MM-DD`.

    Returns:
        bool: True if the `date` is valid.

    Raises:
        TypeError: If `date` is not of type `str`.
        ValueError: If `date` is not formatted as `YYYY-MM-DD` or if it is not before the current date.
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
    '''
    Validate that a given ID string meets specific criteria.

    This function checks whether the provided `id` parameter is a non-empty
    string that does not consist solely of whitespace characters. If the `id`
    does not meet these criteria, an appropriate exception is raised.

    Parameters:
        id (str): The string to be validated.
        param_name (str): The name of the parameter, used in error messages for clarity.

    Returns:
        bool: True if the `id` is valid.

    Raises:
        TypeError: If `id` is not of type `str`.
        ValueError: If `id` is an empty string or contains only whitespace.
    '''
    if not isinstance(id, str):
        raise TypeError(f'Parameter ({param_name}) must be of type string.')
    if len(id) == 0:
        raise ValueError(f'Parameter ({param_name}) cannot be '
                         'an empty string.')
    if len(id.strip()) == 0:
        raise ValueError(f'Parameter ({param_name}) cannot contain ' +
                         'only whitespace.')
    return True
