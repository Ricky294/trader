from enum import Enum


class NameFormat(Enum):
    LOWER_CASE = 'lower_case'
    LOWER_CASE_WITH_UNDERSCORES = 'lower_case_with_underscores'
    UPPER_CASE = 'upper_case'
    UPPER_CASE_WITH_UNDERSCORES = 'upper_case_with_underscores'
    CAMEL_CASE = 'camel_case'
    LOWER_CAMEL_CASE = 'lower_camel_case'
