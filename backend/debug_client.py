import requests
import os
import json

BASE_URL = "http://127.0.0.1:5000"

# Find a PDF file to use
upload_dir = r"e:\hammad\GradeHub-main\backend\uploads"
pdf_files = [f for f in os.listdir(upload_dir) if f.endswith(".pdf")]
if not pdf_files:
    print("No PDF files found in uploads directory!")
    exit(1)

pdf_path = os.path.join(upload_dir, pdf_files[0])
print(f"Testing with file: {pdf_path}")

try:
    # Step 1: Upload
    print("\n--- Step 1: Uploading PDF ---")
    with open(pdf_path, "rb") as f:
        files = {"pdf": f}
        res = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"Status Code: {res.status_code}")
    if res.status_code != 200:
        print(f"Reference Error: {res.text}")
        exit(1)
        
    data = res.json()
    print("Upload successful!")
    preview_token = data.get("preview_token")
    saved_filename = data.get("saved_filename")
    filepath = data.get("filepath")
    
    print(f"Preview Token: {preview_token}")
    
    # Step 2: Confirm Import
    print("\n--- Step 2: Confirming Import ---")
    payload = {
        "preview_token": preview_token,
        "filepath": filepath,
        "saved_filename": saved_filename,
        "department": "TestDept",
        "class": "TestClass",
        "semester": "TestSem"
    }
    
    headers = {"Content-Type": "application/json"}
    res = requests.post(f"{BASE_URL}/api/confirm_import", json=payload, headers=headers)
    
    print(f"Status Code: {res.status_code}")
    print("Raw Response Text:")
    print("-" * 50)
    print(res.text)
    print("-" * 50)
    
    try:
        json_resp = res.json()
        print("\nParsed JSON:")
        print(json.dumps(json_resp, indent=2))
    except Exception as e:
        print(f"\nFailed to parse JSON: {e}")

except Exception as e:
    print(f"\nAn error occurred: {e}")
