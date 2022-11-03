from rest_framework import pagination

class BasicPagination(pagination.PageNumberPagination):
    page_size = 7
    page_size_query_param = 'count'
    max_page_size = 5
    page_query_param = 'p'