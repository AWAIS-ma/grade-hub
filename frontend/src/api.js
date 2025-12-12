const BASE_URL = "http://127.0.0.1:5000";

export async function uploadFile(file) {
  const formData = new FormData();
  formData.append("pdf", file); // Backend expects "pdf" field name

  const res = await fetch(`${BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function importGrades(data) {
  const res = await fetch(`${BASE_URL}/api/confirm_import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export function getDownloadUrl(filename) {
  return `${BASE_URL}/api/download/${filename}`;
}
