import json
import os
from pathlib import Path
from typing import Dict, Any

# إعدادات الشركة الافتراضية
DEFAULT_CONFIG = {
    "company_name": "Health Wave For Drug Trading",
    "company_address": "Nasr City Towers, Tower 2, 7B Al Wafaa & Al Amal St., Nasr City, Cairo, Egypt",
    "company_phone": "+20 122 528 3856",
    "company_email_1": "Ahmed@health-wave.net",
    "company_email_2": "Dr_ahmed_elomda@yahoo.com",
    "logo_path": "assets/logo.png"
}

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """تحميل إعدادات الشركة من ملف JSON أو إرجاع القيم الافتراضية."""
    path = Path(config_path)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config: Dict[str, Any], config_path: str = "config.json") -> bool:
    """حفظ إعدادات الشركة في ملف JSON."""
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False
