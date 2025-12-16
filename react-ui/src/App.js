import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import Chat from './components/Chat';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);

  const handleUpload = (files) => {
    setUploadedFiles(prev => [...prev, ...files]);
  };

  return (
    <div className="App">
      <ToastContainer />
      <h1>Multi-Language RAG Chatbot</h1>
      <FileUpload onUpload={handleUpload} />
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h3>Uploaded Files:</h3>
          <ul>
            {uploadedFiles.map((file, idx) => (
              <li key={idx}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}
      <Chat history={chatHistory} onNewMessage={setChatHistory} />
    </div>
  );
}

export default App;
