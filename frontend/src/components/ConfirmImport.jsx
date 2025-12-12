import { useState } from "react";
import { importGrades } from "../api";

export default function ConfirmImport({ onConfirm, onCancel, fileData }) {
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    if (!fileData) return;
    setLoading(true);
    try {
      const res = await importGrades({
        preview_token: fileData.preview_token,
        filepath: fileData.filepath,
        saved_filename: fileData.saved_filename,
        department: fileData.metadata?.department || "",
        class: fileData.metadata?.class || "",
        semester: fileData.metadata?.semester || "",
      });
      setLoading(false);
      console.log("Import response:", res); // Debug log
      setLoading(false);
      if (res.ok) {
        onConfirm(res);
      } else {
        alert(`Import Error: ${res.error || "Unknown server error"}`);
      }
    } catch (error) {
      setLoading(false);
      console.error("Import execution failed:", error);
      alert(`System Error: ${error.message || "Network or parsing failed"}`);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card max-w-md w-full mx-auto transform transition-all duration-200 scale-100">
        <div className="p-6 text-center">
          <div className="w-16 h-16 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>

          <h2 className="text-xl font-bold text-text-primary mb-2">Confirm Import</h2>
          <p className="text-text-secondary mb-6">
            Are you sure you want to import these grades into the system? This action cannot be undone.
          </p>

          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              disabled={loading}
              className="flex-1 btn-outline"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading}
              className="flex-1 btn-secondary"
            >
              {loading ? "Importing..." : "Confirm Import"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}