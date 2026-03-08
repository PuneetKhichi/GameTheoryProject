import numpy as np
import matplotlib.pyplot as plt
from collections import Counter


class ElectionSimulator:
    """
    Monte Carlo simulator for the 3-party strategic voting game.
    Simulates individual voter-level decisions with stochastic elements.
    """

    def __init__(self, num_voters=1000, seed=42):
        np.random.seed(seed)
        self.num_voters = num_voters

        # Assign each voter to a bloc (proportional to bloc sizes)
        self.bloc_assignment = np.random.choice(
            ['X', 'Y', 'Z'],
            size=num_voters,
            p=[0.35, 0.25, 0.40]
        )

        # True preference ordering for each bloc
        # Index 0 = 1st choice, Index 1 = 2nd choice, Index 2 = 3rd choice
        self.preferences = {
            'X': ['BJP', 'INC', 'SP'],
            'Y': ['INC', 'SP', 'BJP'],
            'Z': ['SP', 'INC', 'BJP'],
        }

    def simulate_election(self, strategic_prob=None):
        """
        Simulate one election.

        Args:
            strategic_prob: dict {bloc: probability of voting for 2nd preference}
                           e.g., {'X': 0.0, 'Y': 0.4, 'Z': 0.1}
        Returns:
            dict with vote counts and winner
        """
        if strategic_prob is None:
            strategic_prob = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}

        votes = Counter()

        for i in range(self.num_voters):
            bloc = self.bloc_assignment[i]
            prefs = self.preferences[bloc]

            # With probability strategic_prob[bloc], vote for 2nd preference
            if np.random.random() < strategic_prob[bloc]:
                votes[prefs[1]] += 1   # Strategic: 2nd preference
            else:
                votes[prefs[0]] += 1   # Sincere: 1st preference

        winner = votes.most_common(1)[0][0]
        return {'votes': dict(votes), 'winner': winner}

    def run_monte_carlo(self, strategic_prob, n_simulations=10000):
        """
        Run many simulations and compute win probability for each party.

        Args:
            strategic_prob: dict of strategic voting probabilities per bloc
            n_simulations: number of elections to simulate

        Returns:
            dict {party: win_probability}
        """
        win_counts = Counter()

        for _ in range(n_simulations):
            result = self.simulate_election(strategic_prob)
            win_counts[result['winner']] += 1

        win_probs = {party: count / n_simulations for party, count in win_counts.items()}
        return win_probs

    def sweep_strategic_probability(self, bloc='Y', n_simulations=5000, n_points=50):
        """
        Sweep the strategic voting probability for one bloc from 0 to 1
        and track how election outcomes change.

        Args:
            bloc: which bloc to sweep ('X', 'Y', or 'Z')
            n_simulations: simulations per probability point
            n_points: number of probability points to test

        Returns:
            dict with probability values and win probabilities for each party
        """
        probs = np.linspace(0, 1, n_points)
        results = {'prob': [], 'BJP': [], 'INC': [], 'SP': []}

        print(f"Running sweep for Bloc {bloc} ({n_points} points x {n_simulations} simulations)...")

        for idx, p in enumerate(probs):
            sp = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
            sp[bloc] = p

            win_probs = self.run_monte_carlo(sp, n_simulations)

            results['prob'].append(p)
            results['BJP'].append(win_probs.get('BJP', 0))
            results['INC'].append(win_probs.get('INC', 0))
            results['SP'].append(win_probs.get('SP', 0))

            # Progress indicator every 10 points
            if (idx + 1) % 10 == 0:
                print(f"  Completed {idx + 1}/{n_points} points...")

        print("Sweep complete!")
        return results

    def plot_sweep(self, results, bloc='Y', save=True):
        """
        Plot the sweep results showing how win probabilities change
        as strategic voting increases.

        Args:
            results: dict from sweep_strategic_probability()
            bloc: which bloc was swept (for labeling)
            save: whether to save the plot to outputs/figures/
        """
        fig, ax = plt.subplots(figsize=(12, 7))

        ax.plot(results['prob'], results['BJP'], 'o-',
                color='#FF9933', label='BJP', linewidth=2, markersize=4)
        ax.plot(results['prob'], results['INC'], 's-',
                color='#00BFFF', label='INC', linewidth=2, markersize=4)
        ax.plot(results['prob'], results['SP'], '^-',
                color='#FF0000', label='SP', linewidth=2, markersize=4)

        ax.set_xlabel(f'Probability of Bloc {bloc} Voting Strategically', fontsize=13)
        ax.set_ylabel('Win Probability', fontsize=13)
        ax.set_title('Effect of Strategic Voting on Election Outcome', fontsize=15, fontweight='bold')
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(-0.05, 1.05)

        plt.tight_layout()

        if save:
            filepath = f'outputs/figures/sweep_bloc_{bloc}.png'
            plt.savefig(filepath, dpi=200)
            print(f"Plot saved to {filepath}")

        plt.show()

    def plot_double_sweep(self, save=True):
        """
        Run and plot sweeps for BOTH Bloc Y and Bloc Z side by side.
        Shows which bloc's strategic behavior has more impact.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

        # Sweep Bloc Y
        results_y = self.sweep_strategic_probability(bloc='Y', n_simulations=3000, n_points=30)

        ax1.plot(results_y['prob'], results_y['BJP'], 'o-', color='#FF9933', label='BJP', linewidth=2)
        ax1.plot(results_y['prob'], results_y['INC'], 's-', color='#00BFFF', label='INC', linewidth=2)
        ax1.plot(results_y['prob'], results_y['SP'], '^-', color='#FF0000', label='SP', linewidth=2)
        ax1.set_xlabel('P(Bloc Y Votes Strategically)', fontsize=12)
        ax1.set_ylabel('Win Probability', fontsize=12)
        ax1.set_title('Bloc Y (Swing Voters) Going Strategic', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(-0.05, 1.05)

        # Sweep Bloc Z
        results_z = self.sweep_strategic_probability(bloc='Z', n_simulations=3000, n_points=30)

        ax2.plot(results_z['prob'], results_z['BJP'], 'o-', color='#FF9933', label='BJP', linewidth=2)
        ax2.plot(results_z['prob'], results_z['INC'], 's-', color='#00BFFF', label='INC', linewidth=2)
        ax2.plot(results_z['prob'], results_z['SP'], '^-', color='#FF0000', label='SP', linewidth=2)
        ax2.set_xlabel('P(Bloc Z Votes Strategically)', fontsize=12)
        ax2.set_ylabel('Win Probability', fontsize=12)
        ax2.set_title('Bloc Z (SP Base) Going Strategic', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(-0.05, 1.05)

        plt.tight_layout()

        if save:
            filepath = 'outputs/figures/double_sweep.png'
            plt.savefig(filepath, dpi=200)
            print(f"Plot saved to {filepath}")

        plt.show()

    def print_key_scenarios(self):
        """Print results for important strategic voting scenarios."""

        print("=" * 60)
        print("  MONTE CARLO ELECTION SIMULATION")
        print("=" * 60)

        scenarios = [
            ("Everyone votes sincerely",          {'X': 0.0, 'Y': 0.0, 'Z': 0.0}),
            ("30% of Bloc Y votes strategically", {'X': 0.0, 'Y': 0.3, 'Z': 0.0}),
            ("50% of Bloc Y votes strategically", {'X': 0.0, 'Y': 0.5, 'Z': 0.0}),
            ("100% of Bloc Y votes strategically", {'X': 0.0, 'Y': 1.0, 'Z': 0.0}),
            ("Both Y and Z 50% strategic",        {'X': 0.0, 'Y': 0.5, 'Z': 0.5}),
            ("All blocs 30% strategic",            {'X': 0.3, 'Y': 0.3, 'Z': 0.3}),
        ]

        for name, sp in scenarios:
            win_probs = self.run_monte_carlo(sp, n_simulations=10000)
            winner = max(win_probs, key=win_probs.get)

            print(f"\n  Scenario: {name}")
            print(f"    Strategic Probs: X={sp['X']}, Y={sp['Y']}, Z={sp['Z']}")
            print(f"    Win Probabilities:")
            for party in ['BJP', 'INC', 'SP']:
                prob = win_probs.get(party, 0)
                bar = '#' * int(prob * 40)
                print(f"      {party}: {prob*100:5.1f}% {bar}")
            print(f"    Most Likely Winner: {winner}")

        print("\n" + "=" * 60)


# --- Run this file directly to test ---
if __name__ == "__main__":
    sim = ElectionSimulator(num_voters=100)

    # 1. Print key scenarios
    sim.print_key_scenarios()

    # 2. Generate the sweep plot for Bloc Y
    print("\n--- Generating Bloc Y Sweep Plot ---")
    results = sim.sweep_strategic_probability(bloc='Y', n_simulations=50, n_points=20)
    sim.plot_sweep(results, bloc='Y')

    # 3. Generate the double sweep (Y and Z side by side)
    print("\n--- Generating Double Sweep Plot ---")
    sim.plot_double_sweep()