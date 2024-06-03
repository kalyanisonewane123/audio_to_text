import streamlit as st
from moviepy.editor import VideoFileClip
import requests
import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Set AssemblyAI API key


api_key=os.getenv(st.secrets["API_KEY"])

# Streamlit app
st.title("Audio and Video Transcription System")

# File uploader
uploaded_file = st.file_uploader("Choose an audio or video file", type=["mp3", "mp4", "wav", "m4a"])

if uploaded_file is not None:
    # Display file details
    st.write("Filename:", uploaded_file.name)
    # st.write("File type:", uploaded_file.type)
    # st.write("File size:", uploaded_file.size, "bytes")

    # Save the uploaded file to a temporary location
    temp_file_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract audio if the uploaded file is a video
    if uploaded_file.type == "video/mp4":
        video_clip = VideoFileClip(temp_file_path)
        audio_clip = video_clip.audio
        audio_path = os.path.join("temp", "extracted_audio.mp3")
        audio_clip.write_audiofile(audio_path)
        temp_file_path = audio_path
        audio_clip.close()
        video_clip.close()

    # Display an audio player for the uploaded file or extracted audio
    st.audio(temp_file_path)

    # Confirmation button
    if st.button("Confirm and Transcribe"):
        with st.spinner('Transcribing...'):
            headers = {
                "authorization": API_KEY,
                "content-type": "application/json"
            }

            # Upload the file to AssemblyAI
            # st.write("Uploading file to AssemblyAI...")
            upload_url = "https://api.assemblyai.com/v2/upload"
            with open(temp_file_path, "rb") as f:
                response = requests.post(upload_url, headers=headers, files={"file": f})

            audio_url = response.json()['upload_url']
            # st.write(f"File uploaded to AssemblyAI at URL: {audio_url}")

            # Request transcription
            st.write("Starting transcription...")
            transcription_url = "https://api.assemblyai.com/v2/transcript"
            data = {
                "audio_url": audio_url
            }
            response = requests.post(transcription_url, headers=headers, json=data)
            transcript_id = response.json()['id']
            # st.write(f"Transcription ID: {transcript_id}")

            # Poll for transcription result
            # st.write("Waiting for transcription to complete...")
            while True:
                transcript_result_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
                response = requests.get(transcript_result_url, headers=headers)
                status = response.json()['status']

                if status == 'completed':
                    transcript = response.json()
                    break
                elif status == 'failed':
                    st.error("Transcription failed.")
                    break
                else:
                    # st.write("Transcription in progress...")
                    time.sleep(5)

            if status == 'completed':
                # st.write("Transcription completed successfully!")
                # st.write("Transcription:")
                st.write(transcript['text'])

                text_file_path = os.path.join("temp", "transcript.txt")
                with open(text_file_path, "w") as text_file:
                    text_file.write(transcript['text'])

                with open(text_file_path, "rb") as text_file:
                    st.download_button(
                        label="Download Transcript as Text",
                        data=text_file,
                        file_name="transcript.txt",
                        mime="text/plain"
                    )

             






