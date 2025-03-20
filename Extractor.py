# Extractor.py
import streamlit as st
import Pipeline as pl
# Import db from firebase_config instead of main
from firebase_config import db
from firebase_admin import firestore

def app():
    st.title("Extractor")

    # 1) Ask user for a URL
    Url = st.text_input("Enter the Url", value="", max_chars=100)

   

    # 3) Extract event on button click
    if st.button("Extract Event"):
        if Url.strip():
            # Call your pipeline function
            result = pl.event_extract(Url)

            st.subheader("Extraction Results")
            st.write("**Title**:", result["title"])
            st.write("**Publication Date**:", result["publication_date"])
            st.write("**Event Category**:", result["event_category"])
            st.write("**Annotated Text**:\n", result["annotated_text"])
            st.write("**URL**:", result["url"])

            # 4) Save to Firestore
            # Optionally, store user info if you have a logged-in user:
            user_id = st.session_state.get("username", "anonymous")

            # Create a new doc in "search_history" collection
            doc_ref = db.collection("search_history").document()
            doc_ref.set({
                "user_id": user_id,
                "url": result["url"],
                "title": result["title"],
                "publication_date": result["publication_date"],
                "event_category": result["event_category"],
                "annotated_text": result["annotated_text"],
                "timestamp": firestore.SERVER_TIMESTAMP
            })

            st.success("Data saved to search history!")
        else:
            st.warning("Please enter a valid URL.")
