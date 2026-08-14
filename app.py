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
            clean_key = api_key.strip()

            try:
                # 1. Dapatkan senarai model sah secara terus dari akaun API anda
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_key}"
                list_res = requests.get(list_url)
                list_data = list_res.json()

                if "models" not in list_data:
                    err_txt = list_data.get("error", {}).get("message", "API Key tidak sah atau kuota tamat.")
                    st.error(f"Ralat Pengesahan API: {err_txt}")
                else:
                    # Pilih model yang menyokong generateContent
                    supported = [m["name"] for m in list_data["models"] if "generateContent" in m.get("supportedGenerationMethods", [])]
                    
                    # Utamakan model flash
                    target_model = next((m for m in supported if "flash" in m.lower()), supported[0] if supported else None)

                    if not target_model:
                        st.error("Tiada model penjanaan yang aktif pada API Key ini.")
                    else:
                        # 2. Hantar permintaan perbualan kepada model yang dipilih
                        # Format contents
                        contents = []
                        for m in st.session_state.messages:
                            role = "user" if m["role"] == "user" else "model"
                            contents.append({
                                "role": role,
                                "parts": [{"text": m["content"]}]
                            })

                        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={clean_key}"
                        payload = {
                            "system_instruction": {
                                "parts": [{"text": SYSTEM_INSTRUCTION.strip()}]
                            },
                            "contents": contents,
                            "generationConfig": {
                                "temperature": 0.7
                            }
                        }

                        gen_res = requests.post(gen_url, json=payload)
                        gen_data = gen_res.json()

                        if gen_res.status_code == 200 and "candidates" in gen_data:
                            bot_reply = gen_data["candidates"][0]["content"]["parts"][0]["text"]
                            message_placeholder.markdown(bot_reply)
                            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                        else:
                            err_txt = gen_data.get("error", {}).get("message", str(gen_data))
                            st.error(f"Ralat Menjana Jawapan ({gen_res.status_code}): {err_txt}")

            except Exception as e:
                st.error(f"Ralat Sambungan: {e}")
