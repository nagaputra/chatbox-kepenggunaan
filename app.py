import streamlit as st
from google import genai
from google.genai import types

# Tetapan Halaman Web
st.set_page_config(page_title="Pembantu Kepenggunaan & Gaya Hidup AI", page_icon="🛍️")
st.title("🛍️ Pembantu Kepenggunaan & Gaya Hidup AI")
st.write("Tanyakan soalan berkaitan hak pengguna, aduan KPDN/TTPM, cadangan makanan sihat, isu kesihatan, atau penipuan (scam).")

# Input API Key di Sidebar
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Peranan & Panduan AI
SYSTEM_INSTRUCTION = """
Anda ialah Pembantu AI Kepenggunaan dan Gaya Hidup Pintar di Malaysia.
Tugas utama anda adalah membantu pengguna dalam pelbagai topik kepenggunaan yang luas:
1. HAK PENGGUNA & ADUAN: Panduan Akta Perlindungan Pengguna, aduan KPDN, Tribunal Tuntutan Pengguna (TTPM), kes scam/NSRC 997.
2. MAKANAN & KESIHATAN: Cadangan pilihan makanan sihat, semakan isu keselamatan makanan, kesedaran status halal, isu kesihatan am.
3. ISU PENGGUNA AM: Hak pembeli barangan rosak, isu harga barangan, perbelanjaan berhemat.

Gaya jawapan mesra, profesional, bertatasusila, praktikal dan berfakta dalam Bahasa Melayu.
"""

# Sejarah Perbualan
if "messages" not in st.session_state:
    st.session_state.messages = []

# Paparkan mesej lama
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Pengguna
if user_input := st.chat_input("Tanya soalan anda di sini..."):
    if not api_key:
        st.error("Sila masukkan Gemini API Key di bahagian menu sisi dahulu!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                client = genai.Client(api_key=api_key.strip())
                
                # Format sejarah perbualan
                contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

                # Menggunakan model aktif
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION.strip(),
                        temperature=0.7,
                    )
                )
                
                bot_reply = response.text
                message_placeholder.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "Quota exceeded" in err_str:
                    st.warning("⏳ Had kuota percuma penuh seketika. Sila tunggu 1 minit dan cuba hantar soalan semula.")
                else:
                    st.error(f"Ralat sistem: {err_str}")
