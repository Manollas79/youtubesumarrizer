import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

# Load environment variables
load_dotenv()

# Configure the Google Gemini API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Define the summarization prompt
summary_prompt = """
You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 800 words. Please provide the summary of the text given here:
"""

# Define a new prompt for additional processing
additional_prompt = """
You are a YouTube video transcripter. You will be taking the transcript text
and analyze the entire video and provide the entire transcript in points
above 2000 words. Please provide the entire transcript of the text given here:
"""

# Function to extract transcript details from YouTube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

# Function to generate content using Google Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Function to translate text using googletrans
def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text

# Language options for translation
LANGUAGE_OPTIONS = {
    "Kannada": "kn",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta"
}

# Custom CSS for styling
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #1c1c1c;
            color: white;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .title {
            font-size: 2.5em;
            font-weight: bold;
            background: -webkit-linear-gradient(#e66465, #9198e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 20px;
            margin-bottom: 10px.
        }
        .subtitle {
            font-size: 1.2em;
            margin-bottom: 20px.
        }
        .stTextInput>div>div>input {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 25px;
            width: 600px;
            box-sizing: border-box;
            margin-bottom: 20px.
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 25px;
            padding: 15px 30px;
            cursor: pointer;
            font-size: 16px.
        }
        .stButton>button:hover {
            background-color: #45a049.
        }
        .result-section {
            margin-top: 20px.
        }
        .result-title {
            font-size: 1.5em;
            margin-bottom: 10px.
        }
        .result-content {
            padding: 20px;
            border: 2px solid #ddd;
            border-radius: 15px;
            background-color: #2c2c2c.
        }
        .stSelectbox>div>div>div>select {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 25px;
            width: 300px;
            margin-bottom: 20px;
            box-sizing: border-box.
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit app layout
st.markdown("<div class='container'><div class='title'>YouTube Transcript Summarizer</div><div class='subtitle'>Instantly, without uploading any files!</div></div>", unsafe_allow_html=True)

# Input for YouTube video link
youtube_link = st.text_input("YouTube URL", placeholder="Enter YouTube URL... https://www.youtube.com/watch?v=Mcm3CE", label_visibility='hidden')
if youtube_link:
    video_id = youtube_link.split("v=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

# Button to get summarized notes
if st.button("Get Summarized Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        summary = generate_gemini_content(transcript_text, summary_prompt)
        st.session_state['summary'] = summary
        st.session_state.pop('analysis', None)
        st.subheader("Summarized Notes:")
        st.write(summary)

# Button to get detailed notes
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        analysis = generate_gemini_content(transcript_text, additional_prompt)
        st.session_state['analysis'] = analysis
        st.session_state.pop('summary', None)
        st.subheader("Detailed Notes:")
        st.write(analysis)

# Ensure summary is available before showing translation options
if 'summary' in st.session_state:
    st.subheader("Translate Summarized Notes:")
    target_language = st.selectbox("Select target language for translation:", options=list(LANGUAGE_OPTIONS.keys()))
    
    # Button to translate summary
    if st.button("Translate Summarized Notes"):
        summary = st.session_state['summary']
        translated_summary = translate_text(summary, LANGUAGE_OPTIONS[target_language])
        st.session_state['translated_summary'] = translated_summary
        
        # Display both the summarized notes and the translated summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Summarized Notes:")
            st.write(summary)
        
        with col2:
            st.subheader("Translated Summarized Notes:")
            st.write(translated_summary)

# Ensure analysis is available before showing translation options
if 'analysis' in st.session_state:
    st.subheader("Translate Detailed Notes:")
    target_language = st.selectbox("Select target language for translation:", options=list(LANGUAGE_OPTIONS.keys()))
    
    # Button to translate analysis
    if st.button("Translate Detailed Notes"):
        analysis = st.session_state['analysis']
        translated_analysis = translate_text(analysis, LANGUAGE_OPTIONS[target_language])
        st.session_state['translated_analysis'] = translated_analysis
        
        # Display both the detailed notes and the translated analysis
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Detailed Notes:")
            st.write(analysis)
        
        with col4:
            st.subheader("Translated Detailed Notes:")
            st.write(translated_analysis)
