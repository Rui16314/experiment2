import streamlit as st
import pandas as pd
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets Setup ---
def save_to_google_sheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("experiment2.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Experiment 2").sheet1

    if isinstance(data['race'], list):
        data['race'] = ', '.join(data['race'])

    sheet.append_row([data['name'], data['gender'], data['age'], data['race'], data['X']])

def load_data_from_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("experiment2.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Experiment 2").sheet1

    return sheet.get_all_records()

# --- Pages ---
def show_welcome():
    st.title("🎓 Welcome to Experiment 2!")

    st.write("Click below to begin.")
    if st.button("Start"):
        st.session_state.page = "form"

def show_form():
    st.title("👤 Personal Information")

    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.slider("Age", 10, 100, 20)
    race = st.multiselect("Race", ["Asian", "Black", "White", "Latino", "Indigenous", "Other"])

    if st.button("Next: Game Rules"):
        st.session_state.pdata = {
            "name": name,
            "gender": gender,
            "age": age,
            "race": race,
            "X": 0,
            "rounds": []
        }
        st.session_state.page = "rules"

def show_rules():
    st.title("📜 Game Rules")
    st.write("""
    You will play 10 rounds. In each round, click a button to receive a random payoff between 0 and 10.
    Your final score (X value) will be the **sum of all 10 rounds**.
    After each round, you'll see feedback on your current total.
    """)
    if st.button("Start Game"):
        st.session_state.round = 1
        st.session_state.total = 0
        st.session_state.page = "game"

def show_game():
    st.title(f"🎮 Round {st.session_state.round} of 10")

    if st.button("Play Round"):
        payoff = random.randint(0, 10)
        st.session_state.total += payoff
        st.session_state.pdata["rounds"].append(payoff)
        st.success(f"You earned {payoff} points this round!")
        st.info(f"Total so far: {st.session_state.total}")

        if st.session_state.round < 10:
            st.session_state.round += 1
        else:
            st.session_state.pdata["X"] = st.session_state.total
            st.session_state.page = "final"

def show_final():
    st.title("🎉 Game Complete")

    st.write(f"Your final score (X value) is: **{st.session_state.pdata['X']}**")
    save_to_google_sheet(st.session_state.pdata)
    st.success("Your data has been saved anonymously.")
    if st.button("View Class Dashboard"):
        st.session_state.page = "dashboard"

def show_dashboard():
    st.title("📊 Class Dashboard")

    data = load_data_from_google_sheet()
    if not data:
        st.info("No data available yet.")
        return

    df = pd.DataFrame(data)

    st.subheader("All Participants")
    st.dataframe(df)

    st.subheader("Average X Value")
    avg_x = df["X"].mean()
    st.metric(label="Average X", value=f"{avg_x:.2f}")

    st.subheader("Gender Distribution")
    st.bar_chart(df["gender"].value_counts())

    st.subheader("Age Distribution")
    st.bar_chart(df["age"])

    st.subheader("Race Breakdown")
    all_races = []
    for entry in df["race"]:
        if isinstance(entry, str):
            races = [r.strip() for r in entry.split(",")]
            all_races.extend(races)

    race_counts = pd.Series(all_races).value_counts()
    st.bar_chart(race_counts)

    if st.button("Play Again"):
        st.session_state.page = "welcome"

# --- Page Routing ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if st.session_state.page == "welcome":
    show_welcome()
elif st.session_state.page == "form":
    show_form()
elif st.session_state.page == "rules":
    show_rules()
elif st.session_state.page == "game":
    show_game()
elif st.session_state.page == "final":
    show_final()
elif st.session_state.page == "dashboard":
    show_dashboard()
