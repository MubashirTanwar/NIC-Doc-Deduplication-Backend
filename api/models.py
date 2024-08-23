from django.db import models

class PDFDocument(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='pdf_files/')

class ExtractedLine(models.Model):
    pdf_document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='output_images/')
    text = models.TextField(null=True, blank=True)

class ExtractedText(models.Model):
    pdf_document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE)
    text = models.TextField()

class AuthToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.CharField(max_length=255)                                         # TODO: This should be a foreign key to the User model
    created = models.DateTimeField(auto_now_add=True)

class Logs(models.Model):
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)   
    created = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f"{self.user} - {self.action} - {self.ip_address} - {self.created}"
    