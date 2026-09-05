from rest_framework.pagination import CursorPagination

class ProductCursorPagination(CursorPagination):
    page_size = 10
    # Must be an indexed field, like id or created_at
    ordering = '-created_at'  
