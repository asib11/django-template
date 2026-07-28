import re
from rest_framework.response import Response
from rest_framework import status

class CustomResponseListMixin:
    success_details = "Data fetched successfully."
    success_code = "LIST_SUCCESS"

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return response(
            details=self.success_details,
            code=self.success_code,
            status_code=status.HTTP_200_OK,
            data=data,
        )

def response(
        details: str,
        code: str='SUCCESS',
        success: bool=True,
        status_code=status.HTTP_200_OK,
        data=None,
    ):

    response_data = {
        'success': success,
        'details': details,
        'code': code,
        'status_code': status_code,
    }
    
    if data is not None:
        response_data['data'] = data

    return Response(response_data, status=status_code)



def error_response(
        details: str,
        code: str='ERROR',
        success: bool=False,
        status_code=status.HTTP_400_BAD_REQUEST,
        data=None,
    ):
    message = details

    if isinstance(details, dict):
        formatted_errors = {}
        for key, value in details.items():
            if isinstance(value, list):
                formatted_errors[key] = ' '.join(str(v) for v in value)
            else:
                formatted_errors[key] = str(value)

        message = formatted_errors
        
    elif isinstance(details, list):
        message = ' '.join(str(v) for v in details)

    elif isinstance(details, str):
        match = re.search(r"string='([^']+)'", details)
        if match:
            message = match.group(1)

    response_data = {
        'success': success,
        'details': message,
        'code': code,
        'status_code': status_code,
    }

    if data is not None:
        response_data['data'] = data

    return Response(response_data, status=status_code)
