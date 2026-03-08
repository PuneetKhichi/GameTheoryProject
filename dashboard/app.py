import streamlit as st
import numpy as np
import sys
import os

# Add project root to path so we can import from src/
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.game_definition import ElectoralGame
from src.simulation import ElectionSimulator
from src.mechanism_design import VotingMechanism

# --- Page Config ---
st.set_page_config(
    page_title="Strategic Voting in India",
    page_icon="🗳️",
    layout="wide"
)

st.title("Strategic Voting in Indian Elections")
st.markdown("**A Game-Theoretic Analysis under FPTP**")
st.markdown("---")

# ============================================================
# SIDEBAR: ALL CONTROLS
# ============================================================
st.sidebar.header("Game Parameters")

st.sidebar.subheader("Bloc Sizes (%)")
bloc_x = st.sidebar.slider("Bloc X (BJP base)", 10, 60, 35)
bloc_y = st.sidebar.slider("Bloc Y (Swing voters)", 10, 60, 25)
bloc_z = 100 - bloc_x - bloc_y

if bloc_z < 5:
    st.sidebar.error("Bloc Z too small! Adjust the sliders.")
    st.stop()

st.sidebar.write(f"Bloc Z (SP base): **{bloc_z}%**")

st.sidebar.markdown("---")
st.sidebar.subheader("Strategic Voting")
p_y = st.sidebar.slider("P(Bloc Y votes strategically)", 0.0, 1.0, 0.0, 0.05)
p_z = st.sidebar.slider("P(Bloc Z votes strategically)", 0.0, 1.0, 0.0, 0.05)

st.sidebar.markdown("---")
st.sidebar.subheader("Simulation Settings")
n_voters = st.sidebar.selectbox("Number of voters", [1000, 5000, 10000], index=0)
n_sims = st.sidebar.selectbox("Simulations per scenario", [500, 1000, 3000], index=0)

# ============================================================
# SECTION 1: THE GAME
# ============================================================
st.header("1. The Electoral Game")

# Build custom game config from sidebar
config = {
    'Bloc_X': {'size': bloc_x, 'utility': {'BJP': 10, 'INC': 5, 'SP': 1}},
    'Bloc_Y': {'size': bloc_y, 'utility': {'BJP': 2, 'INC': 10, 'SP': 7}},
    'Bloc_Z': {'size': bloc_z, 'utility': {'BJP': 1, 'INC': 6, 'SP': 10}},
}
game = ElectoralGame(bloc_config=config)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Bloc X (BJP Base)")
    st.write(f"Size: **{bloc_x}%**")
    st.write("Preferences: BJP > INC > SP")

with col2:
    st.subheader("Bloc Y (Swing)")
    st.write(f"Size: **{bloc_y}%**")
    st.write("Preferences: INC > SP > BJP")

with col3:
    st.subheader("Bloc Z (SP Base)")
    st.write(f"Size: **{bloc_z}%**")
    st.write("Preferences: SP > INC > BJP")

# Sincere outcome
sincere = {'Bloc_X': 'BJP', 'Bloc_Y': 'INC', 'Bloc_Z': 'SP'}
sincere_winner = game.compute_winner(sincere)
condorcet = game.condorcet_winner()

st.markdown("---")

m1, m2, m3 = st.columns(3)
m1.metric("Sincere Voting Winner", sincere_winner)
m2.metric("Condorcet Winner", condorcet or "None")

# Social welfare
welfare = {p: game.social_welfare(p) for p in game.parties}
best_welfare = max(welfare, key=welfare.get)
m3.metric("Welfare-Maximizing Winner", best_welfare)

# Show welfare bar chart
st.subheader("Social Welfare by Party")
st.bar_chart(welfare)

# ============================================================
# SECTION 2: NASH EQUILIBRIA
# ============================================================
st.markdown("---")
st.header("2. Nash Equilibria")

equilibria = game.enumerate_all_equilibria()
st.write(f"Found **{len(equilibria)}** Pure Strategy Nash Equilibria:")

for i, eq in enumerate(equilibria):
    with st.expander(f"NE #{i+1}: {eq['profile']} --> {eq['winner']} wins"):
        st.write(f"**Strategies:** {eq['profile']}")
        st.write(f"**Winner:** {eq['winner']}")
        st.write(f"**Payoffs:** {eq['payoffs']}")

        # Flag "bad" equilibria
        if eq['winner'] != condorcet and condorcet is not None:
            st.error(
                f"BAD EQUILIBRIUM: {eq['winner']} wins even though "
                f"{condorcet} is the Condorcet winner!"
            )
        else:
            st.success("This equilibrium elects the Condorcet winner.")

# ============================================================
# SECTION 3: SIMULATION
# ============================================================
st.markdown("---")
st.header("3. Monte Carlo Simulation")

col_sin, col_str = st.columns(2)

with col_sin:
    st.subheader("Sincere Voting")
    sincere_votes = {'BJP': bloc_x, 'INC': bloc_y, 'SP': bloc_z}
    st.bar_chart(sincere_votes)
    st.success(f"Winner: **{max(sincere_votes, key=sincere_votes.get)}**")

with col_str:
    st.subheader("With Strategic Voting")
    sim = ElectionSimulator(num_voters=n_voters)
    win_probs = sim.run_monte_carlo(
        {'X': 0.0, 'Y': p_y, 'Z': p_z},
        n_simulations=n_sims
    )

    # Make sure all parties appear
    for p in ['BJP', 'INC', 'SP']:
        if p not in win_probs:
            win_probs[p] = 0.0

    st.bar_chart(win_probs)
    winner = max(win_probs, key=win_probs.get)
    prob = win_probs[winner] * 100
    st.warning(f"Most likely winner: **{winner}** ({prob:.1f}%)")

# Show what changed
if max(sincere_votes, key=sincere_votes.get) != winner:
    st.error(
        f"Strategic voting CHANGED the outcome! "
        f"{max(sincere_votes, key=sincere_votes.get)} --> {winner}"
    )

# ============================================================
# SECTION 4: MECHANISM COMPARISON
# ============================================================
st.markdown("---")
st.header("4. Voting Mechanism Comparison")

st.write("Same voter preferences, different voting rules:")

prefs = (
    [['BJP', 'INC', 'SP']] * bloc_x +
    [['INC', 'SP', 'BJP']] * bloc_y +
    [['SP', 'INC', 'BJP']] * bloc_z
)
vm = VotingMechanism(prefs)
results = vm.compare_all()

c1, c2, c3, c4 = st.columns(4)
c1.metric("FPTP", results['FPTP']['winner'])
c2.metric("IRV", results['IRV']['winner'])
c3.metric("Approval", results['Approval']['winner'])
c4.metric("Condorcet", results['Condorcet'] or "None")

# Explain the difference
fptp_w = results['FPTP']['winner']
irv_w = results['IRV']['winner']
approval_w = results['Approval']['winner']

if fptp_w != irv_w or fptp_w != approval_w:
    st.error(
        "FPTP produces a DIFFERENT winner than other methods! "
        "This proves FPTP is vulnerable to vote splitting."
    )
    st.info(
        "Under IRV or Approval Voting, voters don't need to vote strategically. "
        "The mechanism itself handles the coordination problem."
    )
else:
    st.success("All mechanisms agree for this configuration.")

# ============================================================
# SECTION 5: KEY INSIGHT
# ============================================================
st.markdown("---")
st.header("5. Key Takeaway")

st.markdown("""
> **Under India's FPTP system, rational voters trying to avoid wasting their vote 
> can accidentally cause the least-preferred candidate to win.** 
> 
> This is not a bug in voter behavior -- it is a bug in the mechanism.
> Switching to IRV or Approval Voting would fix this without requiring 
> any voter coordination.

*Adjust the sliders in the sidebar to explore different scenarios!*
""")

# Footer
st.markdown("---")
st.caption("Game Theory Project | Strategic Voting Analysis")