import re
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
        error_messages = []
        for key, value in details.items():
            if isinstance(value, list):
                error_messages.extend(value)
            else:
                error_messages.append(str(value))
        
        if error_messages:
            message = error_messages[0]
    
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
