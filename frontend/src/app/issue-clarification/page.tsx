"use client";

import Link from "next/link";
import { useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  FileText,
  Search,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import {
  claimSubmissionApi,
  issueClarificationApi,
  IssueClarificationResponse,
} from "@/services/api";

const sampleIssue =
  "Pemerintah diam-diam merencanakan evakuasi paksa setelah alarm darurat palsu."

export default function IssueClarificationPage() {
  const [activeTab, setActiveTab] = useState<"check" | "submit">("check");
  const [issue, setIssue] = useState(sampleIssue);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IssueClarificationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [claim, setClaim] = useState("");
  const [summary, setSummary] = useState("");
  const [source, setSource] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [category, setCategory] = useState("lainnya");
  const [anonymous, setAnonymous] = useState(true);
  const [submitterAlias, setSubmitterAlias] = useState("");
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!issue.trim()) {
      setError("Silakan masukkan isu yang ingin diperiksa.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await issueClarificationApi.check(issue);
      setResult(response);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Terjadi kesalahan yang tidak terduga.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!claim.trim()) {
      setSubmitError("Klaim wajib diisi sebelum dikirim.");
      return;
    }

    setSubmitLoading(true);
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      const response = await claimSubmissionApi.submit({
        claim,
        summary,
        source,
        source_url: sourceUrl,
        category,
        anonymous,
        submitter_alias: submitterAlias || undefined,
      });

      setSubmitSuccess(response.message || "Klaim berhasil dikirim dan menunggu persetujuan admin.");
      setClaim("");
      setSummary("");
      setSource("");
      setSourceUrl("");
      setCategory("lainnya");
      setAnonymous(true);
      setSubmitterAlias("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Gagal mengirim usulan klaim.";
      setSubmitError(message);
    } finally {
      setSubmitLoading(false);
    }
  };

  const statusTone =
    result?.status_result === "sudah_diklarifikasi"
      ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
      : result?.status_result === "ditemukan_mirip"
        ? "bg-amber-500/10 text-amber-300 border border-amber-500/30"
        : "bg-coal-800 text-slate-200 border border-coal-700";

  const statusLabel =
    result?.status_result === "sudah_diklarifikasi"
      ? "sudah diklarifikasi"
      : result?.status_result === "ditemukan_mirip"
        ? "ditemukan mirip"
        : result?.status_result === "belum_ditemukan"
          ? "belum ditemukan"
          : "belum ada isi";

  const formatClaimStatus = (status?: string) => {
    const normalized = (status || "").trim().toLowerCase();
    const canonicalStatus =
      normalized === "sebagian benar"
        ? "menyesatkan"
        : normalized === "sebagian_benar"
          ? "menyesatkan"
          : normalized;

    const statusMap: Record<string, { label: string; tone: string }> = {
      hoaks: {
        label: "Hoaks",
        tone: "bg-red-500/10 text-red-200 border border-red-500/30",
      },
      disinformasi: {
        label: "Disinformasi",
        tone: "bg-rose-500/10 text-rose-200 border border-rose-500/30",
      },
      menyesatkan: {
        label: "Menyesatkan",
        tone: "bg-amber-500/10 text-amber-200 border border-amber-500/30",
      },
      benar: {
        label: "Benar",
        tone: "bg-emerald-500/10 text-emerald-200 border border-emerald-500/30",
      },
      lainnya: {
        label: "Lainnya",
        tone: "bg-slate-500/10 text-slate-200 border border-slate-500/30",
      },
    };

    const fallback = {
      label:
        canonicalStatus
          ? canonicalStatus
              .split(" ")
              .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
              .join(" ")
          : "Lainnya",
      tone: "bg-slate-500/10 text-slate-200 border border-slate-500/30",
    };

    return statusMap[canonicalStatus] || fallback;
  };

  const primaryClaimStatus = formatClaimStatus(result?.matches[0]?.status);

  return (
    <div className="min-h-screen text-slate-100">
      <header className="border-b border-red-500/20 bg-coal-900/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/15 border border-red-400/30 flex items-center justify-center text-red-300">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold tracking-wide text-white">WARAZ</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                Cek Klarifikasi Isu
              </div>
            </div>
          </div>

          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200 hover:bg-red-500/20 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Kembali ke beranda
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-8">
          <section className="rounded-3xl border border-coal-800 bg-coal-900/80 p-6 shadow-lg shadow-red-950/20">
            <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-200">
              <Sparkles className="w-3.5 h-3.5" />
              Mesin Rekomendasi Klarifikasi
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => setActiveTab("check")}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  activeTab === "check"
                    ? "bg-[#fb5858] text-white"
                    : "border border-coal-700 bg-coal-950 text-slate-300"
                }`}
              >
                <Search className="w-4 h-4" />
                Cek klarifikasi isu
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("submit")}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  activeTab === "submit"
                    ? "bg-[#fb5858] text-white"
                    : "border border-coal-700 bg-coal-950 text-slate-300"
                }`}
              >
                <FileText className="w-4 h-4" />
                Ajukan klaim baru
              </button>
            </div>

            {activeTab === "check" ? (
              <>
                <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-white">
                  Cek apakah isu sudah pernah diklarifikasi.
                </h1>
                <p className="mt-3 max-w-xl text-sm leading-relaxed text-slate-400">
                  Masukkan klaim atau narasi yang beredar, lalu sistem akan membandingkannya dengan basis klarifikasi terkurasi untuk melihat kesamaannya.
                </p>

                <form onSubmit={handleSubmit} className="mt-8 space-y-4">
                  <label className="block text-sm font-medium text-slate-300">
                    Isu / Klaim
                  </label>
                  <textarea
                    value={issue}
                    onChange={(event) => setIssue(event.target.value)}
                    rows={7}
                    className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-4 text-sm text-slate-100 shadow-inner outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-500/20"
                    placeholder="Tempel judul, klaim, atau narasi yang Anda curigai..."
                  />

                  <div className="flex flex-wrap items-center gap-3">
                    <button
                      type="submit"
                      disabled={loading}
                      className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#fb5858] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#ff6f6f] disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      <Search className="w-4 h-4" />
                      {loading ? "Memeriksa..." : "Periksa klarifikasi"}
                    </button>

                    <button
                      type="button"
                      onClick={() => setIssue(sampleIssue)}
                      className="rounded-xl border border-coal-700 bg-coal-900 px-4 py-3 text-sm text-slate-300 transition hover:border-coal-600"
                    >
                      Coba kasus contoh
                    </button>
                  </div>
                </form>

                {error && (
                  <div className="mt-5 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                    {error}
                  </div>
                )}
              </>
            ) : (
              <>
                <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-white">
                  Ajukan klaim baru untuk ditinjau admin.
                </h1>
                <p className="mt-3 max-w-xl text-sm leading-relaxed text-slate-400">
                  Pengajuan bersifat anonim. Setelah dikirim, admin akan menilai apakah klaim tersebut layak masuk ke basis klarifikasi WARAZ.
                </p>

                <form onSubmit={handleClaimSubmit} className="mt-8 space-y-5">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">Klaim</label>
                    <textarea
                      value={claim}
                      onChange={(event) => setClaim(event.target.value)}
                      rows={5}
                      placeholder="Contoh: Pemerintah terlihat memaksa evakuasi massal setelah alarm palsu..."
                      className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-4 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">Ringkasan singkat</label>
                    <textarea
                      value={summary}
                      onChange={(event) => setSummary(event.target.value)}
                      rows={3}
                      placeholder="Tambahkan penjelasan singkat terkait klaim tersebut..."
                      className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-4 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">Sumber</label>
                      <input
                        value={source}
                        onChange={(event) => setSource(event.target.value)}
                        placeholder="Sumber atau kanal"
                        className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                      />
                    </div>

                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">Kategori</label>
                      <select
                        value={category}
                        onChange={(event) => setCategory(event.target.value)}
                        className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                      >
                        <option value="lainnya">Lainnya</option>
                        <option value="hoaks">Hoaks</option>
                        <option value="disinformasi">Disinformasi</option>
                        <option value="benar">Benar</option>
                        <option value="menyesatkan">Menyesatkan</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">Link sumber (opsional)</label>
                    <input
                      value={sourceUrl}
                      onChange={(event) => setSourceUrl(event.target.value)}
                      placeholder="https://..."
                      className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                    />
                  </div>

                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 rounded-2xl border border-coal-700 bg-coal-950/60 p-4">
                    <div>
                      <div className="text-sm font-medium text-slate-200">Kirim sebagai anonim</div>
                      <div className="text-xs text-slate-400">Data pengirim tidak dipublikasikan ke aplikasi.</div>
                    </div>

                    <button
                      type="button"
                      onClick={() => setAnonymous((prev) => !prev)}
                      className={`relative inline-flex h-7 w-12 items-center rounded-full transition ${anonymous ? "bg-red-500" : "bg-coal-700"}`}
                      aria-label="Toggle anonim"
                    >
                      <span className={`inline-block h-5 w-5 rounded-full bg-white transition ${anonymous ? "translate-x-6" : "translate-x-1"}`} />
                    </button>
                  </div>

                  {!anonymous && (
                    <div>
                      <label className="mb-2 block text-sm font-medium text-slate-300">Alias pengirim (opsional)</label>
                      <input
                        value={submitterAlias}
                        onChange={(event) => setSubmitterAlias(event.target.value)}
                        placeholder="Alias Anda"
                        className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                      />
                    </div>
                  )}

                  {submitError && (
                    <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                      {submitError}
                    </div>
                  )}

                  {submitSuccess && (
                    <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200 flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4" />
                      {submitSuccess}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={submitLoading}
                    className="inline-flex items-center justify-center rounded-xl bg-[#fb5858] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#ff6f6f] disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {submitLoading ? "Mengirim..." : "Kirim usulan klaim"}
                  </button>
                </form>
              </>
            )}
          </section>

          <aside className="rounded-3xl border border-coal-800 bg-coal-900/80 p-6 shadow-lg shadow-red-950/10">
            <h2 className="text-lg font-semibold text-white">Ringkasan status</h2>

            {!result && !error && (
              <div className="mt-6 rounded-2xl border border-dashed border-coal-700 bg-coal-950/60 p-5 text-sm text-slate-400">
                Belum ada evaluasi. Masukkan isu untuk melihat hasilnya.
              </div>
            )}

            {result && (
              <div className="mt-6 space-y-5">
                <div className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium ${statusTone}`}>
                  {result.status_result === "sudah_diklarifikasi" ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <AlertTriangle className="w-4 h-4" />
                  )}
                  {statusLabel}
                </div>

                <div className="rounded-2xl border border-coal-700 bg-coal-950/60 p-4">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">
                    Skor kemiripan
                  </div>
                  <div className="mt-2 text-3xl font-bold text-white">{result.score.toFixed(2)}</div>
                </div>

                <div className="rounded-2xl border border-coal-700 bg-coal-950/60 p-4">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-slate-500">
                    Status klaim
                  </div>
                  <div className={`mt-2 inline-flex items-center rounded-full px-3 py-1.5 text-xs font-medium ${primaryClaimStatus.tone}`}>
                    {primaryClaimStatus.label}
                  </div>
                </div>

                <p className="text-sm leading-relaxed text-slate-300">{result.note}</p>

                <div className="space-y-3">
                  {result.matches.length === 0 ? (
                    <div className="text-sm text-slate-400">Belum ada rekam jejak yang cocok.</div>
                  ) : (
                    result.matches.map((match) => {
                      const claimStatus = formatClaimStatus(match.status);

                      return (
                        <div key={match.id} className="rounded-2xl border border-red-500/20 bg-red-500/5 p-4">
                          <div className="flex items-start justify-between gap-3">
                            <div className="text-sm font-semibold text-white">{match.claim}</div>
                            <div className={`inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.18em] ${claimStatus.tone}`}>
                              {claimStatus.label}
                            </div>
                          </div>
                          <div className="mt-2 text-xs text-slate-300">{match.summary}</div>
                          <div className="mt-3 text-[11px] text-slate-400">
                            {match.source} · {match.date}
                          </div>
                          {match.url && (
                            <a
                              href={match.url}
                              target="_blank"
                              rel="noreferrer"
                              className="mt-3 inline-block text-xs text-red-200 underline underline-offset-4"
                            >
                              Lihat sumber
                            </a>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </aside>
        </div>
      </main>
    </div>
  );
}
