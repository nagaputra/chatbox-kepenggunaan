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
            
            # Format input sejarah perbualan untuk Interactions API
            turns = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                turns.append({
                    "role": role,
                    "content": m["content"]
                })

            payload = {
                "model": "gemini-3-flash",
                "system_instruction": SYSTEM_INSTRUCTION,
                "input": turns
            }

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key.strip()
            }

            url = "https://generativelanguage.googleapis.com/v1beta/interactions"

            try:
                response = requests.post(url, headers=headers, json=payload)
                data = response.json()

                if response.status_code == 200:
                    # Dapatkan teks respon daripada struktur Interactions API
                    bot_reply = ""
                    if "outputs" in data and len(data["outputs"]) > 0:
                        bot_reply = data["outputs"][-1].get("text", "")
                    elif "text" in data:
                        bot_reply = data["text"]
                    elif "response" in data:
                        bot_reply = str(data["response"])

                    if bot_reply:
                        message_placeholder.markdown(bot_reply)
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    else:
                        st.write(data)
                else:
                    error_msg = data.get("error", {}).get("message", "Gagal menghubungi Gemini Interactions API.")
                    st.error(f"Ralat API ({response.status_code}): {error_msg}")

            except Exception as e:
                st.error(f"Ralat Sambungan: {e}")
