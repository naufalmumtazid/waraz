const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface VideoInfo {
  fps: number;
  total_frame: number;
  durasi_detik: number;
  lebar: number;
  tinggi: number;
}

export interface ArchiveRecord {
  id: string;
  judul: string;
  durasi_detik?: number;
  fps?: number;
  lebar?: number;
  tinggi?: number;
  total_frame?: number;
  tanggal_asli?: string | null;
  sumber?: string | null;
  tautan?: string | null;
  thumbnail_filename?: string | null;
  dibuat_pada?: string;
}

export interface MatchedPair {
  query_idx: number;
  archive_idx: number;
  dist_phash: number;
  dist_dhash?: number;
  mirip: boolean;
}

export interface DetectionResult {
  status: "daur_ulang" | "tidak_ditemukan" | "tidak_dapat_dianalisis";
  arsip_tercocok?: ArchiveRecord | null;
  skor: number;
  keyakinan: "sangat tinggi" | "tinggi" | "sedang" | "rendah" | "tidak ada";
  frame_cocok: number;
  frame_total: number;
  consecutive_run: number;
  avg_hamming: number;
  catatan: string;
  query_thumbnail_filename?: string;
  info_video?: VideoInfo;
  detail_pasangan?: MatchedPair[];
}

export const videoApi = {
  getThumbnailUrl: (type: "arsip" | "temp", filename: string) => {
    return `${API_BASE_URL}/api/v1/video/thumbnail/${type}/${filename}`;
  },

  listArchives: async (): Promise<ArchiveRecord[]> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/video/arsip`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error("Gagal mengambil daftar arsip dari server.");
    }
    return res.json();
  },

  deleteArchive: async (id: string): Promise<{ status: string; pesan: string }> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/video/arsip/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal menghapus arsip.");
    }
    return res.json();
  },

  seedDemo: async () => {
    const res = await fetch(`${API_BASE_URL}/api/v1/video/seed-demo`, {
      method: "POST",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal melakukan seeding demo.");
    }
    return res.json();
  },

  detectVideo: async (
    file: File,
    kasusId?: string
  ): Promise<DetectionResult> => {
    const formData = new FormData();
    formData.append("file", file);
    if (kasusId) formData.append("kasus_id", kasusId);

    const res = await fetch(`${API_BASE_URL}/api/v1/video/deteksi`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal melakukan deteksi video.");
    }
    return res.json();
  },

  registerArchive: async (params: {
    file: File;
    judul: string;
    tanggal_asli?: string;
    sumber?: string;
    tautan?: string;
  }): Promise<ArchiveRecord> => {
    const formData = new FormData();
    formData.append("file", params.file);
    formData.append("judul", params.judul);
    if (params.tanggal_asli) formData.append("tanggal_asli", params.tanggal_asli);
    if (params.sumber) formData.append("sumber", params.sumber);
    if (params.tautan) formData.append("tautan", params.tautan);

    const res = await fetch(`${API_BASE_URL}/api/v1/video/arsip`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal mendaftarkan video ke arsip.");
    }
    return res.json();
  },
};
