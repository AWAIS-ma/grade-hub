export default function PreviewTable({ data, onConfirm }) {
  const previewRows = data.preview_rows || [];
  const headers = data.canonical_cols || (previewRows.length > 0 ? Object.keys(previewRows[0]) : []);
  
  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-text-primary mb-2">Preview Extracted Data</h2>
        <p className="text-text-secondary">
          Review the extracted data before importing. Found {previewRows.length} preview records.
        </p>
        {data.metadata && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold mb-2">Metadata:</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              {data.metadata.department && <div><strong>Department:</strong> {data.metadata.department}</div>}
              {data.metadata.class && <div><strong>Class:</strong> {data.metadata.class}</div>}
              {data.metadata.semester && <div><strong>Semester:</strong> {data.metadata.semester}</div>}
              {data.metadata.course_session && <div><strong>Session:</strong> {data.metadata.course_session}</div>}
            </div>
          </div>
        )}
      </div>

      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-primary to-secondary">
              <tr>
                {headers.map((col) => (
                  <th 
                    key={col} 
                    className="px-6 py-4 text-left text-sm font-semibold text-white uppercase tracking-wider"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {previewRows.map((row, idx) => (
                <tr 
                  key={idx} 
                  className="hover:bg-gray-50 transition-colors duration-150"
                >
                  {headers.map((col) => (
                    <td 
                      key={col} 
                      className="px-6 py-4 text-sm text-text-primary whitespace-nowrap"
                    >
                      {row[col] || ''}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-8 flex justify-end space-x-4">
        <button
          onClick={() => window.location.reload()}
          className="btn-outline"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          className="btn-accent"
        >
          <div className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Confirm Import
          </div>
        </button>
      </div>
    </div>
  );
}