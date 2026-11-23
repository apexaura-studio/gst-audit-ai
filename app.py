import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

st.set_page_config(
    page_title="LocalVendor & MSME Compliance Auditor AI",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ LocalVendor & MSME Compliance Auditor")
st.caption("Free Basic Check — GSTIN format, invoice basics, aur MSME compliance guidance ke liye.")

st.warning(
    "⚠️ **Disclaimer:** Yeh AI tool sirf initial guidance aur compliance awareness ke liye hai. "
    "Yeh koi legal, tax, ya Chartered Accountant (CA) ki official salah nahi hai. Final filing ya tax decision se pehle apne CA ya tax advisor se confirm karein."
)

api_key = st.text_input("Apni Gemini API Key enter karein:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-pro")

    vendor_type = st.selectbox(
        "Vendor / Enterprise Category chunein:",
        [
            "Micro Enterprise (MSME)",
            "Small Enterprise (MSME)",
            "Medium Enterprise (MSME)",
            "Unregistered Local Vendor"
        ]
    )

    input_mode = st.radio(
        "Data kaise dena chahte hain?",
        ["Text / GSTIN paste karein", "Invoice File (PDF/Image) upload karein"]
    )

    input_text = ""
    uploaded_file = None

    if input_mode == "Text / GSTIN paste karein":
        input_text = st.text_area("Yahan GSTIN, bill details, ya payment terms paste karein:")
    else:
        uploaded_file = st.file_uploader(
            "Invoice upload karein (PDF, PNG, JPG):",
            type=["pdf", "png", "jpg", "jpeg"]
        )

    if st.button("🚀 Run Free Basic Audit"):
        file_content = None
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                reader = pypdf.PdfReader(uploaded_file)
                file_content = "".join([page.extract_text() or "" for page in reader.pages])
            else:
                file_content = Image.open(uploaded_file)

        final_data = input_text.strip() if input_mode == "Text / GSTIN paste karein" else file_content

        if final_data:
            with st.spinner("Compliance details check ki ja rahi hain..."):
                prompt = f"""
                You are an Indian GST and MSME Compliance Assistant for local vendors and small businesses.
                Analyze the following details for a {vendor_type}:

                Data: {final_data}

                Provide a clear, easy-to-understand basic audit report in simple Hindi/Hinglish with English technical terms where needed:
                1. **GSTIN Format & Structure Check**: Check if a GSTIN is present and whether its structure looks valid (15-character format). Note that live government portal status requires official verification.
                2. **Invoice Basics Check**: Look for key details like invoice number, date, HSN/SAC, and tax breakup (CGST/SGST/IGST), and point out anything missing or unclear.
                3. **MSME & Payment Awareness**: Briefly highlight relevant MSME compliance points (such as Udyam details or timely payment awareness) based on the provided info.
                4. **Next Steps**: Give 2-3 practical action points for the small business owner.
                """

                if uploaded_file and not isinstance(file_content, str):
                    response = model.generate_content([prompt, file_content])
                else:
                    response = model.generate_content(prompt)

                st.subheader("📊 Basic Audit Report")
                st.markdown(response.text)

                st.divider()
                st.info("💎 **Aage ke liye Pro Idea:** Bulk invoice check, detailed checklist export, aur vendor summary reports isme aage add kiye ja sakte hain.")
        else:
            st.warning("Kripya audit ke liye text enter karein ya file upload karein.")
else:
    st.info("💡 Aage badhne ke liye upar apni Gemini API key daalein.")
