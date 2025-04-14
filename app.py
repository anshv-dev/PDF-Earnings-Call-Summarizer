import streamlit as st
from utils import extract_text_from_pdf, summarize_text
import tempfile
import io
import base64
import os

# Create temp directory if it doesn't exist
os.makedirs('temp', exist_ok=True)

# Initialize NLTK resources for Streamlit Cloud deployment
import nltk
try:
    # Only download if they don't exist
    if not os.path.exists(os.path.join(os.path.expanduser('~'), 'nltk_data', 'tokenizers', 'punkt')):
        nltk.download('punkt', quiet=True)
    if not os.path.exists(os.path.join(os.path.expanduser('~'), 'nltk_data', 'corpora', 'stopwords')):
        nltk.download('stopwords', quiet=True)
    print("NLTK resources initialized for deployment")
except Exception as e:
    print(f"Note: NLTK download error: {e}. Using fallback methods.")

# Set page configuration
st.set_page_config(
    page_title="Earnings Call PDF Summarizer",
    page_icon="📊",
    layout="wide"
)

# Main title and description
st.title("Earnings Call PDF Summarizer")
st.markdown("""
This application extracts text from earnings call PDFs and generates concise summaries 
highlighting key financial points. Upload an earnings call PDF to get started.
""")

# File uploader
uploaded_file = st.file_uploader("Upload Earnings Call PDF", type=["pdf"], help="Upload a PDF file of an earnings call transcript")

if uploaded_file is not None:
    # Create a progress bar for the overall process
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Extract text from PDF
        status_text.text("Extracting text from PDF...")
        
        # Save the uploaded PDF to a temporary file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Show the temp file path in the debug area
            st.write(f"Processing file: {uploaded_file.name}")
            progress_bar.progress(20)
        except Exception as save_error:
            st.error(f"Error saving the uploaded file: {str(save_error)}")
            raise
        
        # Try to extract text from the PDF
        try:
            extracted_text = extract_text_from_pdf(tmp_path)
            progress_bar.progress(40)
        except Exception as extract_error:
            st.error(f"Error extracting text from PDF: {str(extract_error)}")
            st.info("This could be due to PDF security settings or the PDF might not contain extractable text. Try a different PDF file.")
            raise
        
        # Validate the extracted text
        if not extracted_text or len(extracted_text.strip()) < 100:
            st.error("Could not extract sufficient text from the PDF. Please ensure the PDF contains extractable text.")
            progress_bar.empty()
            status_text.empty()
        else:
            # Step 2: Summarize the extracted text
            status_text.text("Generating summary...")
            try:
                summary = summarize_text(extracted_text)
                progress_bar.progress(90)
            except Exception as summary_error:
                st.error(f"Error generating summary: {str(summary_error)}")
                raise
            
            # Step 3: Display results
            status_text.text("Summary generated successfully!")
            progress_bar.progress(100)
            
            # Create tabs for original text and summary
            tab1, tab2 = st.tabs(["Summary", "Original Text"])
            
            with tab1:
                st.subheader("Earnings Call Summary")
                st.write(summary)
                
                # Create a download button for the summary
                try:
                    summary_bytes = summary.encode()
                    b64 = base64.b64encode(summary_bytes).decode()
                    filename = f"{uploaded_file.name.split('.')[0]}_summary.txt"
                    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Summary</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as download_error:
                    st.warning(f"Could not create download link: {str(download_error)}")
            
            with tab2:
                st.subheader("Original Extracted Text")
                st.text_area("Extracted content", extracted_text, height=400)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        progress_bar.empty()
        status_text.empty()
        # Display a more helpful message
        st.info("Troubleshooting tips: Make sure your PDF file is not password-protected and contains extractable text. Scanned PDFs may not work properly without OCR processing.")
else:
    # Display instructions when no file is uploaded
    st.info("Please upload an earnings call PDF to generate a summary.")
    
    # Example of what to expect
    st.subheader("What to expect")
    st.markdown("""
    1. **Upload** an earnings call PDF document
    2. The system will **extract** the text from the PDF
    3. Advanced NLP algorithms will **summarize** the content
    4. You can view and **download** the summary highlighting key financial points
    """)

# Add information footer
st.markdown("---")
st.markdown("""
**About this tool**: This application helps financial analysts save time by automatically extracting 
and summarizing key points from earnings call documents, allowing for quicker assessment of company 
performance and management outlooks.
""")
