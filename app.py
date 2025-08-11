import streamlit as st
import random
import pandas as pd

# --- Helper Functions ---
def load_local_data():
    if "all_data" not in st.session_state:
        st.session_state.all_data = []
    return st.session_state.all_data

def save_local_data(data):
    st.session_state.all_data.append(data)

# --- Pages ---
def welcome():
    st.title("🎮 Welcome to the Bidding Game")
    st.write("Enter your details to begin:")

    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=18, max_value=100)
    race = st.selectbox("Race", ["Asian", "Black", "White", "Latino", "Other"])

    if st.button("Start Game"):
        st.session_state.pdata = {
            "name": name,
            "gender": gender,
            "age": age,
            "race": race,
            "rounds": [],
            "selected_round": None,
            "X": None
        }
        st.session_state.page = "game"

def game():
    st.title("🕹️ Bidding Game")

    round_num = len(st.session_state.pdata["rounds"]) + 1
    st.subheader(f"Round {round_num}")

    bid = st.slider("Choose your bid (0–100)", 0, 100, 50)
    if st.button("Submit Bid"):
        payoff = random.uniform(0, 1) * bid
        st.session_state.pdata["rounds"].append({
            "round": round_num,
            "bid": bid,
            "payoff": payoff
        })

        if round_num >= 10:
            st.session_state.page = "result"
        else:
            st.experimental_rerun()

def result():
    st.title("🎯 Final Result")

    pdata = st.session_state.pdata
    selected_round = random.randint(1, 10)
    pdata["selected_round"] = selected_round
    selected_bid = pdata["rounds"][selected_round - 1]["bid"]
    selected_payoff = pdata["rounds"][selected_round - 1]["payoff"]
    pdata["X"] = selected_payoff

    save_local_data({
        "name": pdata["name"],
        "gender": pdata["gender"],
        "age": pdata["age"],
        "race": pdata["race"],
        "X": selected_payoff
    })

    st.write(f"🔢 Selected Round: {selected_round}")
    st.write(f"💰 Your Bid: {selected_bid}")
    st.write(f"🏆 Final Payoff (X): {selected_payoff:.2f} points")

    # --- Risk Preference ---
    if selected_bid == 100:
        st.markdown("🧠 **Risk Preference:** Risk-neutral or risk-loving")
    else:
        st.markdown("🧠 **Risk Preference:** Risk-averse")

    if st.button("View Dashboard"):
        st.session_state.page = "dashboard"

def dashboard():
    st.title("📊 Your Dashboard")

    pdata = st.session_state.pdata
    X = pdata["X"]
    selected_index = pdata["selected_round"] - 1
    selected_bid = pdata["rounds"][selected_index]["bid"]

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

    st.subheader("🌍 Group Summary")
    all_data = load_local_data()
    if all_data:
        df = pd.DataFrame(all_data)

        st.markdown("**Distribution of Final Payoffs (X)**")
        st.bar_chart(df["X"].round().value_counts().sort_index())

        st.markdown("**Average Final Payoff by Gender**")
        st.bar_chart(df.groupby("gender")["X"].mean())

        st.markdown("**Average Final Payoff by Age**")
        st.bar_chart(df.groupby("age")["X"].mean())

        st.markdown("**Average Final Payoff by Race**")
        st.bar_chart(df.groupby("race")["X"].mean())
    else:
        st.info("No group data available yet.")

    if st.button("Play Again"):
        st.session_state.page = "welcome"

# --- Page Router ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"

pages = {
    "welcome": welcome,
    "game": game,
    "result": result,
    "dashboard": dashboard
}

pages[st.session_state.page]()



