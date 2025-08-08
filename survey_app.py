import streamlit as st
import pandas as pd
import plotly.express as px
import random

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}
if 'investments' not in st.session_state:
    st.session_state.investments = []
if 'results' not in st.session_state:
    st.session_state.results = []
if 'participant_data' not in st.session_state:
    st.session_state.participant_data = []

# Navigation helper
def next_page(page_name):
    st.session_state.page = page_name

# Welcome Page
def show_welcome():
    st.title("🎉 Welcome to the Risk Preference Survey")
    st.write("This experiment will help us understand your decision-making under risk.")
    if st.button("Start"):
        next_page('personal_info')

# Personal Info Page
def show_personal_info():
    st.title("👤 Personal Information")
    name = st.text_input("Name")
    gender = st.radio("Gender", ["Man", "Woman", "Other"])
    age = st.number_input("Age", min_value=18, max_value=100)
    race = st.text_input("Race")
    if st.button("Continue"):
        st.session_state.personal_info = {
            'name': name,
            'gender': gender,
            'age': age,
            'race': race
        }
        next_page('rules')

# Game Rules Page
def show_rules():
    st.title("📜 Game Rules")
    st.markdown("""
    - You will play 10 rounds.
    - Each round, you receive 100 points.
    - Choose how much to invest in a risky asset.
    - The asset returns 2.5x with 50% chance, or 0 with 50% chance.
    - Your payoff:  
      - With success: `100 - x + 2.5x`  
      - With failure: `100 - x`
    - One round will be randomly selected for your final payoff.
    """)
    if st.button("Start Game"):
        next_page('round_0')

# Game Rounds
def show_round(round_num):
    st.title(f"🎲 Round {round_num + 1}")
    x = st.slider("How much to invest?", 0, 100, 50)
    if st.button("Submit"):
        success = random.choice([True, False])
        payoff = 100 - x + 2.5 * x if success else 100 - x
        st.session_state.investments.append(x)
        st.session_state.results.append(payoff)
        if round_num < 9:
            next_page(f'round_{round_num + 1}')
        else:
            next_page('final')

# Final Payoff Page
def show_final():
    st.title("🏁 Final Results")
    selected_round = random.randint(0, 9)
    final_payoff = st.session_state.results[selected_round]
    avg_x = sum(st.session_state.investments) / 10
    risk_pref = "Risk-neutral or loving" if avg_x == 100 else "Risk-averse"

    st.write(f"🎯 Selected Round: {selected_round + 1}")
    st.write(f"💰 Final Payoff: {final_payoff:.2f} points")
    st.write(f"📊 Average Investment (X): {avg_x:.2f}")
    st.write(f"🧠 Risk Preference: {risk_pref}")

    # Save participant data
    pdata = st.session_state.personal_info.copy()
    pdata['X'] = avg_x
    st.session_state.participant_data.append(pdata)

    if st.button("View Class Results"):
        next_page('dashboard')

# Visualization Dashboard
def show_dashboard():
    st.title("📊 Class Risk Preference Overview")
    data = pd.DataFrame(st.session_state.participant_data)

    if data.empty:
        st.warning("No data available yet.")
        return

    # 1. Histogram of X values
    st.subheader("Distribution of Risk Preferences ")
    fig1 = px.histogram(data, x="X", nbins=20, title="X Distribution")
    st.plotly_chart(fig1)

    # 2. Histogram with names
    st.subheader("X Distribution with Names")
    data['X_bin'] = pd.cut(data['X'], bins=range(0, 105, 5))
    names_by_bin = data.groupby('X_bin')['name'].apply(list).reset_index()
    st.write(names_by_bin)

    # 3. Gender-specific histograms
    for gender in ['Woman', 'Man', 'Other']:
        st.subheader(f"X Distribution for {gender}s")
        gender_data = data[data['gender'] == gender]
        if not gender_data.empty:
            fig = px.histogram(gender_data, x="X", nbins=20)
            st.plotly_chart(fig)

    # 5. Gender comparison
    st.subheader("Average X by Gender")
    gender_avg = data.groupby('gender')['X'].mean().reset_index()
    fig5 = px.bar(gender_avg, x='gender', y='X', title="Average X by Gender")
    st.plotly_chart(fig5)

    # 6. Age and Race comparison
    st.subheader("Average X by Age")
    age_avg = data.groupby('age')['X'].mean().reset_index()
    fig6 = px.bar(age_avg, x='age', y='X')
    st.plotly_chart(fig6)

    st.subheader("Average X by Race")
    race_avg = data.groupby('race')['X'].mean().reset_index()
    fig7 = px.bar(race_avg, x='race', y='X')
    st.plotly_chart(fig7)

# Page Routing
page = st.session_state.page
if page == 'welcome':
    show_welcome()
elif page == 'personal_info':
    show_personal_info()
elif page == 'rules':
    show_rules()
elif page.startswith('round_'):
    round_num = int(page.split('_')[1])
    show_round(round_num)
elif page == 'final':
    show_final()
elif page == 'dashboard':
    show_dashboard()
