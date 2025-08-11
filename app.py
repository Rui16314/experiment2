import streamlit as st
import pandas as pd
import random
import os
import json
from datetime import datetime

DATA_FILE = "game_data.json"

# --- Local Data Storage ---
def save_to_local(data):
    data["timestamp"] = datetime.utcnow().isoformat()
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
    df = df.sort_values(by="timestamp").drop_duplicates(subset="name", keep="last")

    st.subheader("All Participants")
    st.dataframe(df)

    st.subheader("1️⃣ Histogram of X values")
    bins = pd.cut(df["X"], bins=range(0, 201, 10))
    bin_counts = bins.value_counts().sort_index()
    bin_counts.index = bin_counts.index.astype(str)
    st.bar_chart(bin_counts)

    st.subheader("2️⃣ Names in each X bin")
    name_bins = df.groupby(pd.cut(df["X"], bins=range(0, 201, 10)))["name"].apply(list)
    for interval, names in name_bins.items():
        st.write(f"**{interval}**: {', '.join(names)}")

    st.subheader("3️⃣ Histogram of X by Gender")
    for gender in df["gender"].unique():
        st.write(f"**{gender}**")
        gender_df = df[df["gender"] == gender]
        gender_bins = pd.cut(gender_df["X"], bins=range(0, 201, 10))
        gender_counts = gender_bins.value_counts().sort_index()
        gender_counts.index = gender_counts.index.astype(str)
        st.bar_chart(gender_counts)

    st.subheader("4️⃣ Histogram of X for Male Participants")
    male_df = df[df["gender"] == "Male"]
    male_bins = pd.cut(male_df["X"], bins=range(0, 201, 10))
    male_counts = male_bins.value_counts().sort_index()
    male_counts.index = male_counts.index.astype(str)
    st.bar_chart(male_counts)

    st.subheader("5️⃣ Average X by Gender")
    gender_avg = df.groupby("gender")["X"].mean()
    st.bar_chart(gender_avg)

    st.subheader("6️⃣ Average X by Age Group and Race")
    df["age_group"] = pd.cut(df["age"], bins=[10, 20, 30, 40, 50, 60, 100])
    race_avg = df.groupby(["age_group", "race"])["X"].mean().unstack().fillna(0)
    st.bar_chart(race_avg)

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


