# Deploying to Streamlit Cloud

This document explains how to deploy the Earnings Call PDF Summarizer application to Streamlit Cloud.

## Step 1: Push to GitHub

Make sure all code is pushed to your GitHub repository "Earning-Call-PDF".

## Step 2: Sign up for Streamlit Cloud

1. Visit [Streamlit Cloud](https://streamlit.io/cloud) and sign up/log in with your GitHub account.

## Step 3: Deploy the App

1. Click "New app" on the Streamlit Cloud dashboard.

2. Select your GitHub repository "Earning-Call-PDF".

3. Configure the deployment:
   - **Branch**: main
   - **Main file path**: app.py
   - **Python version**: 3.9 or 3.10
   - **Packages**: The system will use the `streamlit_requirements.txt` file automatically

4. Click "Deploy" to launch your application.

## Step 4: Share Your App

After deployment, Streamlit Cloud will provide a public URL for your application.
You can share this URL with anyone, and they can use your application without installing anything.

## Troubleshooting

- If you encounter NLTK-related errors, the application includes fallback mechanisms. The `setup.sh` script should ensure NLTK resources are downloaded during deployment.
- Check the Streamlit Cloud logs if you run into any issues during deployment.

## Limitations

- Streamlit Cloud has a timeout of about 5 minutes for processing files, which is more than sufficient for most earnings call PDF files.
- The free tier has a limit on the number of apps you can deploy and the compute resources available.

## Upgrading

If you need more resources or want to remove the Streamlit branding, Streamlit Cloud offers paid plans with additional benefits.