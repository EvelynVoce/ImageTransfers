import React, { useState } from "react";
import axios from "axios";

function App() {
  const [files, setFiles] = useState([]);
  const [serial, setSerial] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleFolderSelect = (e) => setFiles(Array.from(e.target.files));

  const handleUpload = async () => {
    if (!files.length) return alert("Select a folder first!");
    if (!serial) return alert("Enter a serial number!");
    setUploading(true);

    try {
      const checkResponse = await axios.get(
        `http://127.0.0.1:8000/check_exists/${serial}`
      );

      if (checkResponse.data.exists) {
        alert("A folder for this serial already exists on the server.");
        setUploading(false);
        return;
      }

      const BATCH_SIZE = 50;
      const DELAY_MS = 500;

      const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

      for (let i = 0; i < files.length; i += BATCH_SIZE) {
        const batch = files.slice(i, i + BATCH_SIZE);
        const formData = new FormData();
        batch.forEach((file) => formData.append("files", file));
        formData.append("serial_number", serial); // send serial number

        await axios.post("http://127.0.0.1:8000/upload_batch/", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        // This performs the delay
        await sleep(DELAY_MS);
      }

      alert("Upload complete!");
    } catch (err) {
      console.error(err);
      alert("Upload failed!");
    } finally {
      setUploading(false);
    }

    // Check if all images are uploaded
    const checkResponse = await axios.get(
      `http://127.0.0.1:8000/check_uploads/${serial}`
    );
    
    alert(checkResponse.data.status);

  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>📁 Upload Folder of Images with Serial Number</h1>
      <input
        type="text"
        placeholder="Enter Serial Number"
        value={serial}
        onChange={(e) => setSerial(e.target.value)}
      />
      <br/><br />
      <input type="file" webkitdirectory="true" directory multiple onChange={handleFolderSelect} />
      <br/><br />
      <button onClick={handleUpload} disabled={!files.length || !serial || uploading}>
        {uploading ? "Uploading..." : "Upload Folder"}
      </button>
    </div>
  );
}

export default App;

