import React, { useRef } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const FileUpload = ({ onUpload }) => {
  const fileInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    try {
      const response = await axios.post('/api/upload', formData);
      toast.success(`Uploaded ${response.data.indexed} chunks from ${files.length} file(s)!`);
      onUpload(files);
    } catch (error) {
      toast.error('Upload failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="upload-zone">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        multiple
        accept=".pdf,.docx,.txt,.md"
        style={{ display: 'none' }}
      />
      <button onClick={handleButtonClick} style={{
        padding: '10px 20px',
        backgroundColor: '#007bff',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '0.9em'
      }}>
        Upload Documents
      </button>
      <p style={{ marginTop: '10px', fontSize: '0.8em' }}>Select PDF, DOCX, TXT, or MD files</p>
    </div>
  );
};

export default FileUpload;