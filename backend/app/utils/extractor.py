# extractor.py — pdf metadata and table extraction logic using pdfplumber + pandas
import re
import pandas as pd
import pdfplumber
from flask import current_app

# sanitize helper
def sanitize_identifier(name: str) -> str:
    if not name:
        return "col"
    safe = "".join(c if (c.isalnum() or c == "_") else "_" for c in name.strip())
    if safe and safe[0].isdigit():
        safe = "c_" + safe
    return safe[:64] if safe else "col"

def extract_metadata_from_pdf(pdf_path: str, pages_to_scan: int = None):
    if pages_to_scan is None:
        pages_to_scan = current_app.config["PAGES_TO_SCAN_FOR_METADATA"]
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for p in pdf.pages[:pages_to_scan]:
                text += "\n" + (p.extract_text() or "")
    except Exception:
        return {"department":"", "class":"", "semester":"", "course_session":""}
    s = re.sub(r'\s+', ' ', text).strip()
    patterns = {
        "department": [r"(?:department\s*[:\-]\s*)([A-Za-z0-9&\-,\s\.]+)", r"(?:dept\s*[:\-]\s*)([A-Za-z0-9&\-,\s\.]+)"],
        "class": [r"(?:class\s*[:\-]\s*)([A-Za-z0-9\-\s\/&]+)", r"(?:section\s*[:\-]\s*)([A-Za-z0-9\-\s\/&]+)"],
        "semester": [r"(?:semester\s*[:\-]\s*)([A-Za-z0-9\-\s]+)", r"(?:sem\s*[:\-]\s*)([A-Za-z0-9\-\s]+)"],
        "course_session":[r"(?:session\s*[:\-]\s*)([A-Za-z0-9\-\s\/]+)", r"(?:course session\s*[:\-]\s*)([A-Za-z0-9\-\s\/]+)"]
    }
    res = {"department":"", "class":"", "semester":"", "course_session":""}
    for key, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, s, flags=re.IGNORECASE)
            if m:
                val = m.group(1).strip()
                val = re.sub(r'[\s\.:;,\-\/]+$', '', val).strip()
                res[key] = val
                break
    return res

# extract tables as list of DataFrames
def extract_tables_from_pdf(pdf_path: str, max_pages: int = None):
    """
    Extract tables from PDF with optional page limit for performance.
    If max_pages is None, uses MAX_PAGES_FOR_TABLE_EXTRACTION from config or defaults to 20.
    """
    if max_pages is None:
        max_pages = getattr(current_app.config, "MAX_PAGES_FOR_TABLE_EXTRACTION", 20)
    tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Limit pages processed for performance
            pages_to_process = pdf.pages[:max_pages] if len(pdf.pages) > max_pages else pdf.pages
            for page in pages_to_process:
                try:
                    tlist = page.extract_tables()
                except Exception:
                    tlist = []
                for t in tlist:
                    if t:  # Check if table is not empty
                        df = pd.DataFrame(t)
                        df = df.dropna(how="all").reset_index(drop=True)
                        if not df.empty:
                            tables.append(df)
    except Exception:
        pass
    return tables

# Combined extraction function for better performance (opens PDF only once)
def extract_metadata_and_tables_from_pdf(pdf_path: str, pages_to_scan_metadata: int = None, max_pages_for_tables: int = None):
    """
    Extract both metadata and tables in a single PDF open operation for better performance.
    Returns tuple: (metadata_dict, tables_list)
    """
    if pages_to_scan_metadata is None:
        pages_to_scan_metadata = current_app.config["PAGES_TO_SCAN_FOR_METADATA"]
    if max_pages_for_tables is None:
        max_pages_for_tables = getattr(current_app.config, "MAX_PAGES_FOR_TABLE_EXTRACTION", 20)
    
    metadata = {"department":"", "class":"", "semester":"", "course_session":""}
    tables = []
    text = ""
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata from first few pages
            for p in pdf.pages[:pages_to_scan_metadata]:
                text += "\n" + (p.extract_text() or "")
            
            # Extract tables from limited pages
            pages_to_process = pdf.pages[:max_pages_for_tables] if len(pdf.pages) > max_pages_for_tables else pdf.pages
            for page in pages_to_process:
                try:
                    tlist = page.extract_tables()
                except Exception:
                    tlist = []
                for t in tlist:
                    if t:  # Check if table is not empty
                        df = pd.DataFrame(t)
                        df = df.dropna(how="all").reset_index(drop=True)
                        if not df.empty:
                            tables.append(df)
    except Exception as e:
        return metadata, tables
    
    # Process metadata
    if text:
        s = re.sub(r'\s+', ' ', text).strip()
        patterns = {
            "department": [r"(?:department\s*[:\-]\s*)([A-Za-z0-9&\-,\s\.]+)", r"(?:dept\s*[:\-]\s*)([A-Za-z0-9&\-,\s\.]+)"],
            "class": [r"(?:class\s*[:\-]\s*)([A-Za-z0-9\-\s\/&]+)", r"(?:section\s*[:\-]\s*)([A-Za-z0-9\-\s\/&]+)"],
            "semester": [r"(?:semester\s*[:\-]\s*)([A-Za-z0-9\-\s]+)", r"(?:sem\s*[:\-]\s*)([A-Za-z0-9\-\s]+)"],
            "course_session":[r"(?:session\s*[:\-]\s*)([A-Za-z0-9\-\s\/]+)", r"(?:course session\s*[:\-]\s*)([A-Za-z0-9\-\s\/]+)"]
        }
        for key, pats in patterns.items():
            for pat in pats:
                m = re.search(pat, s, flags=re.IGNORECASE)
                if m:
                    val = m.group(1).strip()
                    val = re.sub(r'[\s\.:;,\-\/]+$', '', val).strip()
                    metadata[key] = val
                    break
    
    return metadata, tables

# normalizing headers map (simple)
HEADER_MAP = {
    "student_name": [r"student\s*name", r"name", r"candidate\s*name"],
    "student_id": [r"reg(istration)?\s*no", r"roll\s*no", r"student\s*id"],
    "internal_marks": [r"internal", r"int(er?nals)?", r"internal\s*marks"],
    "mid_marks": [r"mid", r"mid-?term", r"midterm"],
    "final_marks": [r"final", r"theory", r"final\s*marks"],
    "practical_marks": [r"practical", r"lab", r"practical\s*marks"],
    "total_marks": [r"total", r"obtained", r"grand\s*total"]
}

def normalize_headers(raw_headers):
    canonical, mapping = [], {}
    for raw in raw_headers:
        cell = str(raw).strip()
        lowered = re.sub(r'[^a-z0-9 ]', ' ', cell.lower())
        lowered = re.sub(r'\s+', ' ', lowered).strip()
        matched = None
        for canon, patterns in HEADER_MAP.items():
            for pat in patterns:
                if re.search(r"\b" + pat + r"\b", lowered):
                    matched = canon
                    break
            if matched: break
        if not matched:
            matched = sanitize_identifier(lowered.replace(" ", "_"))
        base = matched
        idx = 1
        while matched in canonical:
            idx += 1
            matched = f"{base}_{idx}"
        canonical.append(matched)
        mapping[cell] = matched
    return canonical, mapping
