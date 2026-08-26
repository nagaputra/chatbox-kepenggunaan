import streamlit as st
import requests

# ---------- KONFIGURASI HALAMAN ----------
st.set_page_config(
    page_title="Tanya Pengguna",
    page_icon="🧾",
    layout="centered",
)

# ---------- GAYA (TEMA RESIT) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
.stApp {
    background: #EDE9DC;
}
.block-container {
    background: #F6F3EA;
    max-width: 640px;
    padding: 2rem 2rem 1rem;
    box-shadow: 0 2px 0 #CFC9B6, 0 30px 60px -25px rgba(32,30,26,0.35);
}
.receipt-header {
    text-align: center;
    border-bottom: 1px dashed #CFC9B6;
    padding-bottom: 16px;
    margin-bottom: 12px;
}
.eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: .18em;
    color: #6E6A5C;
    text-transform: uppercase;
}
.receipt-title {
    font-family: 'Space Mono', monospace;
    font-size: 28px;
    letter-spacing: .06em;
    margin: 6px 0 4px;
    color: #201E1A;
}
.receipt-sub {
    font-size: 13px;
    color: #6E6A5C;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.5;
}
.disclaimer-box {
    border: 1px solid #CFC9B6;
    background: #FFFDF8;
    padding: 10px 12px;
    font-size: 12px;
    line-height: 1.5;
    color: #6E6A5C;
    margin-bottom: 14px;
}
.disclaimer-box b { color: #B0272B; }
.stamp {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 9.5px;
    letter-spacing: .1em;
    color: #B0272B;
    border: 1.5px solid #B0272B;
    padding: 2px 6px;
    margin-top: 4px;
    transform: rotate(-3deg);
    opacity: .8;
}
[data-testid="stChatMessage"] {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# ---------- KEPALA RESIT ----------
st.markdown("""
<div class="receipt-header">
    <div class="eyebrow">Resit Bantuan Rasmi</div>
    <div class="receipt-title">TANYA PENGGUNA</div>
    <div class="receipt-sub">Sistem AI untuk soalan kepenggunaan, keselamatan makanan, kesihatan am &amp; nasihat harian — hak pengguna, waranti, aduan, penipuan, dan lebih lagi.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box">
⚠️ <b>Peringatan:</b> Sistem ini memberi panduan umum sahaja, bukan nasihat undang-undang atau perubatan rasmi.
Untuk isu kesihatan serius, jumpa doktor; untuk tuntutan formal, rujuk Tribunal Tuntutan Pengguna Malaysia (TTPM) atau KPDN.
</div>
""", unsafe_allow_html=True)

# ---------- SYSTEM PROMPT ----------
SYSTEM_PROMPT = """Anda ialah "Tanya Pengguna", sistem bantuan AI serba boleh yang membantu pengguna di Malaysia dengan pelbagai soalan harian — bermula daripada asas kepenggunaan (consumer affairs), dan turut merangkumi topik berkaitan seperti keselamatan makanan, kesihatan am, cadangan produk, dan nasihat praktikal harian yang lain.

BIDANG UTAMA (paling pakar):
- Hak dan tanggungjawab pengguna di Malaysia, Akta Pelindungan Pengguna 1999 (APP 1999)
- Waranti, jaminan produk, bayaran balik (refund), pertukaran barang
- Aduan terhadap peniaga, produk cacat/rosak, Tribunal Tuntutan Pengguna Malaysia (TTPM)
- KPDNHEP, penipuan (scam), e-dagang, iklan mengelirukan, amalan perniagaan tidak adil
- Hak pengguna perkhidmatan (telko, utiliti, insurans, perbankan)

BIDANG SAMPINGAN (boleh jawab juga, bantu dengan baik):
- Keselamatan makanan (contoh: makanan luput/expired, cara simpan makanan, tanda makanan rosak)
- Soalan kesihatan am / gaya hidup sihat yang tidak memerlukan diagnosis perubatan khusus
- Cadangan produk, tips penjimatan, panduan pembelian bijak
- Soalan am harian yang lain yang pengguna tanya

CARA JAWAB:
- Jawab terus dengan berguna dan praktikal — jangan tolak soalan hanya kerana ia bukan tepat hal kepenggunaan
- Untuk isu kesihatan/perubatan yang serius atau spesifik, beri panduan am sahaja dan galakkan berjumpa doktor/pihak berkuasa berkaitan — jangan beri diagnosis atau nasihat perubatan muktamad
- Untuk isu keselamatan makanan, beri panduan praktikal berdasarkan amalan keselamatan makanan am
- Jika soalan berkaitan kepenggunaan, gabungkan sudut hak pengguna bersama nasihat praktikal lain
- HANYA tolak dengan sopan soalan yang benar-benar tiada kaitan dengan kehidupan harian/kepenggunaan/kesihatan (contoh: tugasan coding, matematik akademik)

GAYA BALASAN:
- Jawab dalam Bahasa Melayu (kecuali pengguna menulis dalam Bahasa Inggeris)
- Jelas, ringkas, praktikal — beri langkah tindakan jika berkaitan
- Untuk isu kesihatan/undang-undang serius, nyatakan ini panduan umum sahaja
- Cadangkan saluran rasmi yang relevan: Tribunal Tuntutan Pengguna Malaysia, KPDNHEP (1-800-886-800, ejen.kpdn.gov.my), KKM untuk isu kesihatan/makanan
- Jangan reka fakta yang anda tidak pasti"""

# ---------- KONFIGURASI GROQ ----------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GROQ_MODEL = "openai/gpt-oss-120b"

def call_groq(messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    payload = {
        "model": GROQ_MODEL,
        "max_tokens": 2000,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

# ---------- STATE PERBUALAN ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- CIP SOALAN PERMULAAN ----------
if not st.session_state.messages:
    st.markdown("**Cuba tanya:**")
    cols = st.columns(2)
    starters = [
        "Barang rosak dalam tempoh waranti, apa hak saya?",
        "Bagaimana cara buat aduan di Tribunal Tuntutan Pengguna?",
        "Cara kenal pasti penipuan beli-belah online",
        "Kedai enggan bagi bayaran balik, apa boleh saya buat?",
    ]
    clicked = None
    for i, s in enumerate(starters):
        with cols[i % 2]:
            if st.button(s, key=f"starter_{i}", use_container_width=True):
                clicked = s
    if clicked:
        st.session_state.messages.append({"role": "user", "content": clicked})
        st.rerun()

# ---------- PAPAR SEJARAH ----------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🧾"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            st.markdown('<span class="stamp">RUJUKAN SAHAJA</span>', unsafe_allow_html=True)

# ---------- INPUT PENGGUNA ----------
user_input = st.chat_input("Taip soalan kepenggunaan anda di sini...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# ---------- JANA JAWAPAN JIKA MESEJ TERAKHIR DARIPADA USER ----------
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    if not GROQ_API_KEY:
        error_text = "Ralat konfigurasi: GROQ_API_KEY belum ditetapkan dalam Streamlit Secrets."
        st.session_state.messages.append({"role": "assistant", "content": error_text})
        st.rerun()
    else:
        with st.chat_message("assistant", avatar="🧾"):
            with st.spinner("Menyemak rekod..."):
                try:
                    reply = call_groq(st.session_state.messages)
                except Exception as e:
                    reply = f"Maaf, berlaku ralat sambungan: {e}\n\nSila cuba tanya semula."
            st.write(reply)
            st.markdown('<span class="stamp">RUJUKAN SAHAJA</span>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": reply})

st.markdown(
    "<div style='text-align:center;font-family:Space Mono,monospace;font-size:10px;color:#6E6A5C;margin-top:20px;'>"
    "SAH TANPA TANDATANGAN · DIJANA OLEH AI · SIMPAN RESIT INI</div>",
    unsafe_allow_html=True,
)
