#!/bin/bash

# Download NLTK data (if needed for your project)
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Make any other setup steps here