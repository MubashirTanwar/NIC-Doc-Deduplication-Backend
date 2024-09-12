from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
import fitz
from .utils import extract_pages_from_pdf, process_image, hash_pdf, search_and_save
import pytesseract
from pdf2image import convert_from_path
from elasticsearch import Elasticsearch
from .models import Users, AuthToken
import string
import random
from datetime import datetime
from django.views import View
from django.utils import timezone
from django.contrib import messages
from django.conf import settings



pdfPath = ""

class ProcessPDF(APIView):
    """
    API view for processing a PDF file.
    This view accepts a PDF file and processes it by extracting pages and processing each page image.
    Methods:
        post(request, *args, **kwargs): Processes the PDF file and returns a response with the processed images.
    Attributes:
        parser_classes: A tuple of parser classes used for parsing the request data.
    """
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permission checks
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            pdf_file = request.FILES['pdf']
            if pdf_file is None:
                return JsonResponse({'error': 'No file uploaded.',
                                     'details': 'Please upload a PDF file.',
                                     'code': 400
                                     }, status=400)
            
            if pdf_file.name.endswith('.pdf') is False:
                return JsonResponse({'error': 'Invalid file format.',
                                     'details': 'The uploaded file is not a PDF file, please upload a PDF file.',
                                        'code': 400
                            
                                     }, status=400)
            # Check all edge cases: file size, mime type, secret key, password locked
            if pdf_file.size > 10000000:
                return JsonResponse({'error': 'File size too large.',
                                        'details': 'The uploaded file is too large, please upload a file less than 10MB.',
                                        'code': 400
                                     }, status=400)  
            if pdf_file.content_type != 'application/pdf':
                return JsonResponse({'error': 'Invalid file format.',
                                    'details': 'The uploaded file is not a PDF file, please upload a PDF file.',
                                    'code': 400
                                     }, status=400)
            pdf_file_path = f'media/temp_images/{pdf_file.name}'
            with open(pdf_file_path, 'wb') as f:
                try:
                    f.write(pdf_file.read())
                except Exception as e:
                    return JsonResponse({'error': 'An error occurred while processing the PDF file.',
                                        'details': "The uploaded PDF file was either corrupted or not a valid PDF file.",   
                                        'code': 500
                                        }, status=500)
            pdf_document = fitz.open(pdf_file_path)
            page_images = extract_pages_from_pdf(pdf_document)
            processed_images = []
            for page_num, page_image_path in enumerate(page_images):
                processed_image_path = process_image(page_image_path, 'media/output_images', page_num)
                processed_images.append(processed_image_path)
            return Response({'processed_images': processed_images}, status=200)
        except Exception as e:
            return JsonResponse({'error': "An error occurred while processing the PDF file.",
                                    'details': str(e),
                                    'code': 500
                                 }, status=500)
        

class OCR(APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permission checks
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            pdf_file = request.FILES['pdf']
            if pdf_file.name.endswith('.pdf') is False:
                return JsonResponse({'error': 'Invalid file format.',
                                     'details': 'The uploaded file is not a PDF file, please upload a PDF file.',
                                     'code': 400
                                     }, status=400)
            if pdf_file.size > 10000000:
                return JsonResponse({'error': 'File size too large.',
                                     'details': 'The uploaded file is too large, please upload a file less than 10MB.',
                                     'code': 400
                                     }, status=400)
            if pdf_file.content_type != 'application/pdf':
                return JsonResponse({'error': 'Invalid file format.',
                                     'details': 'The uploaded file is not a PDF file, please upload a PDF file.',
                                     'code': 400
                                     }, status=400)
            
            pdf_file_path = f'media/temp_images/{pdf_file.name}'
            pdfPath = pdf_file_path
            with open(pdf_file_path, 'wb') as f:
                for chunk in pdf_file.chunks():
                    f.write(chunk)
            extracted_text = extract_text_from_pdf(pdf_file_path)
            return Response({'extracted_text': extracted_text}, status=200)
        except Exception as e:
            return JsonResponse({'error': "An error occurred while extracting text from the PDF file.",
                                 'details': str(e),
                                 'code': 500
                                 }, status=500)
                
def extract_text_from_pdf(pdf_path):
                    images = convert_from_path(pdf_path)
                    pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
                    text = ""
                    for i in range(len(images)):
                        text += pytesseract.image_to_string(images[i], lang='mar')
                    return text



class ES(APIView):
    """
    Endpoint for uploading a PDF file and saving its hashed text in Elasticsearch.
    Parameters:
        request (HttpRequest): The HTTP request object.
        args (tuple): Additional positional arguments.
        kwargs (dict): Additional keyword arguments.
    Returns:
        Response: The HTTP response containing a JSON object with the following keys:
            - message (str): A message indicating the result of the operation.
            - location (str): The location of the saved document.
            - status (int): The HTTP status code.
    Example:
        >>> response = ES().post(request)
    """
    authentication_classes = []  # Disable authentication
    permission_classes = []  # Disable permission checks
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        try:
            pdf_file = request.FILES['pdf']

            if pdf_file.name.endswith('.pdf') is False:
                    return JsonResponse({'error': 'Invalid file format.',
                                            'details': 'The uploaded file is not a PDF file, please upload a PDF file.',
                                            'code': 400
                                            }, status=400)
            if pdf_file.size > 10000000:
                    return JsonResponse({'error': 'File size too large.',
                                            'details': 'The uploaded file is too large, please upload a file less than 10MB.',
                                            'code': 400
                                            }, status=400)  
            if pdf_file.content_type != 'application/pdf':
                    return JsonResponse({'error': 'Invalid file format.',
                                            'details': 'The uploaded file is not a PDF file, please upload a PDF file.',
                                            'code': 400
                                            }, status=400)     

            pdf_file_path = f'media/temp_images/{pdf_file.name}'

            
            try:
                es = Elasticsearch(
                        [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                        http_auth=('elastic', '3aStr48Q0Eiv+Om0jw8k')  # replace 'elastic' and 'password' with your username and password
                )
            except Exception as e:
                return JsonResponse({'error': "An error occurred.",
                                    'details': "An error occurred while connecting to Elasticsearch.",
                                    'code': 500
                                    }, status=500)
            if not es.ping():
                    return Response([{'message': 'Failed to connect to Elasticsearch', 'status': 500}]) 
            
            file_path, index = pdf_file_path, 'ocr'
            
            hashed_text = hash_pdf(file_path)
            if hashed_text is None:
                    return Response([{'message': 'Failed to hash text', 'status': 500}])    
            
                #search and Save the hashed text in Elasticsearch
            result, location = search_and_save(es, index, hashed_text, file_path)
            if result is True:
                    return Response([{'message': 'Document already exists', 'location': location, 'status': 200}])
            elif result['_shards']['successful'] == 1 and result['result'] == 'created':
                    return Response([{'message': 'Document saved successfully', 'location': location, 'status': 201}])
            else:
                    return Response([{'message': 'Failed to save document', 'location': location, 'status': 500}])
        
        except Exception as e:
            return JsonResponse({'error': "An error occurred while saving the document in Elasticsearch.",
                                 'details': str(e),
                                 'code': 500
                                 }, status=500)
        
                    

# front end template for creating user
# Helper function to generate a random alphanumeric secret key
def generate_secret_key(length=40):
    """Generate a random alphanumeric secret key."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

class CreateUserView(View):
    def get(self, request):
        """Render the form for creating a new user."""
        return render(request, 'create_user.html')
    
    def post(self, request):
        """Handle the form submission to create a new user."""
        username = request.POST.get('username')
        organization = request.POST.get('organization')
        email = request.POST.get('email')
        
        # Validate the input
        if not username or not organization or not email:
            messages.error(request, "All fields are required.")
            return redirect('create_user')
        
        # Generate the secret key
        secret_key = generate_secret_key()
        
        # Save the user to the database using Django ORM
        try:
            user = Users.objects.create(
                username=username,
                organization=organization,
                email=email,
                secret_key=secret_key,
                created=timezone.now()
            )
            return render(request, 'create_user.html', {
                "username": username,
                "organization": organization,
                "email": email,
                "secret_key": secret_key
            })
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect('create_user')


def generate_api_key(length=40):
        """Generate a random alphanumeric API key."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


class CreateApiKey(View):
     def get(self, request):
          return render(request, 'api_key_form.html')
     
     def post(self, request):
        secret_key = request.POST.get('token')

        user = Users.objects.filter(secret_key=secret_key).first()
        if not user:
                return JsonResponse({
                    "error": "User with the provided token does not exist.",
                    "code": 400
                }, status=400)
        
        apikey = generate_api_key()

        AuthToken.objects.create(
            key=apikey,
            user=user,
            created=datetime.now()
        )

        return render(request, 'api_key_form.html', {
             "apikey" : apikey
        })
            




# def generate_api_key(length=40):
#     """Generate a random alphanumeric API key."""
#     characters = string.ascii_letters + string.digits
#     return ''.join(random.choice(characters) for _ in range(length))

# def connect_db():
#     """Connect to the PostgreSQL database."""
#     conn = psycopg2.connect(
#         dbname= os.getenv("NAME"),
#         user= os.getenv("USER"),
#         password= os.getenv("PASSWORD"),
#         host= os.getenv("HOST"),
#         port= os.getenv("PORT")
#     )
#     return conn

# def user_exists(conn, token):
#     """Check if a user exists in the database with the provided token."""
#     with conn.cursor() as cursor:
#         query = sql.SQL("SELECT id FROM api_users WHERE secret_key = %s")
#         cursor.execute(query, [token])
#         result = cursor.fetchone()
#         return result[0] if result else None

# def save_auth_token(conn, api_key, user_id):
#     """Save the API key in the AuthToken table."""
#     with conn.cursor() as cursor:
#         insert_query = sql.SQL("""
#             INSERT INTO api_authtoken (key, user_id, created)
#             VALUES (%s, %s, %s)
#         """)
#         cursor.execute(insert_query, (api_key, user_id, datetime.now()))
#         conn.commit()

# def create_auth_token():
#     """Check user via token, generate API key, and save it."""
#     # Prompt user for token
#     token = input("Enter your token: ")
    
#     # Connect to the PostgreSQL database
#     conn = connect_db()
    
#     # Check if user exists
#     user_id = user_exists(conn, token)
#     if not user_id:
#         print("User with the provided token does not exist.")
#         conn.close()
#         return
    
#     # Generate a 40-character alphanumeric API key
#     api_key = generate_api_key()
    
#     # Save the API key in the database
#     save_auth_token(conn, api_key, user_id)
    
#     # Close the database connection
#     conn.close()
    
#     print(f"API Key generated and saved successfully: {api_key}")

# if __name__ == "__main__":
#     create_auth_token()
