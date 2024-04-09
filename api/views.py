from django.shortcuts import render
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import fitz
from .utils import extract_pages_from_pdf, process_image, hash_pdf, search_and_save
import pytesseract
from pdf2image import convert_from_path
from elasticsearch import Elasticsearch
import hashlib


pdfPath = ""

class ProcessPDF(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES['pdf']
        pdf_file_path = f'media/temp_images/{pdf_file.name}'
        with open(pdf_file_path, 'wb') as f:
            f.write(pdf_file.read())
        pdf_document = fitz.open(pdf_file_path)
        page_images = extract_pages_from_pdf(pdf_document)
        processed_images = []
        for page_num, page_image_path in enumerate(page_images):
            processed_image_path = process_image(page_image_path, 'media/output_images', page_num)
            processed_images.append(processed_image_path)
        return Response({'processed_images': processed_images})
class OCR(APIView):
            parser_classes = (MultiPartParser, FormParser)
    
            def post(self, request, *args, **kwargs):
                pdf_file = request.FILES['pdf']
                pdf_file_path = f'media/temp_images/{pdf_file.name}'
                pdfPath = pdf_file_path
                with open(pdf_file_path, 'wb') as f:
                    for chunk in pdf_file.chunks():
                        f.write(chunk)
                extracted_text = extract_text_from_pdf(pdf_file_path)
                return Response({'extracted_text': extracted_text})
                
def extract_text_from_pdf(pdf_path):
                    images = convert_from_path(pdf_path)
                    pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
                    text = ""
                    for i in range(len(images)):
                        text += pytesseract.image_to_string(images[i], lang='mar')
                    return text


class ES(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES['pdf']
        pdf_file_path = f'media/temp_images/{pdf_file.name}'

        es = Elasticsearch(
                [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}],
                http_auth=('elastic', '3aStr48Q0Eiv+Om0jw8k')  # replace 'elastic' and 'password' with your username and password
        )
        file_path, index = pdf_file_path, 'ocr'
        
        hashed_text = hash_pdf(file_path)

            #search and Save the hashed text in Elasticsearch
        result, location = search_and_save(es, index, hashed_text, file_path)
        if result is True:
                return Response([{'message': 'Document already exists', 'location': location, 'status': 200}])
        elif result['_shards']['successful'] == 1 and result['result'] == 'created':
                return Response([{'message': 'Document saved successfully', 'location': location, 'status': 201}])
        else:
                return Response([{'message': 'Failed to save document', 'location': location, 'status': 500}])
        
                


            