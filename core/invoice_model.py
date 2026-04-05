from dataclasses import dataclass, field
from typing import List

@dataclass
class InvoiceData:
    # Mandatory Fields
    customer_name: str
    invoice_number: str
    invoice_date: str
    invoice_total: str
    columns: List[str]
    rows: List[List]
    column_widths: List[int]
    
    # Company Default Fields
    company_name: str = "Health Wave For Drug Trading"
    company_address: str = "Nasr City Towers, Tower 2, 7B Al Wafaa & Al Amal St., Nasr City, Cairo, Egypt"
    company_phone: str = "+20 122 528 3856"
    company_email_1: str = "Ahmed@health-wave.net"
    company_email_2: str = "Dr_ahmed_elomda@yahoo.com"
    logo_path: str = "assets/logo.png"
    
    # Optional Settings
    currency: str = "EGP"
    show_total_row: bool = True
    notes: str = ""
