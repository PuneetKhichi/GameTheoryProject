import numpy as np
from itertools import product


class ElectoralGame:
    """
    A 3-bloc strategic voting game under FPTP (First-Past-The-Post).
    
    Players: Three voter blocs (X = BJP base, Y = Swing voters, Z = SP base)
    Strategies: Each bloc votes for one of {BJP, INC, SP}
    Payoffs: Based on which party WINS the election (plurality rule)
    """

    def __init__(self, bloc_config=None):
        self.parties = ['BJP', 'INC', 'SP']

        # Default configuration based on a typical UP constituency
        if bloc_config is None:
            self.blocs = {
                'Bloc_X': {'size': 35, 'utility': {'BJP': 10, 'INC': 5, 'SP': 1}},
                'Bloc_Y': {'size': 25, 'utility': {'BJP': 2, 'INC': 10, 'SP': 7}},
                'Bloc_Z': {'size': 40, 'utility': {'BJP': 1, 'INC': 6, 'SP': 10}},
            }
        else:
            self.blocs = bloc_config

    def compute_winner(self, strategy_profile: dict) -> str:
        """
        Given a strategy profile {bloc: party_voted_for}, determine the FPTP winner.
        The party with the most total votes wins. Ties broken alphabetically.
        """
        vote_counts = {p: 0 for p in self.parties}
        for bloc_name, party_voted in strategy_profile.items():
            vote_counts[party_voted] += self.blocs[bloc_name]['size']

        max_votes = max(vote_counts.values())
        winners = [p for p, v in vote_counts.items() if v == max_votes]
        return winners[0]

    def compute_payoff(self, strategy_profile: dict) -> dict:
        """
        Compute utility for each bloc based on who wins the election.
        """
        winner = self.compute_winner(strategy_profile)
        return {
            bloc: self.blocs[bloc]['utility'][winner]
            for bloc in self.blocs
        }

    def enumerate_all_equilibria(self) -> list:
        """
        Brute-force search over all 27 possible strategy profiles (3 blocs × 3 parties).
        A profile is a Nash Equilibrium if NO bloc can improve its payoff
        by unilaterally switching to a different party.
        """
        bloc_names = list(self.blocs.keys())
        all_profiles = list(product(self.parties, repeat=len(bloc_names)))
        equilibria = []

        for profile in all_profiles:
            strategy = dict(zip(bloc_names, profile))
            payoffs = self.compute_payoff(strategy)
            is_ne = True

            # Check each bloc: can it do better by deviating?
            for i, bloc in enumerate(bloc_names):
                current_utility = payoffs[bloc]
                for alt_party in self.parties:
                    if alt_party == strategy[bloc]:
                        continue
                    # What happens if this bloc switches?
                    deviated = strategy.copy()
                    deviated[bloc] = alt_party
                    deviated_payoff = self.compute_payoff(deviated)[bloc]

                    if deviated_payoff > current_utility:
                        is_ne = False
                        break
                if not is_ne:
                    break

            if is_ne:
                equilibria.append({
                    'profile': strategy,
                    'winner': self.compute_winner(strategy),
                    'payoffs': payoffs
                })

        return equilibria

    def social_welfare(self, winner: str) -> float:
        """
        Compute total social welfare if a given party wins.
        Welfare = sum of (bloc_size × bloc_utility) for all blocs.
        """
        return sum(
            self.blocs[bloc]['utility'][winner] * self.blocs[bloc]['size']
            for bloc in self.blocs
        )

    def condorcet_winner(self) -> str:
        """
        Find the Condorcet winner: the party that beats every other party
        in a head-to-head pairwise majority vote.
        Returns None if no Condorcet winner exists.
        """
        total_size = sum(self.blocs[b]['size'] for b in self.blocs)

        for candidate in self.parties:
            beats_all = True
            for opponent in self.parties:
                if candidate == opponent:
                    continue
                # How many voters prefer candidate over opponent?
                support = sum(
                    self.blocs[b]['size'] for b in self.blocs
                    if self.blocs[b]['utility'][candidate] > self.blocs[b]['utility'][opponent]
                )
                if support <= total_size / 2:
                    beats_all = False
                    break
            if beats_all:
                return candidate
        return None

    def print_full_analysis(self):
        """Run and print a complete analysis of the game."""

        print("=" * 60)
        print("  ELECTORAL GAME: FULL ANALYSIS")
        print("=" * 60)

        # 1. Bloc Info
        print("\n--- Voter Blocs ---")
        for name, info in self.blocs.items():
            print(f"  {name}: Size={info['size']}%, Preferences={info['utility']}")

        # 2. Sincere Voting
        print("\n--- Sincere Voting Outcome ---")
        sincere = {
            'Bloc_X': 'BJP',
            'Bloc_Y': 'INC',
            'Bloc_Z': 'SP'
        }
        winner = self.compute_winner(sincere)
        payoffs = self.compute_payoff(sincere)
        print(f"  Votes: BJP={self.blocs['Bloc_X']['size']}, "
              f"INC={self.blocs['Bloc_Y']['size']}, "
              f"SP={self.blocs['Bloc_Z']['size']}")
        print(f"  Winner: {winner}")
        print(f"  Payoffs: {payoffs}")

        # 3. Social Welfare
        print("\n--- Social Welfare Comparison ---")
        for party in self.parties:
            w = self.social_welfare(party)
            print(f"  W({party} wins) = {w}")
        best_party = max(self.parties, key=lambda p: self.social_welfare(p))
        print(f"  >> Welfare-maximizing winner: {best_party}")

        # 4. Condorcet Winner
        cw = self.condorcet_winner()
        print(f"\n--- Condorcet Winner: {cw} ---")

        # 5. Nash Equilibria
        print("\n--- Pure Strategy Nash Equilibria ---")
        equilibria = self.enumerate_all_equilibria()
        if not equilibria:
            print("  No pure strategy Nash Equilibrium found!")
        else:
            for i, eq in enumerate(equilibria):
                print(f"\n  NE #{i+1}:")
                print(f"    Strategies: {eq['profile']}")
                print(f"    Winner:     {eq['winner']}")
                print(f"    Payoffs:    {eq['payoffs']}")

        print("\n" + "=" * 60)


# --- Run this file directly to test ---
if __name__ == "__main__":
    game = ElectoralGame()
    game.print_full_analysis()