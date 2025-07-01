# NOTE: This version uses Playwright to accurately render JavaScript-based websites.
# You must run this locally or on a server that supports headless browsers.

import streamlit as st
from openai import OpenAI
from playwright.sync_api import sync_playwright
import os

# --- Streamlit Config ---
st.set_page_config(page_title="Startup Summarizer 💼", layout="centered")
st.title("Startup Summarizer 💼")
st.write("Paste a startup website link and get an accurate summary powered by GPT-4o.")

# --- OpenAI Client ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- Input ---
url = st.text_input("Startup Website URL (e.g. https://numerous.ai)")

# --- Function to extract visible site text ---
def get_visible_text_from_url(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            page.wait_for_load_state("networkidle")
            text = page.inner_text("body")
            browser.close()
            return text[:6000]  # Cap at ~6000 characters (approx. 4000 tokens)
    except Exception as e:
        return None

# --- Main Logic ---
if url:
    with st.spinner("Loading and summarizing the website..."):
        full_text = get_visible_text_from_url(url)

        if not full_text:
            st.error("❌ Could not extract meaningful content from the site. Try a different URL.")
        else:
            prompt = f"Summarize the business described on this website as if you are a professional startup analyst:\n\n{full_text}"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional venture capital analyst summarizing startups."},
                    {"role": "user", "content": prompt}
                ]
            )

            st.subheader("📄 Company Summary")
            st.write(response.choices[0].message.content)

            with st.expander("🔍 Raw Extracted Website Text"):
                st.text(full_text)
