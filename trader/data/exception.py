class SchemaError(Exception):

    def __init__(self, *args):
        super(SchemaError, self).__init__(*args)
