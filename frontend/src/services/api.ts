const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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

export interface ClarificationMatch {
  id: string;
  claim: string;
  status: string;
  summary: string;
  date: string;
  source: string;
  url: string;
  score: number;
}

export interface IssueClarificationResponse {
  status_result:
    | "sudah_diklarifikasi"
    | "ditemukan_mirip"
    | "belum_ditemukan"
    | "tidak_ada_isi";
  status_hasil?: string;
  score: number;
  matches: ClarificationMatch[];
  note: string;
}

export interface PublicClaimSubmission {
  id: string;
  claim: string;
  summary: string;
  category: string;
  source: string;
  source_url: string;
  anonymous: boolean;
  submitter_alias: string | null;
  status: string;
  review_note: string | null;
  created_at: string;
  reviewed_at: string | null;
}

export const issueClarificationApi = {
  check: async (issue: string): Promise<IssueClarificationResponse> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/clarification/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ issue }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Failed to evaluate issue clarification.");
    }

    return res.json();
  },
};

export const claimSubmissionApi = {
  submit: async (payload: {
    claim: string;
    summary?: string;
    source?: string;
    source_url?: string;
    category?: string;
    anonymous?: boolean;
    submitter_alias?: string;
  }) => {
    const res = await fetch(`${API_BASE_URL}/api/v1/clarification/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal mengirim usulan klaim.");
    }

    return res.json();
  },
};

export const adminClaimsApi = {
  login: async (payload: { email: string; password: string }) => {
    const res = await fetch(`${API_BASE_URL}/api/v1/clarification/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Login admin gagal.");
    }

    return res.json() as Promise<{ token: string; message: string }>;
  },

  list: async (token: string): Promise<PublicClaimSubmission[]> => {
    const res = await fetch(`${API_BASE_URL}/api/v1/clarification/admin/claims`, {
      headers: {
        "x-admin-token": token,
      },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal memuat daftar usulan klaim.");
    }

    return res.json();
  },

  review: async (
    token: string,
    claimId: string,
    decision: "approve" | "reject",
    reviewNote: string
  ) => {
    const res = await fetch(
      `${API_BASE_URL}/api/v1/clarification/admin/claims/${claimId}/review`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-token": token,
        },
        body: JSON.stringify({ decision, review_note: reviewNote }),
      }
    );

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Gagal mengupdate status usulan klaim.");
    }

    return res.json();
  },
};

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
