import { useState } from 'react';
import UploadForm from './components/UploadForm';
import PreviewTable from './components/PreviewTable';
import ConfirmImport from './components/ConfirmImport';
import Result from './components/Result';

function App() {
  const [fileData, setFileData] = useState(null);
  const [imported, setImported] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [resultData, setResultData] = useState(null);

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-primary to-secondary rounded-xl flex items-center justify-center mr-3">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              GradeHub
            </h1>
          </div>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Automate academic data extraction from PDF documents and manage evaluations efficiently
          </p>
        </header>

        {/* Main Content */}
        <main className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="card p-6 sticky top-8">
                <h2 className="text-xl font-semibold text-text-primary mb-6">Import Process</h2>
                <div className="space-y-4">
                  {/* Step 1 */}
                  <div className={`flex items-center p-3 rounded-lg ${!fileData ? 'bg-primary/10 border border-primary/50' : 'bg-gray-50'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${!fileData ? 'bg-primary text-white' : 'bg-gray-300 text-gray-600'}`}>1</div>
                    <span className={`font-medium ${!fileData ? 'text-primary' : 'text-gray-600'}`}>Upload PDF</span>
                  </div>

                  {/* Step 2 */}
                  <div className={`flex items-center p-3 rounded-lg ${fileData && !imported ? 'bg-secondary/10 border border-secondary/50' : 'bg-gray-50'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${fileData && !imported ? 'bg-secondary text-white' : 'bg-gray-300 text-gray-600'}`}>2</div>
                    <span className={`font-medium ${fileData && !imported ? 'text-secondary' : 'text-gray-600'}`}>Preview Data</span>
                  </div>

                  {/* Step 3 */}
                  <div className={`flex items-center p-3 rounded-lg ${imported ? 'bg-accent/10 border border-accent/50' : 'bg-gray-50'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${imported ? 'bg-accent text-white' : 'bg-gray-300 text-gray-600'}`}>3</div>
                    <span className={`font-medium ${imported ? 'text-accent' : 'text-gray-600'}`}>Complete</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="lg:col-span-2">
              <div className="card p-8">
                {!fileData && (
                  <div className="text-center">
                    <h2 className="text-2xl font-bold text-text-primary mb-4">Upload Academic Document</h2>
                    <p className="text-text-secondary mb-8">Select a PDF file containing student grades and evaluation data</p>
                    <UploadForm setFileData={setFileData} />
                  </div>
                )}

                {fileData && !imported && !showConfirm && (
                  <PreviewTable data={fileData} onConfirm={() => setShowConfirm(true)} />
                )}

                {showConfirm && (
                  <ConfirmImport
                    fileData={fileData}
                    onCancel={() => setShowConfirm(false)}
                    onConfirm={(result) => {
                      setResultData(result);
                      setImported(true);
                      setShowConfirm(false);
                    }}
                  />
                )}

                {imported && <Result resultData={resultData} />}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
