import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

st.set_page_config(page_title="Startup Summarizer 💼", layout="centered")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Startup Summarizer 💼")
st.write("Paste the homepage of a startup, and I’ll tell you what the company does.")

url = st.text_input("Startup Website URL (e.g. https://numerous.ai)")

def extract_text(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]  # Limit input size to avoid token overage
    except Exception:
        return None

if url:
    with st.spinner("Summarizing the company..."):
        site_text = extract_text(url)

        if not site_text:
            st.error("⚠️ Could not read the website. Try a different URL.")
        else:
            prompt = f"Summarize the business described on this website:\n\n{site_text}"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a VC analyst who summarizes what startups do."},
                    {"role": "user", "content": prompt}
                ]
            )

            st.subheader("📄 Company Summary")
            st.write(response.choices[0].message.content)
