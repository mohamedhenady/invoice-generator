import pandas as pd
from typing import Optional, Dict, Any
import os

def read_invoice_excel(file_path: str, sheet_name: Optional[str] = None) -> Dict[Any, Any]:
    """
    تقوم بقراءة ملف Excel وتنظيف البيانات تمهيداً لعرضها في الفاتورة.
    """
    try:
        # قراءة أسماء الـ sheets
        xl = pd.ExcelFile(file_path)
        available_sheets = xl.sheet_names
        
        # اختيار الـ sheet الأولى كافتراضية
        selected_sheet = sheet_name if sheet_name and sheet_name in available_sheets else available_sheets[0]
        
        # قراءة البيانات
        df = pd.read_excel(file_path, sheet_name=selected_sheet)
        
        # 1. تنظيف أسماء الأعمدة: إزالة المسافات وتجنب التكرار
        df.columns = [str(col).strip() for col in df.columns]
        
        # 2. تنظيف البيانات: حذف الصفوف الفارغة
        df.dropna(how='all', inplace=True)
        # تحويل كل الأعمدة لنصوص (Object) لتجنب مشاكل النوع مع القيم الفارغة
        df = df.astype(object).fillna("")
        
        # تجهيز البيانات للإرجاع
        columns = df.columns.tolist()
        rows = df.values.tolist()
        row_count = len(rows)
        
        return {
            "columns": columns,
            "rows": rows,
            "row_count": row_count,
            "preview_df": df,
            "available_sheets": available_sheets,
            "selected_sheet": selected_sheet
        }
        
    except Exception as e:
        return {"error": f"حدث خطأ أثناء قراءة الملف: {str(e)}"}
