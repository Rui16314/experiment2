import streamlit as st
import pandas as pd
import random
import os
import json
from datetime import datetime

DATA_FILE = "game_data.json"

# --- Local Data Storage ---
def save_to_local(data):
    data["timestamp"] = datetime.utcnow().isoformat()  # Optional: for deduplication
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            all_data = json.load(f)
    else:
        all_data = []

    if isinstance(data['race'], list):
        data['race'] = ', '.join(data['race'])

    all_data.append(data)

    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f)

def load_local_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# --- Pages ---
def show_welcome():
    st.title("🎓 Welcome to experiment 2!")
    st.write("You will play a fun game similar to real-life investment in the stock market! Be careful with every investment!")
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
        st.session_state.page = "game_input"

def show_game_input():
    st.title(f"🎮 Round {st.session_state.round} of 10")

    if f"submitted_{st.session_state.round}" not in st.session_state:
        st.session_state[f"submitted_{st.session_state.round}"] = False

    if not st.session_state[f"submitted_{st.session_state.round}"]:
        bid = st.number_input("How much do you want to invest? (0–100)", min_value=0, max_value=100, step=1, key=f"bid_{st.session_state.round}")
        if st.button("Submit Investment"):
            st.session_state.current_bid = bid
            st.session_state[f"submitted_{st.session_state.round}"] = True
            st.session_state.page = "game_result"
            st.rerun()
    else:
        st.info("Investment submitted. Click below to view result.")
        if st.button("View Result"):
            st.session_state.page = "game_result"
            st.rerun()

def show_game_result():
    round_num = st.session_state.round
    bid = st.session_state.current_bid
    outcome = random.choice(["Success", "Failure"])
    payoff = 100 + 1.5 * bid if outcome == "Success" else 100 - bid

    st.session_state.pdata["rounds"].append({
        "round": round_num,
        "bid": bid,
        "outcome": outcome,
        "payoff": payoff
    })

    st.title(f"📄 Round {round_num} Result")
    st.write(f"Outcome: **{outcome}**")
    st.write(f"Payoff this round: **{payoff:.2f} points**")

    if round_num < 10:
        if st.button("Next Round"):
            st.session_state.round += 1
            st.session_state.page = "game_input"
            st.rerun()
    else:
        selected = random.randint(0, 9)
        final_payoff = st.session_state.pdata["rounds"][selected]["payoff"]
        st.session_state.pdata["X"] = final_payoff
        st.session_state.pdata["selected_round"] = selected + 1
        st.session_state.page = "final"
        st.rerun()

def show_final():
    st.title("🎉 Game Complete")
    selected = st.session_state.pdata["selected_round"]
    final_score = st.session_state.pdata["X"]

    st.write(f"🎲 Randomly selected round: **Round {selected}**")
    st.write(f"💰 Your final payoff (X value): **{final_score:.2f} points**")

    save_to_local(st.session_state.pdata)
    st.success("Your data has been saved anonymously.")

    if st.button("View Class Dashboard"):
        st.session_state.page = "dashboard"

def show_dashboard():
    st.title("📊 Class Dashboard")
    data = load_local_data()
    if not data:
        st.info("No data available yet.")
        return

    df = pd.DataFrame(data)

    # Deduplicate by name, keeping the latest entry
    if "timestamp" in df.columns:
        df = df.sort_values(by="timestamp").drop_duplicates(subset="name", keep="last")
    else:
        df = df.drop_duplicates(subset="name", keep="last")

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

    st.subheader("Final Payoff Distribution")
    st.bar_chart(df["X"])

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
elif st.session_state.page == "game_input":
    show_game_input()
elif st.session_state.page == "game_result":
    show_game_result()
elif st.session_state.page == "final":
    show_final()
elif st.session_state.page == "dashboard":
    show_dashboard()


