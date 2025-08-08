import streamlit as st
import pandas as pd
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets Setup ---
def save_to_google_sheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Experiment 1").sheet1

    if isinstance(data['race'], list):
        data['race'] = ', '.join(data['race'])

    # Flatten round data
    round_data = []
    for r in data["rounds"]:
        round_data.extend([r["bid"], r["outcome"], r["payoff"]])

    row = [data['name'], data['gender'], data['age'], data['race'], data['X'], data.get("selected_round", "")] + round_data
    sheet.append_row(row)

def load_data_from_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Your Spreadsheet Name").sheet1

    return sheet.get_all_records()

# --- Pages ---
def show_welcome():
    st.title("🎓 Welcome to the Student Investment Game")
    st.write("This is a fun and interactive game designed to collect anonymous data for classroom analysis.")
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
    You will play 10 rounds. In each round, you receive 100 points and choose how much to invest in a risky asset.
    - If the asset succeeds (50% chance): payoff = 100 + 1.5 × investment
    - If it fails: payoff = 100 − investment
    At the end, one round is randomly selected and its payoff becomes your final score (X value).
    """)
    if st.button("Start Game"):
        st.session_state.round = 1
        st.session_state.page = "game"

def show_game():
    st.title(f"🎮 Round {st.session_state.round} of 10")

    bid = st.number_input("How much do you want to invest? (0–100)", min_value=0, max_value=100, key=f"bid_{st.session_state.round}")

    if st.button("Submit Investment"):
        outcome = random.choice(["Success", "Failure"])
        payoff = 100 + 1.5 * bid if outcome == "Success" else 100 - bid

        st.session_state.pdata["rounds"].append({
            "round": st.session_state.round,
            "bid": bid,
            "outcome": outcome,
            "payoff": payoff
        })

        st.success(f"Outcome: {outcome}")
        st.info(f"Payoff this round: {payoff:.2f}")

        if st.session_state.round < 10:
            st.session_state.round += 1
        else:
            selected = random.randint(0, 9)
            final_payoff = st.session_state.pdata["rounds"][selected]["payoff"]
            st.session_state.pdata["X"] = final_payoff
            st.session_state.pdata["selected_round"] = selected + 1
            st.session_state.page = "final"

def show_final():
    st.title("🎉 Game Complete")

    selected = st.session_state.pdata["selected_round"]
    final_score = st.session_state.pdata["X"]

    st.write(f"🎲 Randomly selected round: **Round {selected}**")
    st.write(f"💰 Your final payoff (X value): **{final_score:.2f} points**")

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

    st.subheader("Average Final Payoff (X)")
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

