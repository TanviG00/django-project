
import docx
import PyPDF2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer
import os
from rest_framework.parsers import MultiPartParser, FormParser
from litellm import completion, OpenAIError
import cv2
import pytesseract
import numpy as np

# Set up your LLM API key
os.environ["GEMINI_API_KEY"] = "AIzaSyCIBF3vThHIHVWIaX5uHYFbZDSXwRD5VxA"

class QuestionAnswerAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file_instance = serializer.save()
            file_path = file_instance.file.path

            # Extract text from the uploaded file
            file_text = self.extract_text_from_file(file_path)

            # Generate questions and answers using LLM
            qa_pairs = self.generate_qa(file_text)

            return Response({'qa_pairs': qa_pairs}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_text_from_file(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        text = ""

        if ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + '\n'

        elif ext in ['.png', '.jpg', '.jpeg']:
            # Handle image file using OpenCV
            image = cv2.imread(file_path)
            text = pytesseract.image_to_string(image)

        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in range(len(reader.pages)):
                    text += reader.pages[page].extract_text()

        elif ext == '.txt':
            with open(file_path, 'r') as f:
                text = f.read()

        return text

    def generate_qa(self, text):
        qa_pairs = []
        questions = text.split('\n')  # Simplistic approach, assuming each line is a question

        for question in questions:
            if question.strip():  # Ignore empty questions
                try:
                    response = completion(
                        model="gemini/gemini-pro",
                        messages=[{"content": question, "role": "user"}],
                    )
                    answer = response['choices'][0]['message']['content']
                    qa_pairs.append({'question': question, 'answer': answer})
                except OpenAIError as e:
                    qa_pairs.append({'question': question, 'error': str(e)})

        return qa_pairs

                   
                    

