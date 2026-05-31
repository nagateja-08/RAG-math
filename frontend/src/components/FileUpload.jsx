import React, { useRef } from 'react';
import { Paperclip, X } from 'lucide-react';

const FileUpload = ({ onUpload, disabled }) => {
  const inputRef = useRef(null);

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
      inputRef.current.value = '';
    }
  };

  return (
    <>
      <input
        ref={inputRef}
        type="file"
        id="file-upload"
        accept=".pdf,.txt"
        className="hidden-file-input"
        onChange={handleChange}
        disabled={disabled}
      />
      <button
        type="button"
        className="icon-btn"
        onClick={() => inputRef.current?.click()}
        disabled={disabled}
        title="Upload PDF or TXT"
      >
        <Paperclip size={20} />
      </button>
    </>
  );
};

export default FileUpload;
