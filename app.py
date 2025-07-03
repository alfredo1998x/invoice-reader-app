import streamlit as st
import fitz  # PyMuPDF
import requests
from PIL import Image
import io
import re
import pandas as pd

st.set_page_config("Invoice OCR Extractor", layout="centered")

OCR_API_KEY = "helloworld"  # Free key from ocr.space

# ───────────── Convert scanned PDF to image using PyMuPDF
def convert_pdf_to_image(uploaded_file):
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=300)
    img_bytes = pix.tobytes("png")
    return img_bytes

# ───────────── Use OCR.space API for cloud-based OCR
def run_ocr_api(image_bytes):
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("image.png", image_bytes)},
        data={"apikey": OCR_API_KEY, "language": "eng"},
    )
    result = response.json()
    if result["IsErroredOnProcessing"]:
        return "Error processing OCR."
    return result["ParsedResults"][0]["ParsedText"]

# ───────────── Extract fields using regex
def extract_invoice_data(text):
    invoice_number = re.search(r"INVOICE\s*#?:?\s*(\d+)", text, re.IGNORECASE)
    invoice_date   = re.search(r"DATE\s*[:\s]*([0-9]{2}/[0-9]{2}/[0-9]{4})", text, re.IGNORECASE)
    total_amount   = re.search(r"TOTAL\s*[:\s]*\$?([\d,]+\.\d{2})", text, re.IGNORECASE)

    return {
        "Invoice Number": invoice_number.group(1) if invoice_number else "Not Found",
        "Invoice Date": invoice_date.group(1) if invoice_date else "Not Found",
        "Total Amount": total_amount.group(1) if total_amount else "Not Found"
    }

# ───────────── UI
st.title("🧾 Invoice OCR Extractor (Cloud-Based)")

uploaded_file = st.file_uploader("Upload a scanned invoice PDF or image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_ext = uploaded_file.name.lower()

    if file_ext.endswith(".pdf"):
        img_bytes = convert_pdf_to_image(uploaded_file)
    else:
        img_bytes = uploaded_file.read()

    with st.spinner("🔍 Running OCR..."):
        text = run_ocr_api(img_bytes)

    st.success("✅ OCR complete!")

    invoice_data = extract_invoice_data(text)

    st.subheader("📋 Extracted Invoice Data")
    df = pd.DataFrame(invoice_data.items(), columns=["Field", "Value"])
    st.table(df)

    if st.checkbox("🧾 Show raw OCR text"):
        st.text_area("Raw OCR Text", text, height=300)
