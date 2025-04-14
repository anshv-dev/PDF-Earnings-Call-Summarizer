# Earnings Call PDF Summarizer

A Streamlit application that extracts text from earnings call PDFs and generates concise summaries highlighting key financial points.

## Features

- **PDF Text Extraction**: Uploads and processes PDF files to extract text content.
- **Multiple Extraction Methods**: Uses multiple PDF text extraction libraries (pdfplumber, PyPDF2, pypdf) with automatic fallbacks.
- **Financial Keyword Recognition**: Identifies important financial terms for better summarization.
- **Advanced Summarization**: Prioritizes sentences with key financial content.
- **User-Friendly Interface**: Simple upload, view, and download functionality.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/anshv-dev/Earning-Call-PDF.git
cd Earning-Call-PDF
```

2. Install the required packages:
```bash
pip install streamlit nltk PyPDF2 pypdf pdfplumber
```

3. Download NLTK resources (if needed):
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Upload an earnings call PDF document.

3. View the generated summary highlighting key financial points.

4. Download the summary as a text file.

## How It Works

1. The application allows you to upload a PDF file.
2. It extracts text from the PDF using multiple extraction methods with fallbacks.
3. The text is tokenized into sentences and analyzed for important financial information.
4. Sentences are ranked based on:
   - Presence of financial keywords
   - Position in the document
   - Word frequency
5. The top-ranked sentences are selected, reordered to maintain original flow, and presented as a summary.

## Dependencies

- streamlit: Web application framework
- nltk: Natural language processing capabilities
- PyPDF2, pypdf, pdfplumber: PDF text extraction libraries