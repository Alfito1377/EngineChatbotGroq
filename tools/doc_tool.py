import os
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. Menentukan lokasi penyimpanan database vektor
LOKASI_DB = "./vector_db"

# 2. Inisialisasi Embedding (Penerjemah teks manusia menjadi vektor angka)
embedding_gratis = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def simpan_dokumen_ke_db(file_path: str, nama_file: str):
    """Fungsi ini dipanggil oleh main.py saat ada file PDF baru yang diunggah dari Laravel"""
    try:
        if not file_path.endswith(".pdf"):
            return f"Format belum didukung di uji coba ini: {nama_file}"

        # A. Baca file PDF
        loader = PyPDFLoader(file_path)
        dokumen_mentah = loader.load()
        
        # B. Potong teks menjadi bagian kecil agar muat di ingatan AI (Context Window)
        pemotong = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        potongan_teks = pemotong.split_documents(dokumen_mentah)

        # C. Ubah potongan teks menjadi angka (embedding) dan simpan permanen ke ChromaDB
        Chroma.from_documents(
            documents=potongan_teks, 
            embedding=embedding_gratis, 
            persist_directory=LOKASI_DB
        )
        return "✅ Dokumen berhasil dianalisis dan disimpan ke memori AI."
        
    except Exception as e:
        return f"Gagal memproses dokumen: {str(e)}"


@tool
def alat_baca_dokumen(pertanyaan: str) -> str:
    """
    Gunakan alat ini HANYA JIKA pengguna bertanya tentang informasi dari dokumen, 
    laporan, pedoman, atau file yang telah diunggah.
    """
    print("🤖 [Sistem]: Agen sedang mencari di database dokumen (ChromaDB)...")
    try:
        # Buka brankas database vektor
        db_vektor = Chroma(persist_directory=LOKASI_DB, embedding_function=embedding_gratis)
        
        # Lakukan Semantic Search dan ambil 4 potongan dokumen paling mirip (k=4)
        hasil_pencarian = db_vektor.similarity_search(pertanyaan, k=4)
        
        if not hasil_pencarian:
            return "Maaf, tidak ditemukan informasi yang relevan di dokumen."
            
        # Gabungkan 4 potongan teks tersebut menjadi satu paragraf panjang untuk dibaca AI
        teks_konteks = "\n\n".join([doc.page_content for doc in hasil_pencarian])
        return f"Informasi dari dokumen:\n{teks_konteks}"
        
    except Exception as e:
        return f"Gagal membaca dokumen. Error: {str(e)}"