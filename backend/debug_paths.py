from app import create_app
import os

# Create app context to load config
app = create_app()
with app.app_context():
    folder = app.config["EXPORT_FOLDER"]
    print(f"CWD: {os.getcwd()}")
    print(f"Export Folder Config: {folder}")
    print(f"Abs Export Folder: {os.path.abspath(folder)}")
    
    # Check for ANY file in that folder
    if os.path.exists(folder):
        files = os.listdir(folder)
        print(f"Files in folder: {files}")
        
        expected_file = "20251019120753_student_marks_report_1.xlsx"
        full_path = os.path.join(folder, expected_file)
        print(f"Looking for: {full_path}")
        print(f"File Exists? {os.path.exists(full_path)}")
    else:
        print("Export folder does not exist!")
