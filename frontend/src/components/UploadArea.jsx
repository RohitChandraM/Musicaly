import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

const ACCEPTED = {
  "audio/wav": [".wav"],
  "audio/mpeg": [".mp3"],
  "audio/flac": [".flac"],
  "audio/x-m4a": [".m4a"],
  "audio/mp4": [".m4a"],
  "audio/aac": [".aac"],
};

export default function UploadArea({ onFileSelected, disabled }) {
  const [dragOver, setDragOver] = useState(false);
  const onDrop = useCallback((accepted) => { if (accepted.length > 0) onFileSelected(accepted[0]); setDragOver(false); }, [onFileSelected]);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: ACCEPTED, maxFiles: 1, disabled,
    onDragEnter: () => setDragOver(true), onDragLeave: () => setDragOver(false),
  });
  const border = isDragActive || dragOver ? "border-purple-400 bg-purple-500/10" : "border-white/20 hover:border-purple-500/60 hover:bg-white/5";
  return (
    <div {...getRootProps()} className={`cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-200 p-10 text-center ${border} ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}>
      <input {...getInputProps()} />
      <div className="flex justify-center mb-4">
        <div className="w-16 h-16 rounded-full bg-purple-600/20 flex items-center justify-center">
          <svg className="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        </div>
      </div>
      {isDragActive ? (
        <p className="text-purple-300 text-lg font-medium">Drop it here…</p>
      ) : (
        <>
          <p className="text-white text-lg font-semibold mb-1">Drop your vocal or song here</p>
          <p className="text-white/50 text-sm mb-4">or click to browse your files</p>
          <div className="flex justify-center gap-2 flex-wrap">
            {["WAV", "MP3", "FLAC", "M4A"].map((fmt) => (
              <span key={fmt} className="px-2.5 py-0.5 text-xs rounded-full bg-white/10 text-white/60 font-mono">{fmt}</span>
            ))}
          </div>
          <p className="text-white/30 text-xs mt-3">Max 200 MB</p>
        </>
      )}
    </div>
  );
}
