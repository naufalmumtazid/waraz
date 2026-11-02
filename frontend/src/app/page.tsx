import Link from "next/link";
import { Video, ArrowRight, ShieldCheck, Database, Network } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold">
              W
            </div>
            <div>
              <span className="font-bold tracking-tight text-white text-base">
                WARAZ
              </span>
              <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                Cyber Intelligence Platform
              </span>
            </div>
          </div>

          <div className="text-xs text-slate-400">
            Deteksi Koordinasi, Klarifikasi Narasi
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-6 py-20 flex-1 flex flex-col justify-center">
        <div className="space-y-6 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium">
            <ShieldCheck className="w-4 h-4" />
            Platform Forensik Disinformasi Terpadu
          </div>

          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
            WARAZ <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
              Deteksi Koordinasi, Klarifikasi Narasi.
            </span>
          </h1>

          <p className="text-base text-slate-400 leading-relaxed max-w-2xl">
            Lapisan analisis intelijen siber untuk memvalidasi fakta, melacak jejak
            daur ulang video lama di luar konteks aslinya, serta memetakan jaringan
            manipulasi narasi terkoordinasi secara aman dan transparan.
          </p>
        </div>

        {/* Feature Navigation Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-14">
          {/* Feature 2 Active Card */}
          <Link
            href="/video-recycle"
            className="group p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-900/80 transition shadow-lg relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 p-4">
              <span className="px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[11px] font-mono">
                Fitur 2 Aktif
              </span>
            </div>

            <div className="w-12 h-12 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-5 group-hover:scale-105 transition">
              <Video className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-white group-hover:text-blue-400 transition flex items-center gap-2">
              Pelacak Video Daur Ulang
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
            </h3>

            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Mendeteksi penggunaan kembali video lama yang disebarkan ulang
              dengan narasi atau konteks palsu menggunakan perceptual hashing
              (pHash & dHash) dan sequence alignment matching.
            </p>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center gap-4 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-blue-400" />
                PostgreSQL Neon
              </span>
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                FastAPI REST Engine
              </span>
            </div>
          </Link>

          {/* Placeholder for Upcoming Features */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/60 opacity-70">
            <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 mb-5">
              <Network className="w-6 h-6" />
            </div>

            <h3 className="text-lg font-bold text-slate-300">
              Peta Koordinasi & Klarifikasi Isu
            </h3>

            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Fitur 1 (Cek Fakta Semantik) & Fitur 4 (Pendeteksi Koordinasi Jaringan
              Buzzer / CIB) dalam roadmap integrasi modular WARAZ.
            </p>

            <div className="mt-5 pt-4 border-t border-slate-800/80 text-[11px] text-slate-500">
              Modul analisis jaringan dan taksonomi manipulasi narasi.
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        WARAZ Platform © 2026 — Advanced Cyber Disinformation Analysis Engine
      </footer>
    </div>
  );
}
