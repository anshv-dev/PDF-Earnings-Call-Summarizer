import PyPDF2
import pypdf
import pdfplumber
import nltk
import ssl
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
import heapq

# Make sure NLTK resources are available
try:
    # Configure SSL context for NLTK downloads if needed
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Download required NLTK resources
    nltk.data.path.append('/home/runner/nltk_data')  # Ensure the path is included
    
    # Check if resources exist, download if needed
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        print("NLTK resources found")
    except LookupError:
        print("Downloading NLTK resources...")
        nltk.download('punkt')
        nltk.download('stopwords')
        print("NLTK resources downloaded successfully")
except Exception as e:
    print(f"Error with NLTK resources: {e}")
    # Continue even if there's an issue, as we'll handle exceptions in the functions

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using multiple methods.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    text = ""
    extraction_methods_tried = []
    
    try:
        # Add error handling details
        print(f"Opening PDF file: {pdf_path}")
        if not os.path.exists(pdf_path):
            raise Exception(f"PDF file does not exist at path: {pdf_path}")
            
        # Method 1: Try pdfplumber first (often works better for complex layouts)
        try:
            print("Attempting to extract with pdfplumber...")
            extraction_methods_tried.append("pdfplumber")
            
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"PDF has {num_pages} pages (pdfplumber)")
                
                for page_num, page in enumerate(pdf.pages):
                    print(f"Processing page {page_num+1}/{num_pages} (pdfplumber)")
                    page_text = page.extract_text()
                    
                    if page_text:
                        text += page_text + "\n"
                    else:
                        print(f"Warning: No text extracted from page {page_num+1} (pdfplumber)")
        except Exception as plumber_error:
            print(f"pdfplumber extraction failed: {str(plumber_error)}")
            
            # Method 2: Try PyPDF2 
            try:
                print("Attempting to extract with PyPDF2...")
                extraction_methods_tried.append("PyPDF2")
                
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Check if PDF has pages
                    num_pages = len(pdf_reader.pages)
                    print(f"PDF has {num_pages} pages (PyPDF2)")
                    
                    # Extract text from each page
                    for page_num in range(num_pages):
                        print(f"Processing page {page_num+1}/{num_pages} (PyPDF2)")
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        # Check if text was extracted properly
                        if page_text:
                            text += page_text + "\n"
                        else:
                            print(f"Warning: No text extracted from page {page_num+1} (PyPDF2)")
                            
            except Exception as pdf2_error:
                print(f"PyPDF2 extraction failed: {str(pdf2_error)}")
                
                # Method 3: Try pypdf as a final fallback
                try:
                    print("Attempting to extract with pypdf...")
                    extraction_methods_tried.append("pypdf")
                    
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_reader = pypdf.PdfReader(pdf_file)
                        
                        num_pages = len(pdf_reader.pages)
                        print(f"PDF has {num_pages} pages (pypdf)")
                        
                        for page_num in range(num_pages):
                            print(f"Processing page {page_num+1}/{num_pages} (pypdf)")
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            
                            if page_text:
                                text += page_text + "\n"
                            else:
                                print(f"Warning: No text extracted from page {page_num+1} (pypdf)")
                    
                except Exception as pypdf_error:
                    print(f"pypdf extraction also failed: {str(pypdf_error)}")
                    errors = {
                        "pdfplumber": str(plumber_error) if "pdfplumber" in extraction_methods_tried else "Not tried",
                        "PyPDF2": str(pdf2_error) if "PyPDF2" in extraction_methods_tried else "Not tried",
                        "pypdf": str(pypdf_error) if "pypdf" in extraction_methods_tried else "Not tried"
                    }
                    error_msg = ", ".join([f"{k}: {v}" for k, v in errors.items() if v != "Not tried"])
                    raise Exception(f"All PDF extraction methods failed. Errors: {error_msg}")
                
        # Clean the extracted text and return
        if text:
            text = clean_text(text)
            print(f"Successfully extracted {len(text)} characters of text")
            return text
        else:
            # If we got here but have no text, all methods were tried but failed to extract text
            methods_str = ", ".join(extraction_methods_tried)
            raise Exception(f"No text could be extracted from the PDF using methods: {methods_str}. The PDF might be scanned or have content restrictions.")
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def clean_text(text):
    """
    Clean the extracted text by removing extra whitespaces and special characters.
    
    Args:
        text (str): Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    # Remove unnecessary line breaks
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def extract_financial_keywords(text):
    """
    Extract financial keywords from the text to prioritize in the summary.
    
    Args:
        text (str): The input text
        
    Returns:
        set: Set of financial keywords found in the text
    """
    financial_terms = [
        'revenue', 'profit', 'earnings', 'ebitda', 'income', 'margin', 'cash flow',
        'balance sheet', 'assets', 'liabilities', 'debt', 'equity', 'dividend',
        'eps', 'guidance', 'forecast', 'outlook', 'growth', 'decline', 'increase',
        'decrease', 'quarter', 'fiscal', 'year', 'annual', 'quarterly', 'billion',
        'million', 'percent', 'market share', 'capital', 'investment', 'stock',
        'shareholder', 'investor', 'performance', 'target', 'expectation'
    ]
    
    found_terms = set()
    text_lower = text.lower()
    
    for term in financial_terms:
        if term in text_lower:
            found_terms.add(term)
            
    return found_terms

def custom_sentence_tokenize(text):
    """
    Custom sentence tokenization function to avoid using nltk's sent_tokenize
    which is causing the punkt_tab error.
    
    Args:
        text (str): Text to tokenize into sentences
        
    Returns:
        list: List of sentences
    """
    # Simple regex-based sentence tokenization
    # This handles periods, question marks, and exclamation points
    import re
    # Split on periods, question marks, or exclamation points followed by space or newline
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Remove empty sentences
    return [s.strip() for s in sentences if s.strip()]

def summarize_text(text, max_sentences=15):
    """
    Summarize the text focusing on key financial points.
    
    Args:
        text (str): The text to summarize
        max_sentences (int): Maximum number of sentences in the summary
        
    Returns:
        str: Generated summary highlighting key financial points
    """
    try:
        # Use custom sentence tokenizer instead of NLTK's sent_tokenize
        sentences = custom_sentence_tokenize(text)
        print(f"Successfully tokenized text into {len(sentences)} sentences")
        
        # If there are too few sentences, return the original text
        if len(sentences) <= max_sentences:
            return text
            
        # Extract financial keywords
        financial_keywords = extract_financial_keywords(text)
        
        try:
            # Try to use NLTK stopwords
            stop_words = set(stopwords.words('english'))
        except Exception as e:
            print(f"Error loading stopwords: {e}. Using custom stopwords list.")
            # Fallback to a basic list of stopwords if NLTK's stopwords fail
            stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 
                          'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
                          'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 
                          'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 
                          'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
                          'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 
                          'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
                          'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 
                          'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                          'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 
                          'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 
                          'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 
                          'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 
                          't', 'can', 'will', 'just', 'don', 'should', 'now'}
        
        # Custom tokenize words
        def simple_word_tokenize(text):
            """Simple word tokenizer to replace NLTK's word_tokenize"""
            import re
            return re.findall(r'\b\w+\b', text.lower())
        
        # Tokenize words and remove stopwords
        word_tokens = simple_word_tokenize(text.lower())
        filtered_words = [word for word in word_tokens if word.isalnum() and word not in stop_words]
        
        # Calculate word frequencies
        word_counts = {}
        for word in filtered_words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        
        # Calculate sentence scores
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = simple_word_tokenize(sentence.lower())
            
            # Higher weight for sentences at the beginning or end (often contain key information)
            position_weight = 1.0
            if i < len(sentences) * 0.1 or i > len(sentences) * 0.9:
                position_weight = 1.5
                
            # Higher weight for sentences containing financial keywords
            financial_weight = 1.0
            for keyword in financial_keywords:
                if keyword in sentence.lower():
                    financial_weight = 2.0
                    break
                    
            # Calculate the score based on word frequencies and weights
            score = 0
            for word in words:
                if word in word_counts:
                    score += word_counts[word]
                    
            # Apply weights
            score = score * position_weight * financial_weight
            sentence_scores[sentence] = score
        
        # Get top sentences for the summary
        summary_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:max_sentences]
        summary_sentences = [s[0] for s in summary_sentences]  # Get just the sentences, not the scores
        
        # Reorder sentences based on their original position to maintain logical flow
        ordered_summary = []
        for sentence in sentences:
            if sentence in summary_sentences:
                ordered_summary.append(sentence)
                if len(ordered_summary) >= max_sentences:
                    break
        
        # Join sentences to form the summary
        summary = ' '.join(ordered_summary)
        
        # Add a header and the financial keywords found
        header = "Key Financial Points:\n\n"
        
        return header + summary
        
    except Exception as e:
        print(f"Error in summarize_text: {str(e)}")
        # Fallback to returning a truncated version of the text if summarization fails
        return f"Key Financial Points:\n\n{text[:5000]}...\n\n[Full text was too long to display]"
