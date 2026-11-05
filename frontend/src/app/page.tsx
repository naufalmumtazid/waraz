import Link from "next/link";
import { Video, ArrowRight, ShieldCheck, Database, Network, MessageSquareText } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <header className="border-b border-red-500/20 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#fb5858]/15 border border-[#fb5858]/30 flex items-center justify-center text-[#ff8686] font-bold">
              W
            </div>
            <div>
              <span className="font-bold tracking-tight text-white text-base">
                WARAZ
              </span>
              <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
                Cyber Intelligence Platform
              </span>
            </div>
          </div>

          <div className="text-xs text-slate-300">
            Deteksi Koordinasi, Klarifikasi Narasi
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-20 flex-1 flex flex-col justify-center">
        <div className="space-y-6 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#fb5858]/10 border border-[#fb5858]/20 text-[#ff9a9a] text-xs font-medium">
            <ShieldCheck className="w-4 h-4" />
            Platform Forensik Disinformasi Terpadu
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            WARAZ <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#fb5858] to-[#ffb4b4]">
              Deteksi Koordinasi, Klarifikasi Narasi.
            </span>
          </h1>

          <p className="text-base text-slate-400 leading-relaxed max-w-2xl">
            Lapisan analisis intelijen siber untuk memvalidasi klaim, memantau video yang dipakai ulang di luar konteks aslinya, serta memetakan pola manipulasi narasi yang terkoordinasi dengan bukti yang jelas.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-14">
          <Link
            href="/issue-clarification"
            className="group p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-[#fb5858]/50 hover:bg-slate-900/80 transition shadow-lg relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="px-2.5 py-1 rounded-full bg-[#fb5858]/10 border border-[#fb5858]/20 text-[#ff9a9a] text-[11px] font-mono">
                F1 Aktif
              </span>
            </div>

            <div className="w-12 h-12 rounded-xl bg-[#fb5858]/15 border border-[#fb5858]/30 flex items-center justify-center text-[#ff9a9a] mb-5 group-hover:scale-105 transition">
              <MessageSquareText className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-white group-hover:text-[#ff9a9a] transition flex items-center gap-2">
              Cek Klarifikasi Isu
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
            </h3>

            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Membandingkan klaim yang beredar dengan basis data klarifikasi terkurasi dan melihat apakah isu tersebut sudah dibantah atau perlu peninjauan analis.
            </p>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-[#ff9a9a]" />
                Pencocokan berbasis bukti
              </span>
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-[#ff9a9a]" />
                Basis pengetahuan terkurasi
              </span>
            </div>
          </Link>

          <Link
            href="/video-recycle"
            className="group p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-red-400/50 hover:bg-slate-900/80 transition shadow-lg relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="px-2.5 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-200 text-[11px] font-mono">
                F2 Aktif
              </span>
            </div>

            <div className="w-12 h-12 rounded-xl bg-red-500/15 border border-red-400/30 flex items-center justify-center text-red-200 mb-5 group-hover:scale-105 transition">
              <Video className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-white group-hover:text-red-200 transition flex items-center gap-2">
              Pelacak Video Daur Ulang
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
            </h3>

            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Mendeteksi video yang dipakai ulang dalam konteks yang salah atau dimanipulasi dengan hashing persepsi dan pencocokan urutan frame.
            </p>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-red-200" />
                PostgreSQL Neon
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-red-200" />
                FastAPI REST Engine
              </span>
            </div>
          </Link>

          <div className="md:col-span-2 p-6 rounded-2xl bg-slate-900/40 border border-slate-800/60 opacity-80">
            <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 mb-5">
              <Network className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-slate-300">
              Pemetaan Jaringan & Narasi Terkoordinasi
            </h3>

            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Fitur 4 (deteksi koordinasi CIB / buzzer) dan alur cek fakta semantik masih berada dalam roadmap modular untuk analisis narasi yang lebih dalam.
            </p>

            <div className="mt-5 pt-4 border-t border-slate-800/80 text-[11px] text-slate-500">
              Modul analisis jaringan dan taksonomi manipulasi narasi masih dalam roadmap integrasi.
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-4">
          <Link
            href="/admin/claims"
            className="rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-200 hover:border-slate-500 transition"
          >
            Panel admin review
          </Link>
        </div>
      </main>

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        WARAZ Platform © 2026 — Advanced Cyber Disinformation Analysis Engine
      </footer>
    </div>
  );
}
