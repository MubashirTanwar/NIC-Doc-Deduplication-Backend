from api.models import AuthToken, Logs, Users
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
    """
    Middleware class for logging errors in the API.
    This middleware logs exceptions and responses with status codes between 400 and 599.
    It captures relevant information such as the timestamp, request path, request method,
    IP address, user agent, exception message, traceback, and response content (if applicable).
    Attributes:
        None
    Methods:
        process_exception(request, exception):
            Logs the exception details when an exception occurs during request processing.
            Returns None.
        process_response(request, response):
            Logs the response details when the response has a status code between 400 and 599.
            Returns the original response.
    Usage:
        Add this middleware class to the Django middleware stack to enable error logging.
    """
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
    Middleware class for handling bearer token authentication and API key validation.
    Args:
        get_response (callable): The next middleware in the chain.
    Attributes:
        get_response (callable): The next middleware in the chain.
    Methods:
        __call__(self, request): Handles the authentication and validation logic.
        authenticate_with_token(self, token, api_key): Authenticates the user with the provided token and API key.
        addLogInDB(self, request, user): Adds a log entry to the database.
    """
    """
    Handles the authentication and validation logic.
    Args:
        request (HttpRequest): The incoming request object.
    Returns:
        HttpResponse: The response object.
    """
    """
    Authenticates the user with the provided token and API key.
    Args:
        token (str): The bearer token.
        api_key (str): The API key.
    Returns:
        User: The authenticated user object if successful, None otherwise.
    """
    """
    Adds a log entry to the database.
    Args:
        request (HttpRequest): The incoming request object.
        user (User): The authenticated user object.
    Returns:
        Logs: The log entry object.
    """

    ...
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if "HTTP_AUTHORIZATION" in request.META:
                # you have 2 things to check here token and api key
                auth_header = request.META["HTTP_AUTHORIZATION"]
                if not auth_header:
                    return JsonResponse({"error": "Authorization header is missing.",
                                         'details': 'Please provide an authorization header.',
                                         'code': 400
                                         }, status=404)
                api_key = request.META.get("HTTP_KEY", "")
                if not api_key:
                    return JsonResponse({"error": "API key is missing.",
                                         'details': 'Please provide an API key.',
                                         'code': 400
                                         }, status=404)

                if auth_header.startswith("Bearer "):
                    token = auth_header[7:]  # Extract the token part
                    # if token is empty or invalid
                    if not token:
                        return JsonResponse({"error": "Token is missing.",
                                             'details': 'Please provide a token.',
                                             'code': 400
                                             }, status=400)
                    if len(token) != 40:
                        return JsonResponse({"error": "Invalid token.",
                                             'details': 'The token is invalid.',
                                             'code': 400
                                             }, status=401)

                    if len(api_key) != 40:
                        return JsonResponse({"error": "Invalid API key.",
                                             'details': 'The API key is invalid.',
                                             'code': 400
                                             }, status=401)
                    print("Token: ", token)
                    print("API Key; ", api_key)
                    user = self.authenticate_with_token(token, api_key)
                    if not user:
                        return JsonResponse({"error": "Could not authenticate user.",
                                             'details': 'The token is invalid or expired.',
                                             'code': 401
                                             }, status=401)

                    log = self.addLogInDB(request, user)
                    print("Log: ", log)
                    request.user = user
        except Exception as e:
            return JsonResponse({"error": "An error occurred.",
                                 'details': str(e),
                                 'code': 500
                                 }, status=500)
        response = self.get_response(request)
        return response

    def authenticate_with_token(self, token, api_key):
        try:
            print("Token: ", token)
            #  search for the token in the database
            auth_token = Users.objects.get(secret_key=token)
            print("Auth Token: ", auth_token)
            if not auth_token:
                return JsonResponse({"error": "Authentication failed.",
                                        'details': 'The token is invalid or expired.',
                                        'code': 401
                                    }, status=401)  
            
            # check if the api key is valid
            api_key = AuthToken.objects.get(key=api_key)
            if not api_key:
                return JsonResponse({"error": "Validation failed.",
                                        'details': 'The API key is invalid.',
                                        'code': 401
                                    }, status=403)
            
            print("autrhtoken: ", api_key)
            print("user: ", api_key.user)
            return api_key.user
        except AuthToken.DoesNotExist:
            return None

    def addLogInDB(self, request, user):
        log = Logs(user=user, action=request.path
                   , ip_address=request.META.get("REMOTE_ADDR", ""))
        log.save()
        return log
        