from rest_framework.response import Response
from rest_framework import status



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

    response_data = {
        'success': success,
        'details': details,
        'code': code,
    }
    
    if data is not None:
        response_data['data'] = data

    return Response(response_data, status=status_code)
