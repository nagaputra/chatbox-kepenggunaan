import streamlit as st
import requests
import time

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

# Paparkan mesej lama
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
            
            payload = {
                "model": "gemini-3.7-flash",
                "system_instruction": SYSTEM_INSTRUCTION.strip(),
                "input": {
                    "type": "text",
                    "text": user_input
                }
            }

            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key.strip()
            }
            url = "https://generativelanguage.googleapis.com/v1beta/interactions"

            bot_reply = ""
            error_details = ""

            # Cuba sehingga 3 kali jika berlaku trafik tinggi (500)
            for attempt in range(3):
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    data = response.json()

                    if response.status_code == 200:
                        if "outputs" in data and len(data["outputs"]) > 0:
                            for output in data["outputs"]:
                                if output.get("type") == "text" and "text" in output:
                                    bot_reply += output["text"]
                                elif "text" in output:
                                    bot_reply += output["text"]
                        elif "text" in data:
                            bot_reply = data["text"]

                        if bot_reply:
                            break
                    elif response.status_code == 500:
                        # Trafik tinggi, tunggu 2 saat dan cuba semula
                        time.sleep(2)
                        continue
                    else:
                        error_details = data.get("error", {}).get("message", f"Status {response.status_code}")
                        break
                except Exception as e:
                    error_details = str(e)
                    break

            if bot_reply:
                message_placeholder.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                st.error(f"Gagal memproses permintaan: {error_details}")
