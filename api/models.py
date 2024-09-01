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
    user = models.ForeignKey('Users', on_delete=models.CASCADE)                      # TODO: This should be a foreign key to the User model
    created = models.DateTimeField(auto_now_add=True)

class Logs(models.Model):
    user = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=255)   
    created = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f"{self.user} - {self.action} - {self.ip_address} - {self.created}"


class Users(models.Model):
    username = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} - {self.email} - {self.created}" 