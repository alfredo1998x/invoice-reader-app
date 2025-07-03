import streamlit as st
import pdfplumber
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import re
import pandas as pd

st.set_page_config("Invoice Reader", layout="centered")

# ────────────────────── Helper Functions ──────────────────────

def extract_text_from_pdf(uploaded_file):
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        if text.strip():
            return text, "text"
        else:
            # Fallback to OCR
            images = convert_from_bytes(uploaded_file.read())
            return pytesseract.image_to_string(images[0]), "image"
    except:
        images = convert_from_bytes(uploaded_file.read())
        return pytesseract.image_to_string(images[0]), "image"

def extract_text_from_image(uploaded_file):
    img = Image.open(uploaded_file)
    return pytesseract.image_to_string(img), "image"

def extract_invoice_data(text):
    data = {}
    data["Invoice Number"] = re.search(r"Invoice\s*#?:?\s*(\d+)", text, re.IGNORECASE)
    data["Invoice Date"]   = re.search(r"Date\s*:? ?(\d{1,2}/\d{1,2}/\d{4})", text)
    data["Total Amount"]   = re.search(r"Total\s*\$?([\d,]+\.\d{2})", text)

    return {
        "Invoice Number": data["Invoice Number"].group(1) if data["Invoice Number"] else "Not Found",
        "Invoice Date": data["Invoice Date"].group(1) if data["Invoice Date"] else "Not Found",
        "Total Amount": data["Total Amount"].group(1) if data["Total Amount"] else "Not Found"
    }

# ────────────────────── UI ──────────────────────

st.title("🧾 Invoice OCR Extractor")

uploaded_file = st.file_uploader("Upload an invoice PDF or image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.name.lower()
    if file_type.endswith(".pdf"):
        text, method = extract_text_from_pdf(uploaded_file)
    else:
        text, method = extract_text_from_image(uploaded_file)

    st.success(f"✅ Extracted using: {'OCR' if method == 'image' else 'Text layer'}")
    invoice_data = extract_invoice_data(text)

    st.subheader("📋 Extracted Invoice Data")
    df = pd.DataFrame(invoice_data.items(), columns=["Field", "Value"])
    st.table(df)

    if st.checkbox("🧾 Show raw extracted text"):
        st.text_area("Raw OCR Text", value=text, height=300)