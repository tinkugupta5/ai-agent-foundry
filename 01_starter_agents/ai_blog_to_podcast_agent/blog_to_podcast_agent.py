import requests
from bs4 import BeautifulSoup
import streamlit as st
from groq import Groq
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

st.set_page_config(page_title="Blog to Podcast", page_icon="🎙️")
st.title("📰 ➡️ 🎙️ Blog to Podcast Generator")

st.sidebar.header("🔑 API Keys")
groq_key = st.sidebar.text_input("GROQ_API_KEY", type="password")
elevenlabs_key = st.sidebar.text_input("ELEVENLABS_API_KEY", type="password")
load_dotenv()

url = st.text_input("Enter Blog URL")

def scrape_blog(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = [p.get_text() for p in soup.find_all("p")]
    return " ".join(paragraphs)

# ---------------- Main Button ----------------
if st.button("🎙️ Generate Podcast"):
    if not groq_key or not elevenlabs_key:
        st.warning("Please enter both API keys")
    elif not url:
        st.warning("Please enter a blog URL")
    else:
        with st.spinner("Processing blog..."):
            try:
                # Step 1: Scrape Blog
                blog_text = scrape_blog(url)

                if len(blog_text) < 200:
                    st.error("Could not extract enough content from the blog.")
                    st.stop()

                # Step 2: Summarize using Groq
                client = Groq(api_key=groq_key)

                response = client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Turn the blog into an engaging podcast script. "
                                "Make it conversational, add an intro hook, smooth transitions, "
                                "and a closing summary."
                            ),
                        },
                        {
                            "role": "user",
                            "content": blog_text[:12000],
                        },
                    ],
                )

                summary = response.choices[0].message.content

                # Step 3: Convert to Audio (ElevenLabs)
                tts = ElevenLabs(api_key=elevenlabs_key)

                audio_generator = tts.text_to_speech.convert(
                    text=summary,
                    voice_id="JBFqnCBsd6RMkjVDRZzb",  # default voice
                    model_id="eleven_multilingual_v2"
                )

                audio_chunks = []
                for chunk in audio_generator:
                    if chunk:
                        audio_chunks.append(chunk)

                audio_bytes = b"".join(audio_chunks)

                # Step 4: Output
                st.success("Podcast generated! 🎧")

                st.audio(audio_bytes, format="audio/mp3")

                st.download_button(
                    "⬇️ Download Podcast",
                    audio_bytes,
                    "podcast.mp3",
                    "audio/mp3"
                )

                with st.expander("📄 Podcast Script"):
                    st.write(summary)

            except Exception as e:
                st.error(f"Error: {e}")