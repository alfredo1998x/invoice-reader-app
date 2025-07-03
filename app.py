import streamlit as st
import pdfplumber
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
            return "", "image"  # fallback disabled
    except:
        return "", "error"

def extract_text_from_image(uploaded_file):
    img = Image.open(uploaded_file)
    return pytesseract.image_to_string(img), "image"

def extract_invoice_data(text):
    invoice_number = re.search(r"INVOICE\s*#?:?\s*(\d+)", text, re.IGNORECASE)
    invoice_date   = re.search(r"DATE\s*[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})", text, re.IGNORECASE)
    total_amount   = re.search(r"TOTAL\s*[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)

    return {
        "Invoice Number": invoice_number.group(1) if invoice_number else "Not Found",
        "Invoice Date": invoice_date.group(1) if invoice_date else "Not Found",
        "Total Amount": total_amount.group(1) if total_amount else "Not Found"
    }

# ────────────────────── Streamlit UI ──────────────────────

st.title("🧾 Invoice OCR Extractor")

uploaded_file = st.file_uploader("Upload an invoice PDF or image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.name.lower()
    if file_type.endswith(".pdf"):
        text, method = extract_text_from_pdf(uploaded_file)
        if method == "image":
            st.error("❌ This PDF is scanned and cannot be read without OCR. Please upload an image instead.")
            st.stop()
    else:
        text, method = extract_text_from_image(uploaded_file)

    st.success(f"✅ Extracted using: {'OCR' if method == 'image' else 'Text layer'}")

    invoice_data = extract_invoice_data(text)

    st.subheader("📋 Extracted Invoice Data")
    df = pd.DataFrame(invoice_data.items(), columns=["Field", "Value"])
    st.table(df)

    if st.checkbox("🧾 Show raw extracted text"):
        st.text_area("Raw OCR Text", value=text, height=300)
