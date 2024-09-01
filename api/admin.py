from django.contrib import admin

# Register your models here.
from .models import PDFDocument, ExtractedLine, ExtractedText, AuthToken, Logs, Users

admin.site.register(PDFDocument)
admin.site.register(ExtractedLine)
admin.site.register(ExtractedText)
admin.site.register(AuthToken)
admin.site.register(Logs)
admin.site.register(Users)
