from api.models import AuthToken, Logs
from django.http import JsonResponse



import logging
import traceback
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler("error_logs.log"), logging.StreamHandler()]
)

class ErrorLoggingMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        error_message = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'path': request.path,
            'method': request.method,
            'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'exception': str(exception),
            'traceback': traceback.format_exc(),
        }
        logger.error(error_message)
        return None

    def process_response(self, request, response):
        if 400 <= response.status_code < 600:  # Catch both client and server errors
            error_message = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'path': request.path,
                'method': request.method,
                'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                'status_code': response.status_code,
                'response': response.content.decode('utf-8') if response.streaming is False else 'Streaming content',
            }
            logger.error(error_message)
        return response

class BearerTokenMiddleware:
    """
    Middleware class for handling bearer token authentication.
    Args:
        get_response (function): The function to get the response.
    Attributes:
        get_response (function): The function to get the response.
    Methods:
        __call__(self, request): Handles the authentication process and sets the user in the request object.
        authenticate_with_token(self, token): Authenticates the user with the provided token.
    """
    """
    Handles the authentication process and sets the user in the request object.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The HTTP response object.
    """
    ...
    """
    Authenticates the user with the provided token.
    Args:
        token (str): The bearer token.
    Returns:
        User: The authenticated user object if successful, None otherwise.
    """
    ...
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "HTTP_AUTHORIZATION" in request.META:
            auth_header = request.META["HTTP_AUTHORIZATION"]
            if not auth_header:
                return JsonResponse({"error": "Authorization header is missing."}, status=404)
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Extract the token part
                # if token is empty or invalid
                if not token:       
                    return JsonResponse({"error": "Token is missing."}, status=400)
                if len(token) != 40:
                    return JsonResponse({"error": "Invalid token."}, status=401)
                
                 
               
            

        response = self.get_response(request)
        return response


    def authenticate_with_token(self, token):
        try:
            print("Token: ", token) 
            #  search for the token in the database
            auth_token = AuthToken.objects.get(key=token)
            if not auth_token:
                return JsonResponse({"error": "Could not authenticate user."}, status=401)
            print("User: ", auth_token.user)
            return auth_token.user
        except AuthToken.DoesNotExist:
            return None

    def addLogInDB(self, request, user):
        log = Logs(user=user, action="Login", ip_address=request.META.get("REMOTE_ADDR", ""))
        log.save()
        return log
        