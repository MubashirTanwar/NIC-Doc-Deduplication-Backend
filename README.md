# Document De-duplication Backend

---

## Overview

**Introduction:**
In today's digital landscape, the proliferation of PDF documents necessitates efficient management strategies. However, conventional methods often overlook document de-duplication, leading to redundant data storage and resource inefficiency. This project addresses this challenge by developing a bespoke API tailored for Marathi PDF de-duplication, leveraging the power of Transformer.

**Features:**
- PDF Support: 
Efficient processing of PDF documents.
- User Interface: User-friendly interface accessible to users with varying technical expertise.
- Accurate Text Extraction: Utilizes a custom TrOCR model to ensure precise text extraction, even from complex documents.
- Marathi Language Support: Focuses on Marathi text recognition and extraction.
- Fast Processing: Optimized for speed to deliver results promptly.
- Elasticsearch Integration: Utilizes Elasticsearch for efficient document storage and retrieval.

---

## Scope

The project aims to enhance operational efficiency and preserve crucial information for educational institutions, government bodies, and corporations dealing with extensive paperwork. It focuses on creating a robust system for managing digital documents in the Marathi language, utilizing a custom TrOCR model trained on a comprehensive Marathi dataset. While currently focused on Marathi, there is potential for future expansion to include other languages and document formats.

---

## Technologies Used

- Frontend: React
- Backend: Django REST API, Elasticsearch, Kibana
- TrOCR Marathi: HuggingFace, TrOCR, Google-ViT, Tesseract

---

## Requirements / Dependencies

Ensure you have the following software installed on your local machine before running the frontend of the application:

- **Elasticsearch and Kibana:** Install Elasticsearch and Kibana by following the instructions on the [official Elastic website](https://www.elastic.co/downloads/). Ensure both Elasticsearch and Kibana services are started.

- **Node.js:** Install Node.js from the [official Node.js website](https://nodejs.org/). Verify the installation by running `node --version` and `npm --version` in your terminal.

- **Python:** Install Python from the [official Python website](https://www.python.org/downloads/). Verify the installation by running `python --version` and `pip --version` in your terminal.
- **Tesseract:** Install Tesseract OCR by following the instructions on the [official Tesseract OCR GitHub page](https://github.com/tesseract-ocr/tesseract). Verify the installation by running `tesseract --version` in your terminal.
- **PostgreSQL:** Install PostgreSQL and set up a database. You can download it from the [official PostgreSQL website](https://www.postgresql.org/download/).


Make sure you have the required versions of these software installed to ensure smooth functioning of the application.


---
## Usage

To run the backend of the application, follow these steps:

### **Clone the repository:**

```bash
git clone https://github.com/MubashirTanwar/NIC-Doc-Deduplication-Backend
```

###  **Navigate to the project directory:**

```bash
cd ./NIC-Doc-Deduplication-Backend
```

### **Apply migrations:**

```bash
python manage.py migrate
```

### **Start the development server:**

```bash
python manage.py runserver
```

### **Start Kibana and Elasticsearch**
```bash
cd path/to/elasticsearch/bin
elasticsearch.bat

cd path/to/kibana/bin
kibana.bat
```

### **Access the application:**

The Django API will be accessible at `http://127.0.0.1:8000/`


---

## Conclusion

In conclusion, this project offers a comprehensive frontend solution for PDF document de-duplication, representing a significant advancement in document management and search. By automating processes and emphasizing the Marathi language, it not only improves efficiency but also contributes to the preservation and accessibility of Marathi documents. Its success could pave the way for similar systems in other languages, broadening the scope of automated document management and search.


---

## Links

- **React Frontend Repository:** [Github](https://github.com/MubashirTanwar/NIC-Doc-Deduplication-Web-App)

- **TrOCR Training and Inference Repository:** [Github](https://github.com/MubashirTanwar/TrOCR)
- **Marathi Dataset**: [Github](https://github.com/MubashirTanwar/TrOCR)
