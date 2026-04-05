import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from pathlib import Path

# استيراد الأجزاء الداخلية
from core.invoice_model import InvoiceData
from core.excel_reader import read_invoice_excel
from core.pdf_generator import generate_pdf
from core.config_manager import load_config, save_config

# --- 1. إعدادات الصفحة والتحقق من المجلدات ---
st.set_page_config(
    page_title="مولّد فواتير Health Wave",
    page_icon="🧾",
    layout="wide"
)

# دعم اللغة العربية (RTL)
st.markdown("""
<style>
    body { direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; }
    .main-header { padding: 20px 0; font-weight: 700; border-bottom: 2px solid var(--primary-color, #1a5276); margin-bottom: 30px; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: 600; padding: 10px; }
    .stDownloadButton>button { padding: 10px; border-radius: 5px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# مسارات المشروع
BASE_PATH = Path(__file__).parent
CONFIG_FILE = BASE_PATH / "config.json"
ASSETS_DIR = BASE_PATH / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# تحميل الإعدادات في الـ session state
if "config" not in st.session_state:
    st.session_state.config = load_config(str(CONFIG_FILE))

# --- 3. تصميم الواجهة ---
st.markdown('<h1 class="main-header">🧾 مولّد فواتير Health Wave</h1>', unsafe_allow_html=True)



# القسم الثاني: بيانات الفاتورة
st.subheader("📋 بيانات الفاتورة")
col_meta1, col_meta2, col_meta3, col_meta4 = st.columns(4)
with col_meta1:
    customer_name = st.text_input("Customer Name *")
with col_meta2:
    invoice_number = st.text_input("Invoice Number *", value=f"HW-{date.today().strftime('%Y%m')}-001")
with col_meta3:
    invoice_date_val = st.date_input("Date *", value=date.today())
with col_meta4:
    invoice_total_val = st.text_input("Invoice Total")

notes_content = st.text_area("ملاحظات (تظهر في أسفل الفاتورة)", placeholder="أدخل أي ملاحظات إضافية هنا...")

# القسم الثالث: بيانات ملف Excel
st.subheader("📊 بيانات المنتجات (Excel)")
excel_file = st.file_uploader("ارفع ملف Excel الذي يحتوي على بيانات الفاتورة", type=["xlsx", "xls"])

if excel_file:
    # حفظ الملف مؤقتاً لقراءته
    with open("temp_invoice.xlsx", "wb") as f:
        f.write(excel_file.getbuffer())
    
    result = read_invoice_excel("temp_invoice.xlsx")
    
    if "error" in result:
        st.error(result["error"])
    else:
        st.info(f"✅ تم اكتشاف {result['row_count']} منتج في ملف Excel.")
        st.dataframe(result["preview_df"], use_container_width=True)
        
        # اختيار الـ Sheet في حال وجود أكثر من واحدة
        if len(result["available_sheets"]) > 1:
            selected_sheet = st.selectbox("اكتشفنا صفحات متعددة، اختر الصفحة المطلوبة:", result["available_sheets"])
            if selected_sheet != result["selected_sheet"]:
                result = read_invoice_excel("temp_invoice.xlsx", sheet_name=selected_sheet)
                st.dataframe(result["preview_df"])

        # التحكم في عرض الأعمدة
        st.markdown("---")
        st.write("📏 **التحكم في عرض الأعمدة (%)**")
        st.caption("ملاحظة: يمكنك تعديل النسبة لكل عمود للحصول على أفضل شكل. (تم تخصيص عرض ثابت لعمود الترقيم #).")
        col_widths = []
        num_cols = len(result["columns"])
        split_cols = st.columns(num_cols)
        for i, col_name in enumerate(result["columns"]):
            with split_cols[i]:
                default_w = int(100 / num_cols)
                w = st.slider(col_name, min_value=1, max_value=100, value=default_w, key=f"col_w_{i}")
                col_widths.append(w)

        # القسم الرابع: التوليد والتحميل
        st.markdown("---")
        if st.button("🚀 توليد وتحميل الفاتورة PDF"):
            if not customer_name or not invoice_number:
                st.warning("⚠️ يرجى ملء اسم العميل ورقم الفاتورة أولاً.")
            else:
                try:
                    with st.spinner("جاري إنشاء الفاتورة..."):
                        # بناء نموذج البيانات
                        invoice_data_obj = InvoiceData(
                            customer_name=customer_name,
                            invoice_number=invoice_number,
                            invoice_date=invoice_date_val.strftime("%Y/%m/%d"),
                            invoice_total=invoice_total_val,
                            columns=result["columns"],
                            rows=result["rows"],
                            column_widths=col_widths,
                            company_name=st.session_state.config["company_name"],
                            company_address=st.session_state.config["company_address"],
                            company_phone=st.session_state.config["company_phone"],
                            company_email_1=st.session_state.config["company_email_1"],
                            company_email_2=st.session_state.config["company_email_2"],
                            logo_path=st.session_state.config["logo_path"],
                            notes=notes_content
                        )
                        
                        # توليد PDF
                        pdf_bytes = generate_pdf(invoice_data_obj)
                        
                        # زر التحميل
                        st.success("✅ الفاتورة جاهزة!")
                        st.download_button(
                            label="⬇️ تنزيل ملف PDF",
                            data=pdf_bytes,
                            file_name=f"Invoice_{invoice_number}.pdf",
                            mime="application/pdf"
                        )
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التوليد: {str(e)}")

# إزالة الملف المؤقت عند الانتهاء (اختياري)
if os.path.exists("temp_invoice.xlsx") and not excel_file:
    os.remove("temp_invoice.xlsx")
