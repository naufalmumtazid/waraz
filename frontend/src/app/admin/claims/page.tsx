"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, CheckCircle2, ShieldCheck, XCircle } from "lucide-react";
import logoImg from "@/assets/logo.png";
import { adminClaimsApi, PublicClaimSubmission } from "@/services/api";

export default function AdminClaimsPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState<string | null>(null);
  const [claims, setClaims] = useState<PublicClaimSubmission[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingClaims, setLoadingClaims] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const savedToken = window.localStorage.getItem("waraz-admin-token");
    if (savedToken) {
      setToken(savedToken);
      void fetchClaims(savedToken);
    }
  }, []);

  const fetchClaims = async (adminToken: string) => {
    setLoadingClaims(true);
    setError(null);

    try {
      const data = await adminClaimsApi.list(adminToken);
      setClaims(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal memuat usulan klaim.";
      setError(msg);
    } finally {
      setLoadingClaims(false);
    }
  };

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      const result = await adminClaimsApi.login({ email, password });
      setToken(result.token);
      window.localStorage.setItem("waraz-admin-token", result.token);
      await fetchClaims(result.token);
      setMessage("Login admin berhasil. Daftar usulan klaim sudah dimuat.");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Login gagal.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (claimId: string, decision: "approve" | "reject", reviewNote: string) => {
    if (!token) {
      setError("Silakan login admin terlebih dahulu.");
      return;
    }

    try {
      await adminClaimsApi.review(token, claimId, decision, reviewNote);
      await fetchClaims(token);
      setMessage(`Klaim ${decision === "approve" ? "disetujui" : "ditolak"}.`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Gagal meninjau klaim.";
      setError(msg);
    }
  };

  return (
    <div className="min-h-screen text-slate-100">
      <header className="border-b border-red-500/20 bg-coal-900/80 sticky top-0 z-40 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src={logoImg}
              alt="WARAZ logo"
              width={40}
              height={40}
              className="h-10 w-10 rounded-xl border border-red-400/30 bg-red-500/15 p-1.5 object-contain"
            />
            <div>
              <div className="text-sm font-bold tracking-wide text-white">WARAZ</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                Admin Review Claims
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

      <main className="max-w-6xl mx-auto px-4 py-10">
        {!token ? (
          <div className="max-w-xl mx-auto rounded-3xl border border-coal-800 bg-coal-900/80 p-6 shadow-lg shadow-red-950/20">
            <h1 className="text-2xl font-extrabold text-white">Login admin</h1>
            <p className="mt-2 text-sm text-slate-400">
              Hanya admin yang boleh meninjau dan menyetujui klaim baru sebelum masuk ke basis klarifikasi.
            </p>

            <form onSubmit={handleLogin} className="mt-6 space-y-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">Email</label>
                <input
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-500/20"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-300">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="w-full rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-500/20"
                />
              </div>

              {error && (
                <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center justify-center rounded-xl bg-[#fb5858] px-5 py-3 text-sm font-semibold text-white hover:bg-[#ff6f6f] disabled:opacity-60"
              >
                {loading ? "Masuk..." : "Masuk sebagai admin"}
              </button>
            </form>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="rounded-3xl border border-coal-800 bg-coal-900/80 p-6 shadow-lg shadow-red-950/20">
              <div className="flex items-center justify-between gap-4 flex-wrap">
                <div>
                  <div className="text-xs uppercase tracking-[0.2em] text-red-200">Panel admin</div>
                  <h1 className="mt-2 text-2xl font-extrabold text-white">Daftar usulan klaim</h1>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    setToken(null);
                    window.localStorage.removeItem("waraz-admin-token");
                  }}
                  className="rounded-xl border border-coal-700 bg-coal-950 px-4 py-2 text-sm text-slate-300 hover:border-coal-600"
                >
                  Logout
                </button>
              </div>

              {message && (
                <div className="mt-4 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-200">
                  {message}
                </div>
              )}

              {error && (
                <div className="mt-4 rounded-2xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
                  {error}
                </div>
              )}
            </div>

            {loadingClaims ? (
              <div className="rounded-3xl border border-coal-800 bg-coal-900/80 p-6 text-slate-400">
                Memuat usulan klaim...
              </div>
            ) : claims.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-coal-700 bg-coal-900/60 p-6 text-slate-400">
                Belum ada usulan klaim yang menunggu review.
              </div>
            ) : (
              <div className="space-y-4">
                {claims.map((claim) => (
                  <div key={claim.id} className="rounded-3xl border border-coal-800 bg-coal-900/80 p-5">
                    <div className="flex justify-between gap-4 flex-wrap">
                      <div>
                        <div className="text-[11px] uppercase tracking-[0.2em] text-red-200">
                          {claim.status}
                        </div>
                        <h2 className="mt-2 text-xl font-bold text-white">{claim.claim}</h2>
                      </div>

                      <div className="text-xs text-slate-400">
                        {claim.anonymous ? "Anonim" : claim.submitter_alias || "Publik"}
                      </div>
                    </div>

                    <div className="mt-4 text-sm text-slate-300 whitespace-pre-wrap">{claim.summary || "Tidak ada ringkasan tambahan."}</div>

                    <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-400">
                      <div>kategori: {claim.category || "lainnya"}</div>
                      <div>sumber: {claim.source || "input_pengguna"}</div>
                      <div>dibuat: {new Date(claim.created_at).toLocaleString("id-ID")}</div>
                    </div>

                    {claim.source_url && (
                      <a
                        href={claim.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mt-4 inline-block text-xs text-red-200 underline underline-offset-4"
                      >
                        Lihat sumber eksternal
                      </a>
                    )}

                    <div className="mt-5 flex flex-col md:flex-row gap-3">
                      <textarea
                        id={`note-${claim.id}`}
                        placeholder="Catatan review admin..."
                        className="flex-1 rounded-2xl border border-coal-700 bg-coal-950/80 p-3 text-sm text-slate-100 outline-none focus:border-red-400 focus:ring-2 focus:ring-red-500/20"
                      />

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={async () => {
                            const note = (
                              document.getElementById(`note-${claim.id}`) as HTMLTextAreaElement | null
                            )?.value ?? "";
                            await handleReview(claim.id, "approve", note);
                          }}
                          className="inline-flex items-center gap-2 rounded-xl bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-400"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                          Setujui
                        </button>

                        <button
                          type="button"
                          onClick={async () => {
                            const note = (
                              document.getElementById(`note-${claim.id}`) as HTMLTextAreaElement | null
                            )?.value ?? "";
                            await handleReview(claim.id, "reject", note);
                          }}
                          className="inline-flex items-center gap-2 rounded-xl bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-400"
                        >
                          <XCircle className="w-4 h-4" />
                          Tolak
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
