# api.py — REST API blueprint
import os, json
from flask import Blueprint, current_app, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from .utils.extractor import extract_metadata_from_pdf, extract_tables_from_pdf, extract_metadata_and_tables_from_pdf, normalize_headers, sanitize_identifier
from .utils.excel import save_df_to_excel
import pandas as pd
from .db import get_conn, create_db_if_not_exists
from datetime import datetime
from pathlib import Path

api_bp = Blueprint("api", __name__)

# Helper to check allowed file
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXT"]

@api_bp.before_request
def log_request_info():
    print(f"DEBUG: API Request: {request.method} {request.path}", flush=True)

@api_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200

@api_bp.route("/upload", methods=["POST"])
def upload_pdf():
    """
    Accepts multipart/form-data with field 'pdf' (file).
    Returns JSON:
      { ok: true, preview_token, metadata, raw_headers, canonical_cols, preview_rows, saved_filename, filepath }
    """
    if 'pdf' not in request.files:
        return jsonify({"ok": False, "error": "missing_file"}), 400
    file = request.files['pdf']
    if file.filename == "":
        return jsonify({"ok": False, "error": "empty_filename"}), 400
    if not allowed_file(file.filename):
        return jsonify({"ok": False, "error": "only_pdf_allowed"}), 400
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_name = f"{timestamp}_{filename}"
    saved_path = os.path.join(current_app.config["UPLOAD_FOLDER"], saved_name)
    file.save(saved_path)

    # extract metadata + tables in single pass for better performance
    metadata, tables = extract_metadata_and_tables_from_pdf(saved_path)
    if not tables:
        return jsonify({"ok": False, "error": "no_tables_detected"}), 400
    # pick largest table
    best = max(tables, key=lambda d: (d.shape[0], d.shape[1]))
    # determine header row
    header_candidate = best.iloc[0].astype(str).tolist() if not best.empty else []
    use_header = False
    if header_candidate:
        nonempty = sum(1 for x in header_candidate if x and x.lower() != "none")
        unique = len(set(header_candidate))
        if nonempty >= 1 and unique >= max(1, int(len(header_candidate)*0.5)):
            use_header = True
    if use_header:
        raw_headers = [str(h).strip() if h is not None else "" for h in header_candidate]
        data_df = best.iloc[1:].reset_index(drop=True).copy()
    else:
        raw_headers = [f"col{i}" for i in range(1, best.shape[1]+1)]
        data_df = best.copy()
    # normalize data frame - optimized using vectorized operations
    data_df.columns = range(data_df.shape[1])
    data_df = data_df.fillna("").astype(str)
    canonical_cols, mapping = normalize_headers(raw_headers)
    
    # Use vectorized operations for better performance
    # Ensure we have enough columns
    num_cols_needed = len(canonical_cols)
    if data_df.shape[1] < num_cols_needed:
        # Add empty columns if needed
        for i in range(data_df.shape[1], num_cols_needed):
            data_df[i] = ""
    elif data_df.shape[1] > num_cols_needed:
        # Trim excess columns
        data_df = data_df.iloc[:, :num_cols_needed]
    
    # Rename columns and apply string operations vectorized
    data_df.columns = canonical_cols
    # Apply strip to all string columns at once
    for col in canonical_cols:
        data_df[col] = data_df[col].str.strip()
    
    df_clean = data_df.copy()
    # add metadata columns at start
    df_clean.insert(0, "course_session", metadata.get("course_session",""))
    df_clean.insert(0, "semester", metadata.get("semester",""))
    df_clean.insert(0, "class", metadata.get("class",""))
    df_clean.insert(0, "department", metadata.get("department",""))

    # Save preview to CSV file (token)
    preview_token = f"preview_{timestamp}.csv"
    preview_path = os.path.join(current_app.config["UPLOAD_FOLDER"], preview_token)
    df_clean.to_csv(preview_path, index=False)
    preview_rows = df_clean.head(current_app.config["MAX_PREVIEW_ROWS"]).to_dict(orient="records")

    return jsonify({
        "ok": True,
        "preview_token": preview_token,
        "metadata": metadata,
        "raw_headers": raw_headers,
        "canonical_cols": canonical_cols,
        "mapping": mapping,
        "preview_rows": preview_rows,
        "filepath": saved_path,
        "saved_filename": saved_name
    }), 200

@api_bp.route("/confirm_import", methods=["POST"])
def confirm_import():
    """
    Body fields (form or json):
      preview_token, filepath, saved_filename,
      optionally 'rename_map' (JSON-string or dict) and metadata fields 'department','class','semester'
    Process: loads preview CSV, optionally renames columns, creates DB table and inserts rows, exports excel.
    """
    # Accept json or form
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    preview_token = data.get("preview_token")
    filepath = data.get("filepath")
    saved_filename = data.get("saved_filename")
    if not preview_token or not filepath:
        return jsonify({"ok": False, "error": "missing_data"}), 400
    preview_path = os.path.join(current_app.config["UPLOAD_FOLDER"], preview_token)
    # Load df
    df = pd.read_csv(preview_path, dtype=str).fillna("")

    # rename if provided
    rename_map = {}
    if "rename_map" in data:
        try:
            rm = data.get("rename_map")
            if isinstance(rm, str):
                rename_map = json.loads(rm)
            elif isinstance(rm, dict):
                rename_map = rm
        except Exception:
            rename_map = {}
    if rename_map:
        df = df.rename(columns=rename_map)

    # decide SQL types
    columns_sql = []
    def is_num(s):
        if s is None: return False
        s = str(s).strip().replace(',', '')
        if s == '': return False
        return re_full.match(s) is not None

    import re
    re_full = re.compile(r"-?\d+(\.\d+)?")
    for col in df.columns:
        if col in ("department","class","semester","course_session","student_name","student_id"):
            typ = "VARCHAR(500) NULL"
        else:
            # compute numeric ratio
            series = df[col].astype(str).tolist()
            num_count = sum(1 for v in series if is_num(v))
            total = max(1, len(series))
            typ = "FLOAT NULL" if (num_count/total) >= 0.6 else "VARCHAR(1000) NULL"
        columns_sql.append((col, typ))

    # create DB and table
    create_db_if_not_exists()
    table_name = f"student_marks_{sanitize_identifier(Path(filepath).stem)}"
    conn = None
    try:
        conn = get_conn()
    except Exception as e:
        return jsonify({"ok": False, "error": "db_connect_failed", "detail": str(e)}), 500
    try:
        cur = conn.cursor()
        # SQLite syntax (no database prefix, no ENGINE clause)
        cols_ddl = ", ".join(f"\"{c}\" {t}" for c,t in columns_sql)
        ddl = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" ({cols_ddl});"
        cur.execute(ddl)
        conn.commit()
        # insert rows
        cols = [c for c,_ in columns_sql]
        placeholders = ", ".join(["?"]*len(cols))  # SQLite uses ? instead of %s
        col_names = ", ".join(f'"{c}"' for c in cols)
        sql = f"INSERT INTO \"{table_name}\" ({col_names}) VALUES ({placeholders})"
        rows=[]
        # Use itertuples instead of iterrows for better performance
        coltype_map = dict(columns_sql)
        for r in df.itertuples(index=False):
            vals=[]
            for i, c in enumerate(cols):
                v = r[i]
                if v=="" or pd.isna(v):
                    vals.append(None)
                else:
                    coltype = coltype_map[c]
                    if "FLOAT" in coltype:
                        s = str(v).replace(',','').strip()
                        try: vals.append(float(s))
                        except: vals.append(None)
                    else:
                        vals.append(str(v))
            rows.append(tuple(vals))
        if rows:
            cur.executemany(sql, rows)
            conn.commit()
        cur.close()
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"ok": False, "error": "db_error", "detail": str(e)}), 500
    finally:
        if conn:
            conn.close()

    # export to excel
    try:
        # read back data with pandas
        conn2 = get_conn()
        df_export = pd.read_sql(f"SELECT * FROM \"{table_name}\";", conn2)
        conn2.close()
        
        # Use original PDF filename (without timestamp prefix and .pdf extension)
        original_filename = saved_filename if saved_filename else Path(filepath).name
        # Remove timestamp prefix if present (format: YYYYMMDDHHMMSS_originalname.pdf)
        if '_' in original_filename:
            parts = original_filename.split('_', 1)
            if len(parts) > 1 and parts[0].isdigit():
                original_filename = parts[1]
        
        # Replace .pdf extension with .xlsx
        excel_name = Path(original_filename).stem + ".xlsx"
        excel_path = os.path.join(current_app.config["EXPORT_FOLDER"], excel_name)
        
        # Handle duplicate filenames
        counter = 1
        while os.path.exists(excel_path):
            excel_name = f"{Path(original_filename).stem}_{counter}.xlsx"
            excel_path = os.path.join(current_app.config["EXPORT_FOLDER"], excel_name)
            counter += 1
        
        # Create title from metadata or filename
        dept = data.get("department") or ""
        cls = data.get("class") or ""
        sem = data.get("semester") or ""
        title_parts = [p for p in [dept, cls, sem] if p]
        title = " - ".join(title_parts) if title_parts else Path(original_filename).stem
        
        save_df_to_excel(df_export, excel_path, title=title)
    except Exception as e:
        return jsonify({"ok": False, "error": "export_error", "detail": str(e)}), 500

    # cleanup preview file
    try:
        os.remove(preview_path)
    except Exception:
        pass

    return jsonify({"ok": True, "excel_name": excel_name, "table_name": table_name, "original_pdf": original_filename}), 200

@api_bp.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    export_folder = current_app.config["EXPORT_FOLDER"]
    print(f"DEBUG: download_file request. Filename: {filename}", flush=True)
    print(f"DEBUG: Export folder: {export_folder} (Absolute: {os.path.abspath(export_folder)})", flush=True)
    full_path = os.path.join(export_folder, filename)
    print(f"DEBUG: Looking for file at: {full_path}, Exists: {os.path.exists(full_path)}", flush=True)
    try:
        return send_from_directory(export_folder, filename, as_attachment=True)
    except Exception as e:
        print(f"DEBUG: send_from_directory error: {e}", flush=True)
        return jsonify({"error": "download_failed", "detail": str(e)}), 404
