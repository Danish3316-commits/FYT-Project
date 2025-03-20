import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

# Uncomment if you actually need to initialize the Firebase app
#cred = credentials.Certificate("newsbook-e9046-359984ad755d.json")
#firebase_admin.initialize_app(cred)

def app():
    st.title("Welcome to :violet[Newsbook]")

    # Ensure certain keys exist in st.session_state
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "useremail" not in st.session_state:
        st.session_state.useremail = ""
    if "signedout" not in st.session_state:
        st.session_state.signedout = False
    if "signout" not in st.session_state:
        st.session_state.signout = False

    # Only show Login/Signup if user is not already signed out
    if not st.session_state.signedout:
        choice = st.selectbox("Login/Signup", ["Login", "Signup"])
    else:
        choice = None

    # -- Sign-out function --
    def sign_out():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ""
        st.session_state.useremail = ""

    # If user chooses Login
    if choice == "Login":
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")

        def login():
            try:
                user = auth.get_user_by_email(email)
                # If successful:
                st.write("Login Successful")
                st.session_state.username = user.uid
                st.session_state.useremail = user.email
                st.session_state.signedout = True
                st.session_state.signout = True
            except:
                st.warning("Login Failed")

        st.button("Login", on_click=login)

    # If user chooses Signup
    elif choice == "Signup":
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        username = st.text_input("Enter your unique username")

        if st.button("Create my account"):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success("Account Created Successfully!")
            st.markdown("Please Login using your email and password")
            st.balloons()

    # If the user is signed in (signout == True), show their info + sign-out button
    if st.session_state.signout:
        st.text("Name: " + st.session_state.username)
        st.text("Email Id: " + st.session_state.useremail)
        st.button("Sign out", on_click=sign_out)
