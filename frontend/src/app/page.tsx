import Link from "next/link";
import {
  Video,
  ArrowRight,
  ShieldCheck,
  Database,
  Network,
  MessageSquareText,
  BrainCircuit,
  FileCheck2,
} from "lucide-react";
import logoImg from "@/assets/logo.png";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen text-slate-100 flex flex-col font-sans">
      <header className="border-b border-red-900/40 bg-coal-900/60 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src={logoImg} alt="logo waraz" width={400} height={400} className="max-w-24" />
          </div>

          <div className="text-xs text-slate-300">
            Deteksi Koordinasi, Klarifikasi Narasi
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-16 flex-1 flex flex-col justify-center">
        <div className="space-y-6 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-medium">
            <ShieldCheck className="w-4 h-4" />
            Platform Forensik Disinformasi Terpadu
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight leading-tight">
            <span className="text-red-400 [text-shadow:0_0_35px_rgba(248,113,113,0.5)]">
              WARAZ
            </span>
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400">
              Deteksi Koordinasi, Klarifikasi Narasi.
            </span>
          </h1>

          <p className="text-base text-slate-400 leading-relaxed max-w-2xl">
            Lapisan analisis intelijen siber untuk memvalidasi klaim publik, melacak penggunaan ulang video lama di luar konteks aslinya, serta memetakan teknik manipulasi dan rekayasa narasi dengan bukti yang transparan.
          </p>
        </div>

        {/* Grid Fitur Utama */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          {/* F1 */}
          <Link
            href="/issue-clarification"
            className="group p-6 rounded-2xl bg-coal-900 border border-coal-800 hover:border-red-500/50 hover:bg-coal-900/80 transition shadow-lg relative overflow-hidden flex flex-col justify-between"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-[11px] font-mono">
                F1 Aktif
              </span>
            </div>

            <div>
              <div className="w-12 h-12 rounded-xl bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-400 mb-5 group-hover:scale-105 transition">
                <MessageSquareText className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-bold text-white group-hover:text-red-400 transition flex items-center gap-2">
                Cek Klarifikasi Isu
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
              </h3>

              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Memeriksa kebenaran klaim publik terhadap basis data klarifikasi terkurasi dan melihat apakah isu sudah dibantah fakta.
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-coal-800/80 flex items-center gap-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-red-400" />
                Pencocokan semantik
              </span>
            </div>
          </Link>

          {/* F2 */}
          <Link
            href="/video-recycle"
            className="group p-6 rounded-2xl bg-coal-900 border border-coal-800 hover:border-red-500/50 hover:bg-coal-900/80 transition shadow-lg relative overflow-hidden flex flex-col justify-between"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-[11px] font-mono">
                F2 Aktif
              </span>
            </div>

            <div>
              <div className="w-12 h-12 rounded-xl bg-red-600/20 border border-red-500/30 flex items-center justify-center text-red-400 mb-5 group-hover:scale-105 transition">
                <Video className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-bold text-white group-hover:text-red-400 transition flex items-center gap-2">
                Pelacak Video Daur Ulang
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
              </h3>

              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Mendeteksi video lama yang dipakai ulang di luar konteks asli melalui perceptual hashing dan kecocokan urutan frame.
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-coal-800/80 flex items-center gap-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-red-400" />
                Dual-hash pHash & dHash
              </span>
            </div>
          </Link>

          {/* F3 */}
          <Link
            href="/manipulation-map"
            className="group p-6 rounded-2xl bg-coal-900 border border-coal-800 hover:border-red-500/50 hover:bg-coal-900/80 transition shadow-lg relative overflow-hidden flex flex-col justify-between"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="px-2.5 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-[11px] font-mono">
                F3 Aktif
              </span>
            </div>

            <div>
              <div className="w-12 h-12 rounded-xl bg-orange-600/20 border border-orange-500/30 flex items-center justify-center text-orange-400 mb-5 group-hover:scale-105 transition">
                <BrainCircuit className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-bold text-white group-hover:text-orange-400 transition flex items-center gap-2">
                Peta Teknik Manipulasi
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
              </h3>

              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Memetakan 9 taksonomi pola manipulasi psikologis (urgensi palsu, framing ancaman, ilusi konsensus, dsb) dengan sorotan bukti.
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-coal-800/80 flex items-center gap-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <FileCheck2 className="w-3.5 h-3.5 text-orange-400" />
                9 Taksonomi & Kontra-Contoh
              </span>
            </div>
          </Link>

          {/* F4 & F5 Roadmap Preview */}
          <div className="md:col-span-3 p-6 rounded-2xl bg-coal-900/40 border border-coal-800/60 opacity-80 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-coal-800 border border-coal-700 flex items-center justify-center text-slate-400 flex-shrink-0">
                <Network className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-200">
                  Modul Lanjutan: Peta Koordinasi Jaringan (F4) & Mitigasi (F5)
                </h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  Analisis seeder & jembatan buzzer CIB serta pembuatan paket bukti kartu klarifikasi terverifikasi.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3 flex-shrink-0">
              <Link
                href="/admin/claims"
                className="rounded-xl border border-coal-700 bg-coal-900 px-4 py-2 text-xs text-slate-300 hover:border-coal-600 transition"
              >
                Panel Admin Review
              </Link>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-coal-800/80 py-6 text-center text-xs text-slate-500">
        WARAZ Platform © 2026 — Advanced Cyber Disinformation Analysis Engine
      </footer>
    </div>
  );
}
