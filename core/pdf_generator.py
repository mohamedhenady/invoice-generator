import base64
import os
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from .invoice_model import InvoiceData

logger = logging.getLogger(__name__)

def _get_jinja_env(template_dir: str) -> Environment:
    """إعداد بيئة Jinja2 لتحميل القوالب."""
    return Environment(loader=FileSystemLoader(template_dir), autoescape=True)

def _encode_logo(logo_path: str) -> str:
    """تحويل صورة اللوجو لـ Base64 string لاستخدامها في HTML/PDF."""
    try:
        if not os.path.exists(logo_path):
            return ""
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
            return f"data:image/png;base64,{logo_b64}"
    except Exception as e:
        logger.error(f"Logo encoding error: {str(e)}")
        return ""

def generate_pdf(invoice: InvoiceData) -> bytes:
    """
    تأخذ بيانات الفاتورة، تملأ القالب، وتولّد ملف PDF وتعيده كـ bytes.
    """
    try:
        # 1. تحديد المسارات
        current_dir = Path(__file__).parent.parent
        template_dir = current_dir / "templates"
        
        # 2. تجهيز اللوجو
        logo_path = current_dir / invoice.logo_path
        logo_src = _encode_logo(str(logo_path))
        
        # 3. تحميل القالب
        env = _get_jinja_env(str(template_dir))
        template = env.get_template("invoice.html")
        
        # 4. الريندر (Rendering)
        # نقوم بإضافة logo_src ليكون متاحاً في التيمبليت
        html_content = template.render(
            invoice={
                **invoice.__dict__,
                "logo_src": logo_src
            }
        )
        
        # 5. توليد PDF
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"PDF Generation Error: {str(e)}")
        raise RuntimeError(f"فشل توليد الـ PDF: {str(e)}")
