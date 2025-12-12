import { getDownloadUrl } from "../api";

export default function Result({ resultData }) {
  const excelName = resultData?.excel_name;
  const downloadUrl = excelName ? getDownloadUrl(excelName) : null;

  return (
    <div className="text-center py-8">
      <div className="w-20 h-20 bg-secondary/20 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg className="w-10 h-10 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <h2 className="text-3xl font-bold text-text-primary mb-3">Import Successful!</h2>
      <p className="text-lg text-text-secondary mb-4 max-w-md mx-auto">
        The academic data has been successfully imported into the system and exported to Excel.
      </p>

      {excelName && (
        <p className="text-sm text-text-secondary mb-8">
          Excel file: <span className="font-semibold text-primary">{excelName}</span>
        </p>
      )}

      <div className="flex flex-col items-center space-y-4 mb-8">
        {downloadUrl && (
          <a
            href={downloadUrl}
            download={excelName}
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary to-secondary text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download Excel Report
          </a>
        )}
      </div>

      <div className="flex justify-center space-x-4">
        <button
          onClick={() => window.location.reload()}
          className="btn-primary"
        >
          Import Another File
        </button>
        <button
          onClick={() => console.log('View data')}
          className="btn-outline"
        >
          View Data
        </button>
      </div>
    </div>
  );
}