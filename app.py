import streamlit as st
import time
from google import genai
from google.genai import types

# Tetapan Halaman Web
st.set_page_config(page_title="Pembantu Kepenggunaan & Gaya Hidup AI", page_icon="🛍️")
st.title("🛍️ Pembantu Kepenggunaan & Gaya Hidup AI")
st.write("Tanyakan soalan berkaitan hak pengguna, aduan KPDN/TTPM, cadangan makanan sihat, isu kesihatan, atau penipuan (scam).")

# Dapatkan API Key daripada Streamlit Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "")

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
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if not API_KEY:
            st.error("API Key belum disetkan di bahagian Secrets Streamlit.")
        else:
            contents = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

            bot_reply = None
            last_error = ""

            for attempt in range(3):
                try:
                    client = genai.Client(api_key=API_KEY.strip())
                    response = client.models.generate_content(
                        model="gemini-3.7-flash",
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION.strip(),
                            temperature=0.7,
                        )
                    )
                    bot_reply = response.text
                    break
                except Exception as e:
                    err_str = str(e)
                    last_error = err_str
                    if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower():
                        time.sleep(2 * (attempt + 1))
                        continue
                    else:
                        break

            if bot_reply:
                message_placeholder.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                if "RESOURCE_EXHAUSTED" in last_error or "Quota exceeded" in last_error:
                    st.warning("⏳ Had kuota percuma penuh seketika. Sila tunggu 1 minit dan cuba hantar soalan semula.")
                else:
                    st.error(f"Ralat sistem: {last_error}")
