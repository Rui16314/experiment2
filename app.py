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
    round_number = st.session_state.round
    if round_number > 10:
        st.session_state.page = "game_result"
        st.rerun()
        return

    st.title(f"🎮 Round {round_number} of 10")

    if f"submitted_{round_number}" not in st.session_state:
        st.session_state[f"submitted_{round_number}"] = False

    if not st.session_state[f"submitted_{round_number}"]:
        bid = st.number_input("How much do you want to invest? (0–100)", min_value=0, max_value=100, step=1, key=f"bid_{round_number}")
        if st.button("Submit Investment"):
            st.session_state.current_bid = bid
            st.session_state[f"submitted_{round_number}"] = True
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
        selected_bid = st.session_state.pdata["rounds"][selected]["bid"]
        final_payoff = st.session_state.pdata["rounds"][selected]["payoff"]
        st.session_state.pdata["X"] = final_payoff
        st.session_state.pdata["selected_round"] = selected + 1
        st.session_state.pdata["selected_bid"] = selected_bid
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

    if st.button("View Your Dashboard"):
        st.session_state.page = "dashboard"

def show_dashboard():
    st.title("📊 Your Dashboard")

    pdata = st.session_state.pdata
    X = pdata["X"]
    selected_bid = pdata["selected_bid"]

    # --- Individual Summary ---
    st.subheader("🧍 Your Info")
    st.write(f"**Name:** {pdata['name']}")
    st.write(f"**Gender:** {pdata['gender']}")
    st.write(f"**Age:** {pdata['age']}")
    st.write(f"**Race:** {pdata['race']}")
    st.write(f"**Final Payoff (X):** {X:.2f} points")
    st.write(f"**Selected Round Bid:** {selected_bid}")

    if selected_bid == 100:
        st.markdown("🧠 **Risk Preference:** Risk-neutral or risk-loving")
    else:
        st.markdown("🧠 **Risk Preference:** Risk-averse")

    # --- Group-Level Visualizations ---
    st.subheader("🌍 Group Summary")
    all_data = load_local_data()
    if all_data:
        df = pd.DataFrame(all_data)

        # Clean and prepare data
        df["gender"] = df["gender"].fillna("Unknown")
        df["age"] = pd.to_numeric(df["age"], errors="coerce")
        df["race"] = df["race"].fillna("Unknown")
        df["X"] = pd.to_numeric(df["X"], errors="coerce")

        st.markdown("**Distribution of Final Payoffs (X)**")
        bins = pd.interval_range(start=0, end=df["X"].max() + 50, freq=25, closed="right")
        binned = pd.cut(df["X"], bins=bins, include_lowest=True)
        binned_counts = binned.value_counts().sort_index()
        binned_counts.index = binned_counts.index.astype(str)
        st.bar_chart(binned_counts)

        if len(df) >= 5:
            st.markdown("**Average Final Payoff by Gender**")
            st.bar_chart(df.groupby("gender")["X"].mean())

            st.markdown("**Average Final Payoff by Age**")
            st.bar_chart(df.groupby("age")["X"].mean())

            st.markdown("**Average Final Payoff by Race**")
            df["race"] = df["race"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])
            df_exploded = df.explode("race")
            st.bar_chart(df_exploded.groupby("race")["X"].mean())
        else:
            st.info("Not enough data to generate meaningful group charts.")
    else:
        st.info("No group data available yet.")

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



