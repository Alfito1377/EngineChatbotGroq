import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools.db_tool import alat_baca_database
from tools.doc_tool import alat_baca_dokumen
from langchain_core.messages import SystemMessage

# 1. Muat Environment
load_dotenv()

# 2. Inisialisasi LLM Secara Global
# Pastikan menggunakan model Groq yang stabil untuk ReAct (misal: llama3-70b-8192 atau mixtral-8x7b-32768)
llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

daftar_alat = [alat_baca_database, alat_baca_dokumen]

# 3. Instruksi Sistem (Disuntikkan secara native ke LangGraph)
instruksi_sistem = """Kamu adalah asisten AI internal PT Sage Mashlahat Indonesia.
Tugas utamamu adalah merespons pertanyaan pengguna dengan cepat dan memilih SATU alat yang paling tepat.

ATURAN MUTLAK:
1. DATABASE (alat_baca_database): Gunakan HANYA untuk pertanyaan seputar data transaksi, metrik, status, angka, atau isi tabel (misal: "data driver", "jumlah pengiriman", "stok di toko").
2. DOKUMEN (alat_baca_dokumen): Gunakan HANYA untuk pertanyaan konseptual seperti pedoman, kebijakan, SOP, atau regulasi perusahaan.
3. DILARANG BOLAK-BALIK ALAT. Cukup pilih 1 alat yang paling relevan, ambil datanya, buat kesimpulan, dan BERHENTI mencari.
4. Jika pertanyaan ambigu atau tidak jelas, JANGAN panggil alat apa pun. Langsung tanya pengguna agar lebih spesifik.
5. Susun jawaban akhir menggunakan Markdown yang rapi (gunakan poin-poin atau tabel jika perlu).
"""

# 4. Tambahkan Memori Internal (Checkpointer)
# Ini membuat agen ingat konteks percakapan sebelumnya
memory = MemorySaver()

# 5. Inisialisasi Agen Secara Global
# Menggunakan state_modifier lebih direkomendasikan di LangGraph daripada memasukkan prompt ke dalam messages manual
agent_executor = create_react_agent(
    llm, 
    tools=daftar_alat, 
    checkpointer=memory
)

# 6. Fungsi Utama
# 6. Fungsi Utama
def tanya_agen(pertanyaan_user: str, thread_id: str = "sesi_default") -> str:
    try:
        # Konfigurasi sesi memori
        config = {"configurable": {"thread_id": thread_id}}

        # Panggil agen dengan menyertakan instruksi sistem di awal
        respons = agent_executor.invoke(
            {"messages": [
                SystemMessage(content=instruksi_sistem),
                ("user", pertanyaan_user)
            ]},
            config=config
        )

        # MENGAMBIL JAWABAN AKHIR
        jawaban_mentah = respons["messages"][-1].content

        # PROSES EKSTRAKSI
        if isinstance(jawaban_mentah, str):
            jawaban_ai = jawaban_mentah
        elif isinstance(jawaban_mentah, list):
            jawaban_ai = "".join([
                bagian.get("text", "") if isinstance(bagian, dict) else str(bagian) 
                for bagian in jawaban_mentah
            ])
        else:
            jawaban_ai = str(jawaban_mentah)

        return jawaban_ai

    except Exception as e:
        return f"Maaf, agen mengalami kendala: {str(e)}"