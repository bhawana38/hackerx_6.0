import streamlit as st
import requests
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    st.set_page_config(page_title="Ask your PDF via API")
    st.header("Ask your PDF via HackerX API 🤓")

    # Input PDF URL
    pdf_url = st.text_input("Enter the PDF URL:")

    # Input questions
    questions_input = st.text_area("Enter your questions (one per line):")

    # API token
    api_token = st.text_input("Enter API Bearer Token:", type="password")

    if st.button("Send Request"):
        if not pdf_url or not questions_input:
            st.error("Please provide both PDF URL and at least one question.")
            return

        # Prepare JSON payload
        payload = {
            "documents": pdf_url,
            "questions": [q.strip() for q in questions_input.split("\n") if q.strip()]
        }

        try:
            # Send POST request to your deployed Railway app
            response = requests.post(
                "https://llm-query-model-hackerx.up.railway.app/hackrx/run",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_token}"
                },
                json=payload
            )

            if response.status_code == 200:
                st.subheader("API Response:")
                st.json(response.json())
            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")

if __name__ == '__main__':
    main()
