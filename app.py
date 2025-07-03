import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import re
import pandas as pd

st.set_page_config("Invoice OCR Extractor", layout="centered")

# ────────────── Convert PDF page to image (via PyMuPDF, works on Streamlit Cloud)
def convert_pdf_to_image(uploaded_file):
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)  # first page
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")
    return Image.open(io.BytesIO(img_bytes))

# ────────────── Extract invoice data from text
def extract_invoice_data(text):
    invoice_number = re.search(r"INVOICE\s*#?:?\s*(\d+)", text, re.IGNORECASE)
    invoice_date   = re.search(r"DATE\s*[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})", text, re.IGNORECASE)
    total_amount   = re.search(r"TOTAL\s*[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)

    return {
        "Invoice Number": invoice_number.group(1) if invoice_number else "Not Found",
        "Invoice Date": invoice_date.group(1) if invoice_date else "Not Found",
        "Total Amount": total_amount.group(1) if total_amount else "Not Found"
    }

# ────────────── Streamlit App Layout
st.title("🧾 Invoice OCR Extractor")

uploaded_file = st.file_uploader("Upload scanned invoice PDF or image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    ext = uploaded_file.name.lower()
    
    if ext.endswith(".pdf"):
        image = convert_pdf_to_image(uploaded_file)
        text = pytesseract.image_to_string(image)
        method = "OCR (from scanned PDF)"
    else:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        method = "OCR (from image)"

    st.success(f"✅ Extracted using: {method}")

    invoice_data = extract_invoice_data(text)

    st.subheader("📋 Extracted Invoice Data")
    df = pd.DataFrame(invoice_data.items(), columns=["Field", "Value"])
    st.table(df)

    if st.checkbox("🧾 Show raw extracted text"):
        st.text_area("Raw OCR Text", value=text, height=300)
