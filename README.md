# Panduan Deployment - AI Service DDM PT Sage

Dokumen ini berisi langkah-langkah teknis untuk melakukan *deploy* mesin AI (FastAPI & LangChain) ke server VPS berbasis Ubuntu.

---

## 1. Persiapan Server & Instalasi Modul Dasar
Pastikan Anda sudah *login* ke VPS melalui SSH. Jalankan perintah berikut untuk memperbarui sistem dan menginstal perangkat lunak yang dibutuhkan:

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx supervisor unzip -y

## 2. Pemindahan File & Pembuatan Lingkungan Virtual
Kompres folder agent, tools, vector_db, serta file .env, main.py, dan requirements.txt menjadi ai_backend.zip.

Unggah file zip tersebut ke server.

Ekstrak dan siapkan virtual environment:
# Ekstrak file ke direktori server
sudo unzip ai_backend.zip -d /var/www/ai-sage
cd /var/www/ai-sage

# Buat dan aktifkan virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Instal library dari requirements.txt
pip install -r requirements.txt

3. Konfigurasi Kredensial & Hak Akses
Edit kredensial database di dalam file .env:

Sesuaikan DB_HOST dengan IP database MySQL (atau 127.0.0.1 jika dalam satu server).

Pastikan GROQ_API_KEY sudah terisi dengan benar.

Berikan hak akses tulis pada folder vector_db agar sistem ChromaDB dapat memproses dokumen PDF dengan lancar:

Bash
sudo chmod -R 775 /var/www/ai-sage/vector_db
sudo chown -R www-data:www-data /var/www/ai-sage/vector_db
4. Menjalankan AI di Background (Supervisor)
Buat file konfigurasi baru agar FastAPI berjalan otomatis 24/7:

Bash
sudo nano /etc/supervisor/conf.d/ai-sage.conf
Isikan konfigurasi berikut:

Ini, TOML
[program:ai-sage]
directory=/var/www/ai-sage
command=/var/www/ai-sage/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/ai-sage.err.log
stdout_logfile=/var/log/ai-sage.out.log
Simpan file tersebut, lalu nyalakan service:

Bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ai-sage
5. Konfigurasi Nginx (Reverse Proxy)
Buat jembatan agar API tertutup di port 8001 dapat diakses dengan aman:

Bash
sudo nano /etc/nginx/sites-available/ai-sage
Isikan kode berikut:

Nginx
server {
    listen 80;
    server_name api-ai.domainanda.com; # Ganti dengan domain/IP publik Anda

    location / {
        proxy_pass [http://127.0.0.1:8001](http://127.0.0.1:8001);
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
Aktifkan konfigurasi Nginx dan restart:

Bash
sudo ln -s /etc/nginx/sites-available/ai-sage /etc/nginx/sites-enabled/
sudo systemctl restart nginx
6. Penyesuaian Aplikasi Laravel
Langkah terakhir, buka file .env pada proyek Laravel Anda dan perbarui alamat layanannya:

Plaintext
AI_SERVICE_URL=[http://api-ai.domainanda.com](http://api-ai.domainanda.com)
