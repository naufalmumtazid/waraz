"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Video,
  Upload,
  RefreshCw,
  FolderPlus,
  Play,
  FileCheck2,
  Trash2,
  ExternalLink,
  Info,
  CheckCircle2,
  AlertTriangle,
  SlidersHorizontal,
} from "lucide-react";
import { videoApi, ArchiveRecord, DetectionResult } from "@/services/api";

export default function VideoRecycleTrackerPage() {
  const [activeTab, setActiveTab] = useState<"analisis" | "arsip">("analisis");
  const [archives, setArchives] = useState<ArchiveRecord[]>([]);
  const [loadingArchives, setLoadingArchives] = useState(false);
  const [systemMode, setSystemMode] = useState<"demo" | "prod">("demo");

  // Analysis state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(
    null
  );
  const [detectError, setDetectError] = useState<string | null>(null);

  // Archive registration state
  const [regFile, setRegFile] = useState<File | null>(null);
  const [regTitle, setRegTitle] = useState("");
  const [regDate, setRegDate] = useState("");
  const [regSource, setRegSource] = useState("");
  const [regUrl, setRegUrl] = useState("");
  const [registering, setRegistering] = useState(false);
  const [regMessage, setRegMessage] = useState<{
    type: "success" | "error" | "warning";
    text: string;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const regFileInputRef = useRef<HTMLInputElement>(null);

  // Load archives
  const fetchArchives = async () => {
    setLoadingArchives(true);
    try {
      const data = await videoApi.listArchives();
      setArchives(data);
    } catch (err: unknown) {
      console.error("Gagal load arsip:", err);
    } finally {
      setLoadingArchives(false);
    }
  };

  useEffect(() => {
    fetchArchives();
  }, []);

  // Handle detection submit
  const handleDetect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setDetecting(true);
    setDetectError(null);
    setDetectionResult(null);

    try {
      const res = await videoApi.detectVideo(selectedFile);
      setDetectionResult(res);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Terjadi kesalahan.";
      setDetectError(msg);
    } finally {
      setDetecting(false);
    }
  };

  // Reset analysis
  const handleResetAnalysis = () => {
    setSelectedFile(null);
    setDetectionResult(null);
    setDetectError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // Handle archive register submit
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!regFile || !regTitle.trim()) {
      setRegMessage({
        type: "error",
        text: "Berkas video dan judul wajib diisi.",
      });
      return;
    }

    setRegistering(true);
    setRegMessage(null);

    try {
      const res = await videoApi.registerArchive({
        file: regFile,
        judul: regTitle.trim(),
        tanggal_asli: regDate || undefined,
        sumber: regSource.trim() || undefined,
        tautan: regUrl.trim() || undefined,
      });

      setRegMessage({
        type: "success",
        text: `Berhasil mendaftarkan video "${res.judul}" ke arsip dengan ${res.total_frame || 0} frame keyframe hash!`,
      });

      // Reset form
      setRegFile(null);
      setRegTitle("");
      setRegDate("");
      setRegSource("");
      setRegUrl("");
      if (regFileInputRef.current) regFileInputRef.current.value = "";
      fetchArchives();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal mendaftarkan arsip.";
      setRegMessage({ type: "error", text: msg });
    } finally {
      setRegistering(false);
    }
  };

  // Handle seed demo
  const handleSeedDemo = async () => {
    try {
      setLoadingArchives(true);
      await videoApi.seedDemo();
      await fetchArchives();
      alert("Basis video demo berhasil disiapkan!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal seed demo.";
      alert(msg);
    } finally {
      setLoadingArchives(false);
    }
  };

  // Handle delete archive
  const handleDeleteArchive = async (id: string, title: string) => {
    if (!confirm(`Hapus video "${title}" dari basis arsip?`)) return;
    try {
      await videoApi.deleteArchive(id);
      await fetchArchives();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal hapus arsip.";
      alert(msg);
    }
  };

  return (
    <div className="min-h-screen text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-red-900/40 bg-coal-900/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-400 shadow-lg shadow-red-600/25">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-red-400 text-lg">
                  WARAZ
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20 font-mono">
                  F2
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Pelacak Video Daur Ulang & Perceptual Hash
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center bg-coal-800/80 p-1 rounded-lg border border-coal-700 text-xs">
              <button
                type="button"
                onClick={() => setSystemMode("demo")}
                className={`px-3 py-1.5 rounded-md transition font-medium ${
                  systemMode === "demo"
                    ? "bg-red-600 text-white shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Mode Demo (Lomba)
              </button>
              <button
                type="button"
                onClick={() => setSystemMode("prod")}
                className={`px-3 py-1.5 rounded-md transition font-medium ${
                  systemMode === "prod"
                    ? "bg-emerald-600 text-white shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                Mode Produksi
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Body */}
      <div className="max-w-7xl mx-auto px-4 py-8 flex-1 grid grid-cols-1 lg:grid-cols-4 gap-8 w-full">
        {/* Left Sidebar: Archive Management */}
        <aside className="lg:col-span-1 space-y-6">
          <div className="bg-coal-900 border border-coal-800 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4 text-red-400" />
                Status Sistem
              </h2>
              <span
                className={`text-[11px] px-2 py-0.5 rounded font-mono ${
                  systemMode === "demo"
                    ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                    : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                }`}
              >
                {systemMode === "demo" ? "SIMULASI" : "PROD ACTIVE"}
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              {systemMode === "demo"
                ? "🏷️ Mode evaluasi aktif. Sesuai prinsip etika WARAZ, arsip video dienkapsulasi hanya dalam bentuk perceptual hash (pHash & dHash)."
                : "🏢 Mode produksi terhubung langsung ke basis data PostgreSQL Neon. Menolak duplikasi berkas fisik."}
            </p>

            {systemMode === "demo" && (
              <button
                type="button"
                onClick={handleSeedDemo}
                disabled={loadingArchives}
                className="w-full py-2.5 px-3 rounded-xl bg-red-600/10 hover:bg-red-600/20 border border-red-500/30 text-red-400 text-xs font-medium flex items-center justify-center gap-2 transition"
              >
                <RefreshCw
                  className={`w-3.5 h-3.5 ${loadingArchives ? "animate-spin" : ""}`}
                />
                Inisialisasi / Seed Arsip Demo
              </button>
            )}
          </div>

          {/* Stored Archives List */}
          <div className="bg-coal-900 border border-coal-800 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-sm text-slate-200 flex items-center gap-2">
                <FileCheck2 className="w-4 h-4 text-emerald-400" />
                Arsip Tersimpan
              </h3>
              <span className="text-xs bg-coal-800 px-2 py-0.5 rounded-full text-slate-300 font-mono">
                {archives.length}
              </span>
            </div>

            <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
              {archives.length === 0 ? (
                <div className="text-center py-8 text-slate-500 text-xs">
                  Belum ada video di arsip.
                </div>
              ) : (
                archives.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 bg-coal-800/40 border border-coal-700/50 rounded-xl space-y-2 hover:border-coal-600 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-xs font-medium text-slate-200 line-clamp-2">
                        {item.judul}
                      </p>
                      <button
                        type="button"
                        onClick={() => handleDeleteArchive(item.id, item.judul)}
                        className="text-slate-500 hover:text-red-400 p-1"
                        title="Hapus dari arsip"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="text-[11px] text-slate-400 space-y-0.5">
                      <p>
                        📅 Tanggal:{" "}
                        <span className="text-slate-300">
                          {item.tanggal_asli || "-"}
                        </span>
                      </p>
                      <p>
                        🏢 Sumber:{" "}
                        <span className="text-slate-300">
                          {item.sumber || "-"}
                        </span>
                      </p>
                      <p>
                        🎞️ Hash:{" "}
                        <span className="text-slate-300 font-mono">
                          {item.total_frame || 0} frames
                        </span>
                      </p>
                    </div>

                    {item.thumbnail_filename && (
                      <div className="rounded-lg overflow-hidden border border-coal-700 mt-2 bg-black">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={videoApi.getThumbnailUrl(
                            "arsip",
                            item.thumbnail_filename
                          )}
                          alt={item.judul}
                          className="w-full h-24 object-cover"
                        />
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Center / Right Content: Tabs */}
        <main className="lg:col-span-3 space-y-6">
          {/* Tabs bar */}
          <div className="flex border-b border-coal-800 gap-4">
            <button
              type="button"
              onClick={() => setActiveTab("analisis")}
              className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition ${
                activeTab === "analisis"
                  ? "border-red-500 text-red-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Play className="w-4 h-4" />
              1. Analisis Video Uji
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("arsip")}
              className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition ${
                activeTab === "arsip"
                  ? "border-red-500 text-red-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <FolderPlus className="w-4 h-4" />
              2. Daftarkan Video Baru ke Arsip
            </button>
          </div>

          {/* TAB 1: Analisis Video Uji */}
          {activeTab === "analisis" && (
            <div className="space-y-6">
              <div className="bg-coal-900 border border-coal-800 rounded-2xl p-6 shadow-sm">
                <h3 className="font-semibold text-base text-slate-100 mb-1">
                  Unggah Berkas Video yang Ingin Diperiksa
                </h3>
                <p className="text-xs text-slate-400 mb-6">
                  Sistem mengekstrak keyframe berkala, menghitung dual-hash (pHash + dHash),
                  dan mencari pola kemunculan berurutan di dalam basis arsip.
                </p>

                <form onSubmit={handleDetect} className="space-y-5">
                  <div className="border-2 border-dashed border-coal-700 hover:border-red-500/60 rounded-2xl p-6 text-center transition bg-coal-950/40">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="video/mp4,video/mkv,video/webm,video/avi"
                      onChange={(e) => {
                        const file = e.target.files?.[0] || null;
                        setSelectedFile(file);
                        setDetectionResult(null);
                        setDetectError(null);
                      }}
                      className="hidden"
                      id="video-uploader"
                    />
                    <label
                      htmlFor="video-uploader"
                      className="cursor-pointer flex flex-col items-center justify-center gap-3"
                    >
                      <div className="w-12 h-12 rounded-2xl bg-red-600/10 border border-red-500/20 text-red-400 flex items-center justify-center">
                        <Upload className="w-6 h-6" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">
                          {selectedFile
                            ? selectedFile.name
                            : "Klik untuk memilih berkas video"}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          Format didukung: MP4, MKV, WebM, AVI (Maksimal 100 MB)
                        </p>
                      </div>
                    </label>
                  </div>

                  {selectedFile && (
                    <div className="flex items-center justify-between p-3.5 bg-red-950/30 border border-red-800/40 rounded-xl">
                      <div className="flex items-center gap-3">
                        <Video className="w-4 h-4 text-red-400" />
                        <span className="text-xs font-mono text-slate-200">
                          {selectedFile.name} (
                          {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={handleResetAnalysis}
                        className="text-xs text-slate-400 hover:text-slate-200 underline"
                      >
                        Ganti Berkas
                      </button>
                    </div>
                  )}

                  {detectError && (
                    <div className="p-4 bg-orange-950/40 border border-orange-800/50 rounded-xl flex items-start gap-3 text-orange-300 text-xs">
                      <AlertTriangle className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                      <span>{detectError}</span>
                    </div>
                  )}

                  <div className="flex items-center gap-3">
                    <button
                      type="submit"
                      disabled={!selectedFile || detecting}
                      className="flex-1 py-3 px-4 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-medium text-sm flex items-center justify-center gap-2 transition shadow-lg shadow-red-600/20"
                    >
                      {detecting ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Memproses Keyframe & Mencocokkan Hash...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4 fill-white" />
                          Jalankan Pelacak Daur Ulang
                        </>
                      )}
                    </button>
                    {selectedFile && (
                      <button
                        type="button"
                        onClick={handleResetAnalysis}
                        className="px-4 py-3 rounded-xl border border-coal-700 hover:bg-coal-800 text-slate-300 text-sm font-medium transition"
                      >
                        Bersihkan
                      </button>
                    )}
                  </div>
                </form>
              </div>

              {/* Hasil Analisis Deteksi */}
              {detectionResult && (
                <div className="bg-coal-900 border border-coal-800 rounded-2xl p-6 shadow-sm space-y-6">
                  <div className="flex items-center justify-between border-b border-coal-800 pb-4">
                    <div>
                      <h4 className="font-semibold text-base text-slate-100">
                        Hasil Analisis Daur Ulang Video
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Ringkasan pencocokan sekuensial frame acuan vs query.
                      </p>
                    </div>

                    {detectionResult.status === "daur_ulang" ? (
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/15 border border-orange-400/40 text-orange-300 text-xs font-semibold">
                        <ShieldAlert className="w-4 h-4" />
                        KEMUNGKINAN DAUR ULANG
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
                        <ShieldCheck className="w-4 h-4" />
                        TIDAK DITEMUKAN DI ARSIP
                      </div>
                    )}
                  </div>

                  {/* 4 Metric Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 bg-coal-950/60 rounded-xl border border-coal-800">
                      <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                        Skor Kemiripan
                      </p>
                      <p className="text-2xl font-bold text-white mt-1">
                        {(detectionResult.skor * 100).toFixed(1)}%
                      </p>
                    </div>

                    <div className="p-4 bg-coal-950/60 rounded-xl border border-coal-800">
                      <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                        Tingkat Keyakinan
                      </p>
                      <p className="text-xl font-bold text-red-400 mt-1 capitalize">
                        {detectionResult.keyakinan}
                      </p>
                    </div>

                    <div className="p-4 bg-coal-950/60 rounded-xl border border-coal-800">
                      <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                        Frame Cocok / Total
                      </p>
                      <p className="text-xl font-bold text-white mt-1">
                        {detectionResult.frame_cocok} / {detectionResult.frame_total}
                      </p>
                    </div>

                    <div className="p-4 bg-coal-950/60 rounded-xl border border-coal-800">
                      <p className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">
                        Consecutive Run
                      </p>
                      <p className="text-xl font-bold text-white mt-1">
                        {detectionResult.consecutive_run} Frame
                      </p>
                    </div>
                  </div>

                  <div className="p-3.5 bg-coal-800/40 border border-coal-700/50 rounded-xl text-xs text-slate-300 flex items-start gap-2.5">
                    <Info className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                    <span>{detectionResult.catatan}</span>
                  </div>

                  {/* Side-by-Side Visual Comparison */}
                  <div>
                    <h5 className="font-semibold text-sm text-slate-200 mb-3">
                      🖼️ Komparasi Visual Berdampingan (Side-by-Side)
                    </h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                      {/* Left: Query Video Thumbnail */}
                      <div className="bg-coal-950 border border-coal-800 rounded-xl p-4 space-y-3">
                        <p className="text-xs font-medium text-slate-300">
                          Video yang Diperiksa (Input)
                        </p>
                        <div className="aspect-video bg-black rounded-lg overflow-hidden border border-coal-800 flex items-center justify-center">
                          {detectionResult.query_thumbnail_filename ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                              src={videoApi.getThumbnailUrl(
                                "temp",
                                detectionResult.query_thumbnail_filename
                              )}
                              alt="Thumbnail Video Input"
                              className="w-full h-full object-contain"
                            />
                          ) : (
                            <span className="text-xs text-slate-500">
                              Thumbnail tidak tersedia
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Right: Archive Match Thumbnail */}
                      <div className="bg-coal-950 border border-coal-800 rounded-xl p-4 space-y-3">
                        <p className="text-xs font-medium text-slate-300">
                          Video Acuan Asli di Basis Arsip
                        </p>
                        {detectionResult.status === "daur_ulang" &&
                        detectionResult.arsip_tercocok ? (
                          <>
                            <div className="aspect-video bg-black rounded-lg overflow-hidden border border-coal-800 flex items-center justify-center">
                              {detectionResult.arsip_tercocok.thumbnail_filename ? (
                                // eslint-disable-next-line @next/next/no-img-element
                                <img
                                  src={videoApi.getThumbnailUrl(
                                    "arsip",
                                    detectionResult.arsip_tercocok.thumbnail_filename
                                  )}
                                  alt="Thumbnail Arsip"
                                  className="w-full h-full object-contain"
                                />
                              ) : (
                                <span className="text-xs text-slate-500">
                                  Thumbnail arsip tidak tersedia
                                </span>
                              )}
                            </div>
                            <div className="text-xs space-y-1 text-slate-400">
                              <p>
                                <strong className="text-slate-200">
                                  Judul Asli:
                                </strong>{" "}
                                {detectionResult.arsip_tercocok.judul}
                              </p>
                              <p>
                                <strong className="text-slate-200">
                                  Tanggal Asli:
                                </strong>{" "}
                                {detectionResult.arsip_tercocok.tanggal_asli ||
                                  "Tidak tercatat"}
                              </p>
                              <p>
                                <strong className="text-slate-200">
                                  Sumber Resmi:
                                </strong>{" "}
                                {detectionResult.arsip_tercocok.sumber || "-"}
                              </p>
                              {detectionResult.arsip_tercocok.tautan && (
                                <p className="flex items-center gap-1.5 text-red-400 mt-1">
                                  <ExternalLink className="w-3.5 h-3.5" />
                                  <a
                                    href={detectionResult.arsip_tercocok.tautan}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="hover:underline truncate"
                                  >
                                    {detectionResult.arsip_tercocok.tautan}
                                  </a>
                                </p>
                              )}
                            </div>
                          </>
                        ) : (
                          <div className="aspect-video bg-coal-900/50 rounded-lg border border-dashed border-coal-800 flex items-center justify-center p-4 text-center">
                            <span className="text-xs text-slate-500">
                              Tidak ada klip arsip yang cocok secara sekuensial.
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Ethical guardrail disclaimer */}
                  <div className="text-[11px] text-slate-500 border-t border-coal-800 pt-3 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-slate-400" />
                    <span>
                      <strong>Prinsip Etika WARAZ:</strong> Hasil deteksi
                      merupakan indikasi algoritmik pendukung keputusan. Keputusan
                      verifikasi akhir tetap berada pada kendali analis manusia
                      (human-in-the-loop). Berkas video mentah segera dihapus dari server.
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Pendaftaran Arsip Baru */}
          {activeTab === "arsip" && (
            <div className="bg-coal-900 border border-coal-800 rounded-2xl p-6 shadow-sm space-y-6">
              <div>
                <h3 className="font-semibold text-base text-slate-100">
                  Daftarkan Klip Video ke Basis Arsip WARAZ
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Daftarkan video dokumentasi asli agar sistem dapat mendeteksi daur
                  ulang narasi di masa mendatang. Dilengkapi validasi anti-duplikasi.
                </p>
              </div>

              {regMessage && (
                <div
                  className={`p-4 rounded-xl flex items-start gap-3 text-xs border ${
                    regMessage.type === "success"
                      ? "bg-emerald-950/40 border-emerald-800/50 text-emerald-300"
                      : "bg-orange-950/40 border-orange-800/50 text-orange-300"
                  }`}
                >
                  {regMessage.type === "success" ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                  )}
                  <span>{regMessage.text}</span>
                </div>
              )}

              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Berkas Video Asli <span className="text-red-400">*</span>
                  </label>
                  <input
                    ref={regFileInputRef}
                    type="file"
                    accept="video/mp4,video/mkv,video/webm,video/avi"
                    onChange={(e) => setRegFile(e.target.files?.[0] || null)}
                    className="w-full text-xs text-slate-300 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-coal-800 file:text-slate-200 hover:file:bg-coal-700 bg-coal-950 border border-coal-800 rounded-xl p-2 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Judul / Deskripsi Peristiwa <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={regTitle}
                    onChange={(e) => setRegTitle(e.target.value)}
                    placeholder="Contoh: Latihan Penanggulangan Bencana BPBD 2024"
                    className="w-full text-xs bg-coal-950 border border-coal-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-red-500"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Tanggal Asli Kejadian
                    </label>
                    <input
                      type="date"
                      value={regDate}
                      onChange={(e) => setRegDate(e.target.value)}
                      className="w-full text-xs bg-coal-950 border border-coal-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-red-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                      Sumber Resmi / Penerbit
                    </label>
                    <input
                      type="text"
                      value={regSource}
                      onChange={(e) => setRegSource(e.target.value)}
                      placeholder="Contoh: Humas BNPB / YouTube Resmi"
                      className="w-full text-xs bg-coal-950 border border-coal-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-red-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Tautan / Link Berita Asli
                  </label>
                  <input
                    type="url"
                    value={regUrl}
                    onChange={(e) => setRegUrl(e.target.value)}
                    placeholder="https://bnpb.go.id/berita/latihan-banjir"
                    className="w-full text-xs bg-coal-950 border border-coal-800 rounded-xl px-4 py-2.5 text-slate-200 focus:outline-none focus:border-red-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={registering}
                  className="w-full py-3 px-4 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-medium text-sm flex items-center justify-center gap-2 transition shadow-lg shadow-red-600/30"
                >
                  {registering ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Mengekstrak Frame & Mendaftarkan ke Database Neon...
                    </>
                  ) : (
                    <>
                      <FolderPlus className="w-4 h-4" />
                      Simpan Video ke Basis Arsip
                    </>
                  )}
                </button>
              </form>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
