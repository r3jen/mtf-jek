# MTF-JEK - Aplikasi Evaluasi PKPP

Aplikasi Streamlit untuk evaluasi agreement dengan sistem scoring tertimbang.

## Persyaratan

- Python 3.8+
- pip

## Instalasi

1. Clone repository ini
2. Install dependencies:

```bash
pip install streamlit pandas
```

## Menjalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## Login

### Admin
- Username: `admin`
- Password: `admin123`

### User
- Dibuat oleh admin melalui menu "Kelola User"

## Fitur

### Admin Dashboard
- Upload data agreements (Excel)
- Upload data pertanyaan/bobot evaluasi (Excel)
- Kelola user
- Lihat hasil evaluasi

### User Dashboard
- Lihat daftar agreement yang di-assign
- Isi evaluasi dengan skor 1-5
- Lihat riwayat evaluasi

## Struktur Database

Database SQLite (`data.db`) dengan tabel:
- `users` - Data user
- `agreements` - Data agreement
- `pkpp_questions` - Pertanyaan dan bobot evaluasi
- `evaluations` - Header evaluasi (total bobot, skor tertimbang, final score)
- `evaluation_answers` - Detail jawaban per pertanyaan

## Perhitungan Score

- **Total Bobot**: Jumlah semua bobot pertanyaan
- **Total Skor Tertimbang**: Σ (skor × bobot) untuk setiap jawaban
- **Final Score (%)**: (Total Skor Tertimbang / (Total Bobot × 5)) × 100
