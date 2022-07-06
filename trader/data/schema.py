class SchemaError(Exception):

    def __init__(self, *args):
        super(SchemaError, self).__init__(*args)


OPEN_TIME = 'OPEN_TIME'
OPEN_PRICE = 'OPEN_PRICE'
HIGH_PRICE = 'HIGH_PRICE'
LOW_PRICE = 'LOW_PRICE'
CLOSE_PRICE = 'CLOSE_PRICE'
VOLUME = 'VOLUME'

SCHEMA_NAMES = (OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME)

NAME_TO_INDEX = {
    OPEN_TIME: 0,
    OPEN_PRICE: 1,
    HIGH_PRICE: 2,
    LOW_PRICE: 3,
    CLOSE_PRICE: 4,
    VOLUME: 5,
}


NAME_TO_SHORT_NAME = {
    OPEN_TIME: 't',
    OPEN_PRICE: 'o',
    HIGH_PRICE: 'h',
    LOW_PRICE: 'l',
    CLOSE_PRICE: 'c',
    VOLUME: 'v',
}

SHORT_NAME_TO_NAME = {
    't': OPEN_TIME,
    'o': OPEN_PRICE,
    'h': HIGH_PRICE,
    'l': LOW_PRICE,
    'c': CLOSE_PRICE,
    'v': VOLUME,
}
