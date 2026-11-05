"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, CheckCircle2, FileText, ShieldCheck } from "lucide-react";
import { claimSubmissionApi } from "@/services/api";

export default function SubmitClaimPage() {
  const [claim, setClaim] = useState("");
  const [summary, setSummary] = useState("");
  const [source, setSource] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [category, setCategory] = useState("lainnya");
  const [anonymous, setAnonymous] = useState(true);
  const [submitterAlias, setSubmitterAlias] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!claim.trim()) {
      setError("Klaim wajib diisi sebelum dikirim.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

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

      setSuccess(response.message || "Klaim berhasil dikirim untuk ditinjau.");
      setClaim("");
      setSummary("");
      setSource("");
      setSourceUrl("");
      setCategory("lainnya");
      setAnonymous(true);
      setSubmitterAlias("");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Terjadi kesalahan saat mengirim klaim.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-red-500/20 bg-slate-900/80 sticky top-0 z-40 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-500/15 border border-red-400/30 flex items-center justify-center text-red-300">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-bold tracking-wide text-white">WARAZ</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                Ajukan Klaim Baru
              </div>
            </div>
          </div>

          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200 hover:bg-red-500/20 transition"
          >
            <ArrowLeft className="w-4 h-4" />
            Beranda
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-10">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/80 p-6 shadow-lg shadow-red-950/20">
          <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-200">
            <ShieldCheck className="w-3.5 h-3.5" />
            Pengajuan Klaim Anonim
          </div>

          <h1 className="mt-5 text-3xl font-extrabold tracking-tight text-white">
            Tambahkan klaim yang ingin masuk ke basis klarifikasi.
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-slate-400">
            Formulir ini bersifat anonim. Setelah dikirim, admin akan menilai apakah klaim tersebut layak masuk ke basis data klarifikasi WARAZ.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">Klaim</label>
              <textarea
                value={claim}
                onChange={(event) => setClaim(event.target.value)}
                rows={5}
                placeholder="Contoh: Pemerintah terlihat memaksa evakuasi massal setelah alarm palsu..."
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 p-4 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-300">Ringkasan singkat</label>
              <textarea
                value={summary}
                onChange={(event) => setSummary(event.target.value)}
                rows={3}
                placeholder="Tambahkan penjelasan singkat terkait klaim tersebut..."
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 p-4 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">Sumber</label>
                <input
                  value={source}
                  onChange={(event) => setSource(event.target.value)}
                  placeholder="Sumber atau kanal"
                  className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">Kategori</label>
                <select
                  value={category}
                  onChange={(event) => setCategory(event.target.value)}
                  className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
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
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
              />
            </div>

            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 rounded-2xl border border-slate-700 bg-slate-950/60 p-4">
              <div>
                <div className="text-sm font-medium text-slate-200">Kirim sebagai anonim</div>
                <div className="text-xs text-slate-400">Data pengirim tidak dipublikasikan ke aplikasi.</div>
              </div>

              <button
                type="button"
                onClick={() => setAnonymous((prev) => !prev)}
                className={`relative inline-flex h-7 w-12 items-center rounded-full transition ${anonymous ? "bg-red-500" : "bg-slate-700"}`}
                aria-label="Toggle anonim"
              >
                <span
                  className={`inline-block h-5 w-5 rounded-full bg-white transition ${anonymous ? "translate-x-6" : "translate-x-1"}`}
                />
              </button>
            </div>

            {!anonymous && (
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">Alias pengirim (opsional)</label>
                <input
                  value={submitterAlias}
                  onChange={(event) => setSubmitterAlias(event.target.value)}
                  placeholder="Alias Anda"
                  className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 p-3 text-sm text-slate-100 focus:border-red-400 focus:ring-2 focus:ring-red-500/20 outline-none"
                />
              </div>
            )}

            {error && (
              <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-200 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center rounded-xl bg-[#fb5858] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#ff6f6f] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Mengirim..." : "Kirim usulan klaim"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
