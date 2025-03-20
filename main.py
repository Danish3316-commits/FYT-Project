import streamlit as st

st.set_page_config(page_title="NewsBook")

# Import the Firestore client from your new config
from firebase_config import db

from streamlit_option_menu import option_menu
import about
import account
import home
import Extractor
import Search

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        with st.sidebar:
            selected = option_menu(
                menu_title="Newsbook",
                options=["Home", "Account", "Extractor", "Search History", "About"],
                icons=["house-fill", "person-circle", "", "", "info-circle-fill"],
                menu_icon="chat-text-fill",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "black"},
                    "icons": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                },
            )

        if selected == "Home":
            home.app()
        elif selected == "Account":
            account.app()
        elif selected == "Extractor":
            Extractor.app()
        elif selected == "Search History":
            Search.app()
        elif selected == "About":
            about.app()

if __name__ == "__main__":
    app = MultiApp()
    app.run()
