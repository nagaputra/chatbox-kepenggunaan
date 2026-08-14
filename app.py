python -c "
import os

# Cipta folder projek
os.makedirs('ai_chatbox_kepenggunaan', exist_ok=True)

# 1. Fail app.py
app_code = '''import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title=\"Pembantu Kepenggunaan & Gaya Hidup AI\", page_icon=\"🛍️\")
st.title(\"🛍️ Pembantu Kepenggunaan & Gaya Hidup AI\")
st.write(\"Tanyakan soalan berkaitan hak pengguna, aduan KPDN/TTPM, cadangan makanan sihat, isu kesihatan, atau penipuan (scam).\")

api_key = st.sidebar.text_input(\"Masukkan Gemini API Key:\", type=\"password\")

SYSTEM_INSTRUCTION = \"\"\"
Anda ialah Pembantu AI Kepenggunaan dan Gaya Hidup Pintar di Malaysia.
Tugas utama anda adalah membantu pengguna dalam pelbagai topik kepenggunaan yang luas, merangkumi:

1. HAK PENGGUNA & ADUAN: Panduan Akta Perlindungan Pengguna, aduan KPDN, Tribunal Tuntutan Pengguna (TTPM), dan kes scam/NSRC 997.
2. MAKANAN & KESIHATAN: Cadangan pilihan makanan sihat, semakan isu keselamatan makanan, kesedaran status halal, dan panduan membeli barangan dapur berasaskan kesihatan.
3. ISU PENGGUNA AM: Hak pembeli barangan rosak, isu harga barangan, dan nasihat perbelanjaan berhemat.

Gaya jawapan:
- Mesra, profesional, bertatasusila, dan mudah difahami.
- Memberikan cadangan yang praktikal dan berfakta.
- Masukkan penafian mesra bahawa nasihat kesihatan atau perundangan adalah untuk rujukan umum sahaja.
\"\"\"

if \"messages\" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg[\"role\"]):
        st.markdown(msg[\"content\"])

if user_input := st.chat_input(\"Tanya soalan anda di sini...\"):
    if not api_key:
        st.error(\"Sila masukkan Gemini API Key di bahagian menu sisi (sidebar) dahulu!\")
    else:
        st.session_state.messages.append({\"role\": \"user\", \"content\": user_input})
        with st.chat_message(\"user\"):
            st.markdown(user_input)

        try:
            client = genai.Client(api_key=api_key)
            
            with st.chat_message(\"assistant\"):
                message_placeholder = st.empty()
                
                contents = []
                for m in st.session_state.messages:
                    role = \"user\" if m[\"role\"] == \"user\" else \"model\"
                    contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m[\"content\"])]))

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                
                bot_reply = response.text
                message_placeholder.markdown(bot_reply)
                st.session_state.messages.append({\"role\": \"assistant\", \"content\": bot_reply})

        except Exception as e:
            st.error(f\"Ralat berlaku: {e}\")
'''

# 2. Fail requirements.txt
requirements_code = '''streamlit
google-genai
'''

# Write files
with open('ai_chatbox_kepenggunaan/app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

with open('ai_chatbox_kepenggunaan/requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_code)

print('✅ Folder dan fail projek berjaya dicipta dalam folder: ai_chatbox_kepenggunaan')
"
