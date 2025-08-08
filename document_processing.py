#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Dell
#
# Created:     04-08-2025
# Copyright:   (c) Dell 2025
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import requests
import fitz
import os

document_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
local_filename = "policy.pdf"

def download_file(url, filename):
    print(f"Downloading file from {url}..")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File download and saved as {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
        return False

def extract_text_from_pdf(filename):
    print(f"Extracting text from {filename}..")
    text_content = ""
    try:
        with fitz.open(filename) as doc:
            for page in doc:
                text_content += page.get_text()
        print("Text extraction successfull!!")
        return text_content
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

if __name__=="__main__":
    if download_file(document_url, local_filename):
        extracted_text = extract_text_from_pdf(local_filename)
        if extracted_text:
            print("\n---Extracted Text Preview (first 500 characters)---")
            print(extracted_text[:500])
            #print("\nFull Extracted Text ----")
            #print(extracted_text)
        os.remove(local_filename)
        print(f"\nCleaned up local file: {local_filename}")


