import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent

from tools.db_tool import alat_baca_database
from tools.doc_tool import alat_baca_dokumen

load_dotenv()

def inisialisasi_agen():
    llm = ChatGroq(
        model="openai/gpt-oss-120b", 
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0
    )

    daftar_alat = [alat_baca_database, alat_baca_dokumen]

    agent_executor = create_react_agent(llm, daftar_alat)
    
    return agent_executor

def tanya_agen(pertanyaan_user: str) -> str:
    instruksi_sistem = (
        "Kamu adalah asisten AI internal yang cerdas. "
        "Jika pengguna bertanya tentang angka/metrik perusahaan, selalu gunakan alat_baca_database. "
        "Jika pengguna bertanya tentang isi dokumen/SOP, selalu gunakan alat_baca_dokumen. "
        "Jawablah dalam bahasa Indonesia yang natural dan ramah."
    )
    
    try:
        agen = inisialisasi_agen()
        
        respons = agen.invoke({
            "messages": [
                ("system", instruksi_sistem),
                ("user", pertanyaan_user)
            ]
        })
        
        jawaban_ai = respons["messages"][-1].content
        return jawaban_ai
        
    except Exception as e:
        return f"Maaf, agen mengalami kendala: {str(e)}"