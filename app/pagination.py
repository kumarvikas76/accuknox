from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class SearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'results': data
        })