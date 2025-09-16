from rest_framework.pagination import LimitOffsetPagination

PAGINATION_NUMBER_LIST = [20, 40, 80, 120, 200]
DEFAULT_PAGINATION_NUMBER = PAGINATION_NUMBER_LIST[0]

class StandardResultsSetLimitOffset(LimitOffsetPagination):
    default_limit = 20
    max_limit = 200
