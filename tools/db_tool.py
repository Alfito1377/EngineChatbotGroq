import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq

load_dotenv()
url_database = os.getenv("DATABASE_URL")

tabel_penting = [
    "delivery_receipt_details",
    "delivery_receipts",
    "driver",
    "logistic",
    "vehicle"
]

db = SQLDatabase.from_uri(
    url_database,
    include_tables=tabel_penting,
    sample_rows_in_table_info=0  
)
llm_sql = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0 
)

@tool
def alat_baca_database(pertanyaan: str) -> str:
    """
    Gunakan alat ini HANYA jika pengguna bertanya tentang data metrik, angka, 
    dashboard, tabel, atau database visualisasi perusahaan.
    """
    print("🤖 [Sistem]: Agen sedang membuka database MySQL...")
    try:
        skema_tabel = db.get_table_info()
        
        prompt = f"""
        Diberikan skema tabel MySQL berikut:
        {skema_tabel}
        
        Tuliskan HANYA query SQL yang valid (tanpa penjelasan, tanpa format markdown) 
        untuk menjawab pertanyaan ini: "{pertanyaan}"
        """
        
        respons_ai = llm_sql.invoke(prompt)
        query_bersih = respons_ai.content.strip().replace("```sql", "").replace("```", "")
        
        hasil_eksekusi = db.run(query_bersih)
        
        return f"Berikut adalah data mentah dari database: {hasil_eksekusi}"
        
    except Exception as e:
        return f"Gagal mengambil data dari database. Error: {str(e)}"