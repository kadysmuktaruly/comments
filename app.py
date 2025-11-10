import streamlit as st
from transformers import pipeline
from googleapiclient.discovery import build
import warnings
import logging

warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)

# --- YouTube API setup ---
API_KEY = "YOUR_YOUTUBE_API_KEY"

def get_comments(video_url):
    video_id = video_url.split("v=")[-1].split("&")[0]
    youtube = build("youtube", "v3", developerKey=API_KEY)
    comments = []
    
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=50,
        textFormat="plainText"
    )
    response = request.execute()

    for item in response["items"]:
        comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(comment)
    return comments


# --- Summarizer setup ---
summarizer = pipeline("text2text-generation", model="google/flan-t5-large")

def summarize_comments(comments):
    input_text = (
        "Please summarize the main themes and sentiments expressed in the following list of comments: "
        + " ".join(comments)
    )
    summary = summarizer(
        input_text,
        max_length=150,
        do_sample=True,
        temperature=0.7
    )
    return summary[0]['generated_text']


# --- Streamlit UI ---
st.title("🎬 YouTube Comment Analyzer")
st.write("Paste a YouTube video link below to analyze viewer sentiment and main themes.")

video_url = st.text_input("🔗 YouTube Video URL:")

if st.button("Analyze"):
    if video_url:
        with st.spinner("Fetching and analyzing comments..."):
            try:
                comments = get_comments(video_url)
                if comments:
                    summary = summarize_comments(comments)
                    st.success("✅ Analysis Complete!")
                    st.subheader("🧠 Summary of Comments:")
                    st.write(summary)
                else:
                    st.warning("No comments found for this video.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please paste a valid YouTube video link.")
