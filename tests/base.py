def length_error(_min, _max):
    """
    Return a Marshmallow length error according to the min and max values

    param: :_min: the minimum length.
    param: :_max: the maximum length.
    """
    return f'Length must be between {_min} and {_max}.'
