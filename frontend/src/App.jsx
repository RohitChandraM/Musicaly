import { useState, useEffect, useRef } from "react";
import UploadArea from "./components/UploadArea";
import PresetSelector from "./components/PresetSelector";
import StrengthSlider from "./components/StrengthSlider";
import InputTypeSelector from "./components/InputTypeSelector";
import AudioPlayer from "./components/AudioPlayer";
import ProgressBar from "./components/ProgressBar";
import DownloadButtons from "./components/DownloadButtons";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

export default function App() {
  const [file, setFile] = useState(null);
  const [fileId, setFileId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const [inputType, setInputType] = useState("auto");
  const [preset, setPreset] = useState("natural");
  const [strength, setStrength] = useState(0.75);

  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [processing, setProcessing] = useState(false);

  const [processedFileId, setProcessedFileId] = useState(null);
  const [processedUrl, setProcessedUrl] = useState(null);

  const pollRef = useRef(null);

  useEffect(() => {
    return () => {
      if (processedUrl) URL.revokeObjectURL(processedUrl);
    };
  }, [processedUrl]);

  useEffect(() => {
    if (!jobId) return;

    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/status/${jobId}`);
        if (!res.ok) return;
        const data = await res.json();
        setJobStatus(data);

        if (data.status === "done") {
          clearInterval(pollRef.current);
          setProcessing(false);
          setProcessedFileId(fileId);
          const audioRes = await fetch(`${API}/download/${fileId}?fmt=wav`);
          if (audioRes.ok) {
            const blob = await audioRes.blob();
            setProcessedUrl(URL.createObjectURL(blob));
          }
        } else if (data.status === "error") {
          clearInterval(pollRef.current);
          setProcessing(false);
        }
      } catch {
        // ignore poll errors
      }
    }, 1500);

    return () => clearInterval(pollRef.current);
  }, [jobId, fileId]);

  const handleFileSelected = async (selectedFile) => {
    setFile(selectedFile);
    setFileId(null);
    setUploadError(null);
    setJobStatus(null);
    setJobId(null);
    setProcessedFileId(null);
    setProcessedUrl(null);
    setUploading(true);

    try {
      const form = new FormData();
      form.append("file", selectedFile);
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setFileId(data.file_id);
    } catch (err) {
      setUploadError(err.message || "Upload failed. Please try again.");
      setFile(null);
    } finally {
      setUploading(false);
    }
  };

  const handleProcess = async () => {
    if (!fileId) return;
    setProcessing(true);
    setJobStatus({ status: "queued", progress: 0 });
    setProcessedFileId(null);
    setProcessedUrl(null);

    try {
      const res = await fetch(`${API}/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_id: fileId, input_type: inputType, preset, strength }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to start processing");
      setJobId(data.job_id);
    } catch (err) {
      setJobStatus({ status: "error", progress: 0, error: err.message });
      setProcessing(false);
    }
  };

  const handleReset = () => {
    if (pollRef.current) clearInterval(pollRef.current);
    setFile(null);
    setFileId(null);
    setUploading(false);
    setUploadError(null);
    setJobId(null);
    setJobStatus(null);
    setProcessing(false);
    setProcessedFileId(null);
    if (processedUrl) URL.revokeObjectURL(processedUrl);
    setProcessedUrl(null);
  };

  const busy = uploading || processing;
  const done = jobStatus?.status === "done";

  return (
    <div className="min-h-screen bg-[#0d0d0f] text-white font-sans">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-purple-700/10 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-indigo-700/10 blur-3xl" />
      </div>

      <div className="relative z-10 max-w-2xl mx-auto px-4 py-12">
        <div className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/15 border border-purple-500/30 text-purple-300 text-xs font-semibold uppercase tracking-widest mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" />
            Vocal Humanizer AI
          </div>
          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-3 bg-gradient-to-br from-white via-white/90 to-white/50 bg-clip-text text-transparent">
            Make AI Vocals Sound Human
          </h1>
          <p className="text-white/40 text-base">
            One-click polish for AI vocals.
          </p>
        </div>

        <div className="bg-white/[0.04] border border-white/10 rounded-2xl p-6 sm:p-8 space-y-7 backdrop-blur-sm">

          {!file ? (
            <UploadArea onFileSelected={handleFileSelected} disabled={busy} />
          ) : (
            <div className="flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-purple-600/20 flex items-center justify-center shrink-0">
                  <svg className="w-4 h-4 text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
                  </svg>
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-white truncate max-w-[180px] sm:max-w-xs">
                    {file.name}
                  </p>
                  <p className="text-xs text-white/40">{formatBytes(file.size)}</p>
                </div>
              </div>
              {!busy && (
                <button
                  onClick={handleReset}
                  className="ml-3 text-white/30 hover:text-white/70 transition-colors"
                  title="Remove file"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          )}

          {uploadError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 text-red-400 text-sm">
              {uploadError}
            </div>
          )}

          {uploading && (
            <div className="flex items-center gap-2 text-white/50 text-sm">
              <svg className="w-4 h-4 animate-spin text-purple-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Uploading…
            </div>
          )}

          {fileId && !done && (
            <>
              <div className="border-t border-white/8" />
              <InputTypeSelector value={inputType} onChange={setInputType} disabled={busy} />
              <PresetSelector value={preset} onChange={setPreset} disabled={busy} />
              <StrengthSlider value={strength} onChange={setStrength} disabled={busy} />

              <button
                onClick={handleProcess}
                disabled={busy}
                className="w-full py-4 rounded-xl font-bold text-base transition-all duration-200
                  bg-gradient-to-r from-purple-600 to-indigo-600
                  hover:from-purple-500 hover:to-indigo-500
                  disabled:opacity-50 disabled:cursor-not-allowed
                  shadow-lg shadow-purple-900/30"
              >
                {processing ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Humanizing…
                  </span>
                ) : (
                  "✦  Humanize Vocal"
                )}
              </button>
            </>
          )}

          {jobStatus && (
            <ProgressBar
              status={jobStatus.status}
              progress={jobStatus.progress}
              error={jobStatus.error}
              warning={jobStatus.warning}
            />
          )}

          {done && (
            <div className="space-y-6">
              <div className="border-t border-white/8" />
              <AudioPlayer originalFile={file} processedUrl={processedUrl} />
              <DownloadButtons fileId={processedFileId} disabled={false} />

              <button
                onClick={handleReset}
                className="w-full py-3 rounded-xl border border-white/15 text-white/50 hover:text-white/80 hover:border-white/30 text-sm font-medium transition-all"
              >
                Process Another File
              </button>
            </div>
          )}
        </div>

        {!file && (
          <div className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { icon: "🎛️", label: "Smart EQ", desc: "Warms body, removes mud" },
              { icon: "📉", label: "AI Harshness", desc: "Dynamic 2–5 kHz control" },
              { icon: "🔇", label: "De-Esser", desc: "Tames sharp S sounds" },
              { icon: "✨", label: "Warmth", desc: "Subtle saturation & room" },
            ].map((feat) => (
              <div key={feat.label} className="bg-white/[0.03] border border-white/8 rounded-xl p-4 text-center">
                <span className="text-2xl block mb-1">{feat.icon}</span>
                <p className="text-xs font-semibold text-white/70">{feat.label}</p>
                <p className="text-xs text-white/35 mt-0.5">{feat.desc}</p>
              </div>
            ))}
          </div>
        )}

        <p className="text-center text-white/20 text-xs mt-10">
          Vocal Humanizer AI · Open-source DSP · No AI models required
        </p>
      </div>
    </div>
  );
}
