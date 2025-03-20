import streamlit as st
from firebase_admin import firestore
from firebase_config import db  # not from main

def app():
    st.title("🔍 Search History")

    # 1) Optionally, get current user
    user_id = st.session_state.get("username", None)
    if not user_id:
        st.warning("Please log in to see your search history.")
        return

    # 2) Query Firestore for that user’s history
    docs = db.collection("search_history").where("user_id", "==", user_id).order_by("timestamp", direction=firestore.Query.DESCENDING).stream()

    # 3) Display results
    for doc in docs:
        data = doc.to_dict()
        st.subheader(data.get("title", "No Title"))
        st.write("URL:", data.get("url", "N/A"))
        st.write("Publication Date:", data.get("publication_date", "Unknown"))
        st.write("Event Category:", data.get("event_category", "None"))
        st.write("Annotated Text:", data.get("annotated_text", ""))
        st.write("Timestamp:", data.get("timestamp"))
        st.write("---")

