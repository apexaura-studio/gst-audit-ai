import time
import streamlit as st
from google import genai
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
    client = genai.Client(api_key=api_key.strip())

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
            with st.spinner("Compliance details check ki ja rahi hain (load zyada ho toh auto-retry hoga)..."):
                prompt = f"""
                You are an Indian GST and MSME Compliance Assistant for local vendors and small businesses.
                Analyze the following details for a {vendor_type}:

                Data: {final_data}

                Language & Style Rules:
                - Write the entire report in clean, natural Hinglish using Roman script (Latin alphabet), matching the app UI style.
                - Keep standard GST, tax, and MSME technical terms in clear English (for example: GSTIN, HSN/SAC, CGST, SGST, IGST, Taxable Value, Invoice No, Invoice Date, Input Tax Credit, GSTR-1, GSTR-2B, Udyam, MSMED Act, Section 43B(h), E-way Bill).
                - Avoid Devanagari script so the tone stays consistent throughout.
                - Keep formatting crisp, structured, and easy to read on a mobile screen.

                Structure the report into these 4 sections:
                1. **GSTIN Format & Structure Check**: Check if a GSTIN is present and whether its 15-character structure looks valid (state code, PAN format, entity/check structure). Clearly note that live active/inactive status requires official GST portal verification.
                2. **Invoice Basics Check**: Check key details like Invoice No, Invoice Date, HSN/SAC code, Place of Supply, and tax breakup (CGST/SGST/IGST) along with basic calculation accuracy, highlighting anything missing or unclear.
                3. **MSME & Payment Awareness**: Highlight relevant MSME compliance points (such as Udyam registration details and timely payment rules / 45-day awareness where applicable) based on the provided info.
                4. **Next Steps**: Give 3 practical, actionable steps for the small business owner.
                """

                contents = [prompt, file_content] if (uploaded_file and not isinstance(file_content, str)) else prompt

                report_text = None
                last_error = None
                models_to_try = ["gemini-3.8-flash", "gemini-3.8-pro"]

                for model_name in models_to_try:
                    for attempt in range(3):
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=contents
                            )
                            if response and response.text:
                                report_text = response.text
                                break
                        except Exception as e:
                            last_error = e
                            err_str = str(e)
                            if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                                time.sleep(2 * (attempt + 1))
                                continue
                            break
                    if report_text:
                        break

                if report_text is None:
                    st.error(f"Audit generate karte waqt error aaya: {last_error}")
                    st.stop()

                st.subheader("📊 Basic Audit Report")
                st.markdown(report_text)

                st.divider()
                st.info("💎 **Aage ke liye Pro Idea:** Bulk invoice check, detailed checklist export, aur vendor summary reports isme aage add kiye ja sakte hain.")
        else:
            st.warning("Kripya audit ke liye text enter karein ya file upload karein.")
else:
    st.info("💡 Aage badhne ke liye upar apni Gemini API key daalein.")
    
