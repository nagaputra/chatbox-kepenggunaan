import streamlit as st
from google import genai
from google.genai import types

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

        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Format perbualan
                contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

                # Cari model yang sah secara automatik dari akaun API anda
                available_models = [m.name for m in client.models.list() if "generateContent" in (m.supported_actions or [])]
                
                # Utamakan model flash jika ada
                chosen_model = next((m for m in available_models if "flash" in m.lower()), available_models[0] if available_models else None)

                if not chosen_model:
                    st.error("Tiada model penjanaan teks dijumpai untuk API Key ini.")
                else:
                    response = client.models.generate_content(
                        model=chosen_model,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.7,
                        )
                    )
                    
                    bot_reply = response.text
                    message_placeholder.markdown(bot_reply)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        except Exception as e:
            st.error(f"Ralat berlaku: {e}")
