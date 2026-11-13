"use client";

import Image from "next/image";
import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  BrainCircuit,
  Sliders,
  AlertTriangle,
  FileText,
  Sparkles,
  ChevronRight,
  Target,
} from "lucide-react";
import logoImg from "@/assets/logo.png";
import {
  manipulationApi,
  ManipulationAnalysisResponse,
  TechniqueDefinition,
  PresetExample,
} from "@/services/api";

export default function ManipulationMapPage() {
  const [inputText, setInputText] = useState("");
  const [threshold, setThreshold] = useState<number>(0.45);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ManipulationAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [presets, setPresets] = useState<PresetExample[]>([]);
  const [taxonomy, setTaxonomy] = useState<TechniqueDefinition[]>([]);
  const [activeTab, setActiveTab] = useState<"analysis" | "taxonomy">("analysis");
  const [selectedTechniqueFilter, setSelectedTechniqueFilter] = useState<string | null>(null);

  useEffect(() => {
    // Load presets and taxonomy in background
    manipulationApi
      .getPresets()
      .then(setPresets)
      .catch((err: unknown) => console.warn("Failed to load presets", err));

    manipulationApi
      .getTaxonomy()
      .then(setTaxonomy)
      .catch((err: unknown) => console.warn("Failed to load taxonomy", err));
  }, []);

  const handleAnalyze = async (textToAnalyze?: string) => {
    const text = (textToAnalyze !== undefined ? textToAnalyze : inputText).trim();
    if (text.length < 5) {
      setError("Masukkan teks narasi minimal 5 karakter.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await manipulationApi.analyze(text, threshold);
      setResult(res);
      setSelectedTechniqueFilter(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Gagal menganalisis teks narasi.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (preset: PresetExample) => {
    setInputText(preset.text);
    handleAnalyze(preset.text);
  };

  // Kategori icon / badge helper
  const getCategoryColor = (cat: string) => {
    if (cat.includes("Ketakutan") || cat.includes("Ancaman")) return "text-red-400 bg-red-950/40 border-red-800/60";
    if (cat.includes("Waktu")) return "text-amber-400 bg-amber-950/40 border-amber-800/60";
    if (cat.includes("Emosional")) return "text-rose-400 bg-rose-950/40 border-rose-800/60";
    if (cat.includes("Polarisasi")) return "text-purple-400 bg-purple-950/40 border-purple-800/60";
    return "text-orange-400 bg-orange-950/40 border-orange-800/60";
  };

  // Highlighting spans helper
  const renderedHighlightedText = useMemo(() => {
    if (!result) return null;
    const text = result.text;

    // Kumpulkan semua kutipan bukti dari teknik yang terdeteksi
    const quotes: { quote: string; techName: string; techId: string }[] = [];
    result.techniques.forEach((t) => {
      if (t.detected && (!selectedTechniqueFilter || selectedTechniqueFilter === t.technique_id)) {
        t.evidences.forEach((ev) => {
          if (ev.quote && ev.quote.length > 2) {
            quotes.push({ quote: ev.quote, techName: t.technique_name, techId: t.technique_id });
          }
        });
      }
    });

    if (quotes.length === 0) {
      return <p className="text-slate-300 leading-relaxed font-sans">{text}</p>;
    }

    // Urutkan quote berdasarkan panjang karakter menurun agar substring yang lebih spesifik tidak menimpa
    quotes.sort((a, b) => b.quote.length - a.quote.length);

    // Cari posisi kata dalam teks
    let segments: { text: string; isHighlight: boolean; tag?: string }[] = [{ text, isHighlight: false }];

    for (const q of quotes) {
      const newSegments: typeof segments = [];
      for (const seg of segments) {
        if (seg.isHighlight) {
          newSegments.push(seg);
          continue;
        }

        const lowerSeg = seg.text.toLowerCase();
        const lowerQuote = q.quote.toLowerCase();
        const matchIdx = lowerSeg.indexOf(lowerQuote);

        if (matchIdx !== -1) {
          const before = seg.text.slice(0, matchIdx);
          const matched = seg.text.slice(matchIdx, matchIdx + q.quote.length);
          const after = seg.text.slice(matchIdx + q.quote.length);

          if (before) newSegments.push({ text: before, isHighlight: false });
          newSegments.push({ text: matched, isHighlight: true, tag: q.techName });
          if (after) newSegments.push({ text: after, isHighlight: false });
        } else {
          newSegments.push(seg);
        }
      }
      segments = newSegments;
    }

    return (
      <div className="text-slate-200 leading-relaxed font-sans space-y-1">
        {segments.map((seg, idx) =>
          seg.isHighlight ? (
            <mark
              key={idx}
              className="bg-red-500/25 border-b-2 border-red-500 text-red-200 px-1 py-0.5 rounded font-medium relative group inline-block cursor-help mx-0.5"
            >
              {seg.text}
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block bg-coal-950 text-red-400 border border-red-800 text-[10px] px-2 py-0.5 rounded shadow-xl whitespace-nowrap z-30 font-mono">
                {seg.tag}
              </span>
            </mark>
          ) : (
            <span key={idx}>{seg.text}</span>
          )
        )}
      </div>
    );
  }, [result, selectedTechniqueFilter]);

  return (
    <div className="min-h-screen bg-coal-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-red-900/40 bg-coal-900/60 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="transition hover:scale-105">
              <Image
                src={logoImg}
                alt="WARAZ logo"
                width={36}
                height={36}
                className="h-9 w-9 rounded-xl border border-red-500/30 bg-red-600/20 p-1.5 object-contain shadow-lg shadow-red-600/25"
              />
            </Link>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-red-400 text-base">
                  WARAZ
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-950/80 border border-red-800/60 text-red-300 font-mono">
                  Feature 3
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Peta Teknik Manipulasi Narasi</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("analysis")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                activeTab === "analysis"
                  ? "bg-red-600/20 text-red-300 border border-red-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Laboratorium Analisis
            </button>
            <button
              onClick={() => setActiveTab("taxonomy")}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                activeTab === "taxonomy"
                  ? "bg-red-600/20 text-red-300 border border-red-500/30"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Katalog 9 Taksonomi
            </button>
            <Link
              href="/"
              className="ml-3 px-3 py-1.5 rounded-lg bg-coal-800 hover:bg-coal-700 text-slate-300 text-xs transition border border-coal-700"
            >
              Kembali
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full space-y-8">
        {/* Intro Banner */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-coal-900 via-coal-900/90 to-coal-950 border border-red-900/30 p-6 shadow-xl">
          <div className="max-w-3xl space-y-2">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
              <BrainCircuit className="w-3.5 h-3.5" />
              Forensik Rekayasa Narasi & Pola Psikologis
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              Peta Teknik Manipulasi
            </h1>
            <p className="text-xs md:text-sm text-slate-400 leading-relaxed">
              Memetakan berbagai pola dan teknik manipulasi psikologis (seperti urgensi palsu, framing ancaman, ilusi konsensus, hingga whataboutism). Membedakan secara transparan antara narasi disinformasi yang berbahaya dengan kritik publik yang sah.
            </p>
          </div>
        </div>

        {activeTab === "analysis" ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Kolom Kiri: Input & Preset (5 cols) */}
            <div className="lg:col-span-5 space-y-6">
              {/* Form Input */}
              <div className="rounded-2xl bg-coal-900/80 border border-coal-800 p-6 shadow-lg space-y-4">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                    <FileText className="w-4 h-4 text-red-400" />
                    Input Teks Narasi / Klaim
                  </label>
                  <span className="text-[11px] text-slate-500 font-mono">
                    {inputText.length} karakter
                  </span>
                </div>

                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Tempelkan teks postingan medsos, broadcast WhatsApp, atau narasi berita yang mencurigakan di sini..."
                  rows={6}
                  className="w-full bg-coal-950 border border-coal-800 rounded-xl p-3.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-red-500/60 focus:ring-1 focus:ring-red-500/60 transition"
                />

                {/* Ambang Batas Keyakinan Slider */}
                <div className="pt-2 border-t border-coal-800 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <Sliders className="w-3.5 h-3.5 text-red-400" />
                      Ambang Batas Keyakinan (Confidence Threshold):
                    </span>
                    <span className="font-mono text-red-400 font-bold">
                      {Math.round(threshold * 100)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0.2"
                    max="0.8"
                    step="0.05"
                    value={threshold}
                    onChange={(e) => setThreshold(parseFloat(e.target.value))}
                    className="w-full accent-red-500 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                    <span>Sensitif (20%)</span>
                    <span>Standar (45%)</span>
                    <span>Ketat (80%)</span>
                  </div>
                </div>

                {error && (
                  <div className="p-3 rounded-xl bg-red-950/40 border border-red-800/80 text-red-300 text-xs flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                    <span>{error}</span>
                  </div>
                )}

                <button
                  onClick={() => handleAnalyze()}
                  disabled={loading}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 text-white font-semibold text-sm transition shadow-lg shadow-red-600/25 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Menganalisis Narasi...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Mulai Analisis Teknik Manipulasi
                    </>
                  )}
                </button>
              </div>

              {/* Preset Uji Coba */}
              <div className="rounded-2xl bg-coal-900/60 border border-coal-800/80 p-5 space-y-3">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  <Target className="w-4 h-4 text-orange-400" />
                  Preset Contoh Uji Coba (Demo Fast-Track)
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Pilih salah satu skenario untuk melihat deteksi manipulasi atau uji kontra-contoh (kritik yang sah).
                </p>

                <div className="space-y-2 pt-1">
                  {presets.map((preset) => (
                    <button
                      key={preset.id}
                      onClick={() => applyPreset(preset)}
                      className="w-full text-left p-3 rounded-xl bg-coal-950/60 hover:bg-coal-800/80 border border-coal-800 hover:border-red-500/40 transition group flex items-start justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded-full font-mono border ${
                              preset.is_manipulation
                                ? "bg-red-950/80 border-red-800 text-red-300"
                                : "bg-emerald-950/80 border-emerald-800 text-emerald-300"
                            }`}
                          >
                            {preset.is_manipulation ? "Manipulatif" : "Kritik Sah (Kontra)"}
                          </span>
                          <span className="text-xs font-bold text-slate-200 group-hover:text-red-400 transition">
                            {preset.title}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 line-clamp-1 italic">
                          "{preset.text}"
                        </p>
                      </div>
                      <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-red-400 group-hover:translate-x-1 transition flex-shrink-0 mt-1" />
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Kolom Kanan: Hasil Visualisasi & Analisis (7 cols) */}
            <div className="lg:col-span-7 space-y-6">
              {result ? (
                <div className="space-y-6">
                  {/* Status Banner */}
                  <div
                    className={`rounded-2xl p-6 border shadow-lg ${
                      result.is_manipulative
                        ? "bg-red-950/30 border-red-900/60"
                        : "bg-emerald-950/30 border-emerald-900/60"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                            result.is_manipulative
                              ? "bg-red-600/20 border border-red-500/40 text-red-400"
                              : "bg-emerald-600/20 border border-emerald-500/40 text-emerald-400"
                          }`}
                        >
                          {result.is_manipulative ? (
                            <ShieldAlert className="w-6 h-6" />
                          ) : (
                            <ShieldCheck className="w-6 h-6" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h2 className="text-lg font-bold text-white">
                              {result.classification}
                            </h2>
                            <span className="text-[10px] px-2 py-0.5 rounded-full font-mono bg-coal-900 border border-coal-700 text-slate-400">
                              Engine: {result.engine_used}
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 mt-1">
                            {result.summary}
                          </p>
                        </div>
                      </div>

                      <div className="text-right flex-shrink-0">
                        <div className="text-[10px] text-slate-400 uppercase font-mono">
                          Indeks Manipulasi
                        </div>
                        <div
                          className={`text-2xl font-black font-mono ${
                            result.is_manipulative ? "text-red-400" : "text-emerald-400"
                          }`}
                        >
                          {Math.round(result.overall_manipulation_score * 100)}%
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Teks dengan Penyorotan Bukti (Highlighted Spans) */}
                  <div className="rounded-2xl bg-coal-900/80 border border-coal-800 p-6 shadow-lg space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-red-400" />
                        Pemeriksaan Forensik Teks & Kutipan Bukti
                      </h3>
                      {selectedTechniqueFilter && (
                        <button
                          onClick={() => setSelectedTechniqueFilter(null)}
                          className="text-[11px] text-orange-400 hover:underline"
                        >
                          Tampilkan Semua Highlight
                        </button>
                      )}
                    </div>
                    <div className="p-4 rounded-xl bg-coal-950 border border-coal-800/80">
                      {renderedHighlightedText}
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Bagian teks bergaris bawah merah adalah kata kunci pemicu yang terdeteksi melanggar pola psikologis narasi wajar.
                    </p>
                  </div>

                  {/* Visualisasi Bar Skor 9 Teknik */}
                  <div className="rounded-2xl bg-coal-900/80 border border-coal-800 p-6 shadow-lg space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                        <BrainCircuit className="w-4 h-4 text-orange-400" />
                        Peta Distribusi 9 Teknik Manipulasi
                      </h3>
                      <span className="text-[11px] font-mono text-slate-400">
                        Ambang: {Math.round(threshold * 100)}%
                      </span>
                    </div>

                    <div className="space-y-3.5">
                      {result.techniques.map((tech) => {
                        const isFiltered =
                          selectedTechniqueFilter === tech.technique_id;
                        const isTriggered = tech.detected;

                        return (
                          <div
                            key={tech.technique_id}
                            onClick={() =>
                              setSelectedTechniqueFilter(
                                isFiltered ? null : tech.technique_id
                              )
                            }
                            className={`p-3.5 rounded-xl border transition cursor-pointer ${
                              isFiltered
                                ? "bg-red-950/40 border-red-500/80 shadow-md"
                                : isTriggered
                                ? "bg-coal-950/80 border-red-900/40 hover:border-red-500/40"
                                : "bg-coal-950/40 border-coal-800 hover:border-coal-700 opacity-60"
                            }`}
                          >
                            <div className="flex items-center justify-between gap-2 mb-2">
                              <div className="flex items-center gap-2">
                                <span
                                  className={`text-[10px] px-2 py-0.5 rounded border font-mono ${getCategoryColor(
                                    tech.category
                                  )}`}
                                >
                                  {tech.category}
                                </span>
                                <span className="text-xs font-bold text-slate-200">
                                  {tech.technique_name}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 font-mono text-xs">
                                <span
                                  className={`font-bold ${
                                    isTriggered ? "text-red-400" : "text-slate-500"
                                  }`}
                                >
                                  {Math.round(tech.score * 100)}%
                                </span>
                                {isTriggered && (
                                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-red-950 border border-red-800 text-red-300">
                                    Aktif
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Bar Visualizer */}
                            <div className="w-full h-2 rounded-full bg-coal-800 overflow-hidden relative">
                              {/* Marker threshold */}
                              <div
                                className="absolute top-0 bottom-0 w-0.5 bg-slate-400 z-10"
                                style={{ left: `${threshold * 100}%` }}
                                title="Threshold"
                              />
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  isTriggered
                                    ? "bg-gradient-to-r from-orange-500 to-red-500"
                                    : "bg-slate-600"
                                }`}
                                style={{ width: `${Math.min(100, tech.score * 100)}%` }}
                              />
                            </div>

                            {/* Evidence Details */}
                            {tech.evidences.length > 0 && (
                              <div className="mt-2.5 pt-2 border-t border-coal-800/80 space-y-1">
                                {tech.evidences.map((ev, i) => (
                                  <div
                                    key={i}
                                    className="text-[11px] text-slate-300 flex items-start gap-1.5"
                                  >
                                    <span className="text-red-400 font-bold">•</span>
                                    <span>
                                      Bukti: <strong className="text-red-300">"{ev.quote}"</strong>
                                      {ev.explanation && ` — ${ev.explanation}`}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ) : (
                /* Empty state sebelum analisis */
                <div className="rounded-2xl border border-dashed border-coal-800 p-12 text-center space-y-4">
                  <div className="w-14 h-14 rounded-2xl bg-coal-900 border border-coal-800 flex items-center justify-center mx-auto text-slate-500">
                    <BrainCircuit className="w-7 h-7" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="text-base font-bold text-slate-300">
                      Menunggu Input Narasi
                    </h3>
                    <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                      Ketikkan atau tempelkan klaim berita di sebelah kiri, atau pilih preset demo fast-track untuk melihat pemetaan 9 teknik manipulasi dan kutipan bukti forensik.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Tab Katalog Taksonomi */
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">
                  Katalog 9 Taksonomi Manipulasi Narasi WARAZ
                </h2>
                <p className="text-xs text-slate-400">
                  Standar forensik analisis psikologis dan rekayasa narasi terkoordinasi.
                </p>
              </div>
              <span className="text-xs font-mono text-red-400 bg-red-950/60 px-2.5 py-1 rounded-full border border-red-800">
                {taxonomy.length} Teknik Terdaftar
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {taxonomy.map((item) => (
                <div
                  key={item.id}
                  className="rounded-2xl bg-coal-900/80 border border-coal-800 p-5 shadow-lg space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded border font-mono ${getCategoryColor(
                          item.category
                        )}`}
                      >
                        {item.category}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">
                        #{item.id}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-slate-100">
                      {item.name_id}
                    </h3>

                    <p className="text-xs text-slate-400 leading-relaxed">
                      {item.definition}
                    </p>
                  </div>

                  <div className="space-y-2 pt-3 border-t border-coal-800/80">
                    <div className="text-[10px] text-slate-500 font-mono uppercase">
                      Contoh Penerapan:
                    </div>
                    <div className="p-2.5 rounded-lg bg-coal-950 border border-coal-800 text-[11px] text-slate-300 italic">
                      "{item.example}"
                    </div>

                    <div className="text-[10px] text-slate-500 font-mono uppercase pt-1">
                      Indikator Kunci:
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {item.indicators.slice(0, 5).map((ind, idx) => (
                        <span
                          key={idx}
                          className="text-[10px] px-1.5 py-0.5 rounded bg-coal-800 text-slate-400 font-mono"
                        >
                          {ind}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-coal-800/80 py-6 text-center text-xs text-slate-500 mt-12">
        WARAZ Platform © 2026 — Feature 3: Manipulation Technique Mapping Subsystem
      </footer>
    </div>
  );
}
