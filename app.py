import streamlit as st
import requests
import time

# Tetapan Halaman Web
st.set_page_config(page_title="Pembantu Kepenggunaan & Gaya Hidup AI", page_icon="🛍️")
st.title("🛍️ Pembantu Kepenggunaan & Gaya Hidup AI")
st.write("Tanyakan soalan berkaitan hak pengguna, aduan KPDN/TTPM, cadangan makanan sihat, isu kesihatan, atau penipuan (scam).")

# Dapatkan API Key daripada Secrets Streamlit
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
                "x-goog-api-key": API_KEY.strip()
            }
            url = "https://generativelanguage.googleapis.com/v1beta/interactions"

            bot_reply = ""
            last_error_message = ""

            # Cuba sehingga 3 kali jika pelayan mengalami kesesakan sementara (503 / 500)
            for attempt in range(3):
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=40)
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
                    elif response.status_code in [500, 503]:
                        time.sleep(3)
                        continue
                    else:
                        last_error_message = data.get("error", {}).get("message", f"Status {response.status_code}")
                        break
                except Exception as e:
                    last_error_message = str(e)
                    time.sleep(2)

            if bot_reply:
                message_placeholder.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                if "quota" in last_error_message.lower():
                    st.warning("⏳ Had kuota seminit penuh. Sila tunggu 1 minit dan cuba hantar soalan semula.")
                else:
                    st.error(f"Ralat sistem: {last_error_message}")
