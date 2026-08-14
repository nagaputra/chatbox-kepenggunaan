import streamlit as st
import requests

# Tetapan Halaman Web
st.set_page_config(page_title="Pembantu Kepenggunaan & Gaya Hidup AI", page_icon="🛍️")
st.title("🛍️ Pembantu Kepenggunaan & Gaya Hidup AI")
st.write("Tanyakan soalan berkaitan hak pengguna, aduan KPDN/TTPM, cadangan makanan sihat, isu kesihatan, atau penipuan (scam).")

# Input API Key di Sidebar
api_key = st.sidebar.text_input("Masukkan Gemini API Key:", type="password")

# Peranan & Panduan AI
SYSTEM_INSTRUCTION = """
Anda ialah Pembantu AI Kepenggunaan dan Gaya Hidup Pintar di Malaysia.
Tugas utama anda adalah membantu pengguna dalam pelbagai topik kepenggunaan yang luas, merangkumi:

1. HAK PENGGUNA & ADUAN: Panduan Akta Perlindungan Pengguna, aduan KPDN, Tribunal Tuntutan Pengguna (TTPM), dan kes scam/NSRC 997.
2. MAKANAN & KESIHATAN: Cadangan pilihan makanan sihat, semakan isu keselamatan makanan, kesedaran status halal, dan panduan membeli barangan dapur berasaskan kesihatan.
3. ISU PENGGUNA AM: Hak pembeli barangan rosak, isu harga barangan, dan nasihat perbelanjaan berhemat.

Gaya jawapan:
- Mesra, profesional, bertatasusila, dan mudah difahami.
- Memberikan cadangan yang praktikal dan berfakta.
- Masukkan penafian mesra bahawa nasihat kesihatan atau perundangan adalah untuk rujukan umum sahaja.
"""

# Sejarah Perbualan
if "messages" not in st.session_state:
    st.session_state.messages = []

# Paparkan mesej terdahulu
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Pengguna
if user_input := st.chat_input("Tanya soalan anda di sini..."):
    if not api_key:
        st.error("Sila masukkan Gemini API Key di bahagian menu sisi (sidebar) dahulu!")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Format perbualan untuk Gemini REST API
            formatted_contents = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                formatted_contents.append({
                    "role": role,
                    "parts": [{"text": m["content"]}]
                })

            payload = {
                "system_instruction": {
                    "parts": [{"text": SYSTEM_INSTRUCTION}]
                },
                "contents": formatted_contents,
                "generationConfig": {
                    "temperature": 0.7
                }
            }

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"

            try:
                response = requests.post(url, json=payload)
                data = response.json()

                if response.status_code == 200 and "candidates" in data:
                    bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
                    message_placeholder.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    error_msg = data.get("error", {}).get("message", "Gagal menghubungi Gemini API.")
                    st.error(f"Ralat API ({response.status_code}): {error_msg}")

            except Exception as e:
                st.error(f"Ralat Sambungan: {e}")
