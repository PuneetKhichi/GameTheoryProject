from collections import Counter


class VotingMechanism:
    """
    Implements and compares multiple voting mechanisms on the same voter profile.

    Mechanisms:
    1. FPTP  - First Past The Post (only 1st preference counts)
    2. IRV   - Instant Runoff Voting (eliminate last place, redistribute)
    3. Approval Voting (vote for top N candidates you approve of)
    4. Condorcet Winner (pairwise majority comparison - theoretical benchmark)
    """

    def __init__(self, voter_preferences: list):
        """
        Args:
            voter_preferences: List of preference orderings.
                Each element is a list like ['SP', 'INC', 'BJP']
                meaning: 1st choice = SP, 2nd = INC, 3rd = BJP
        """
        self.preferences = voter_preferences
        self.n_voters = len(voter_preferences)

    def fptp(self) -> dict:
        """
        FIRST PAST THE POST (India's current system)
        Count only 1st preferences. Whoever gets most votes wins.
        No majority needed - just plurality.
        """
        first_choices = [pref[0] for pref in self.preferences]
        counts = Counter(first_choices)
        winner = counts.most_common(1)[0][0]
        return {'method': 'FPTP', 'winner': winner, 'counts': dict(counts)}

    def irv(self) -> dict:
        """
        INSTANT RUNOFF VOTING (Ranked Choice)
        1. Count 1st preferences
        2. If someone has majority (>50%), they win
        3. Otherwise, eliminate the party with fewest votes
        4. Redistribute eliminated party's voters to their 2nd preference
        5. Repeat until someone has majority
        """
        remaining_prefs = [list(p) for p in self.preferences]
        rounds = []

        while True:
            # Count first preferences among remaining candidates
            first_choices = [p[0] for p in remaining_prefs if p]
            counts = Counter(first_choices)
            rounds.append(dict(counts))

            # Check for majority
            total = sum(counts.values())
            for party, count in counts.items():
                if count > total / 2:
                    return {
                        'method': 'IRV',
                        'winner': party,
                        'rounds': rounds,
                        'num_rounds': len(rounds)
                    }

            # No majority - eliminate party with fewest votes
            min_party = counts.most_common()[-1][0]

            # Remove eliminated party from all preference lists
            remaining_prefs = [
                [p for p in pref if p != min_party]
                for pref in remaining_prefs
            ]

    def approval(self, threshold=2) -> dict:
        """
        APPROVAL VOTING
        Each voter votes for their top `threshold` candidates.
        The candidate with the most total approvals wins.

        Args:
            threshold: how many candidates each voter approves (default: top 2)
        """
        approval_counts = Counter()
        for pref in self.preferences:
            for i in range(min(threshold, len(pref))):
                approval_counts[pref[i]] += 1

        winner = approval_counts.most_common(1)[0][0]
        return {
            'method': 'Approval Voting',
            'winner': winner,
            'counts': dict(approval_counts),
            'threshold': threshold
        }

    def condorcet_winner(self) -> str:
        """
        CONDORCET WINNER (Theoretical benchmark)
        The party that beats every other party in a head-to-head
        pairwise majority vote. May not exist in all cases.
        """
        all_parties = list(set(p for pref in self.preferences for p in pref))

        for candidate in all_parties:
            beats_all = True
            for opponent in all_parties:
                if candidate == opponent:
                    continue
                # Count voters who prefer candidate over opponent
                prefer_candidate = sum(
                    1 for pref in self.preferences
                    if pref.index(candidate) < pref.index(opponent)
                )
                if prefer_candidate <= self.n_voters / 2:
                    beats_all = False
                    break
            if beats_all:
                return candidate

        return None  # No Condorcet winner exists

    def compare_all(self) -> dict:
        """Run all mechanisms and return results."""
        results = {
            'FPTP': self.fptp(),
            'IRV': self.irv(),
            'Approval': self.approval(),
            'Condorcet': self.condorcet_winner()
        }
        return results

    def print_comparison(self):
        """Run all mechanisms and print a detailed comparison."""

        results = self.compare_all()

        print("=" * 60)
        print("  VOTING MECHANISM COMPARISON")
        print("=" * 60)

        print(f"\n  Total Voters: {self.n_voters}")

        # FPTP
        fptp = results['FPTP']
        print(f"\n  --- 1. FPTP (Current Indian System) ---")
        print(f"  Rule: Whoever gets most 1st-preference votes wins")
        print(f"  Votes: ", end="")
        for party, count in sorted(fptp['counts'].items(), key=lambda x: -x[1]):
            pct = count / self.n_voters * 100
            print(f"{party}={count} ({pct:.1f}%)  ", end="")
        print(f"\n  Winner: {fptp['winner']}")

        # IRV
        irv = results['IRV']
        print(f"\n  --- 2. Instant Runoff Voting (IRV) ---")
        print(f"  Rule: Eliminate last place, redistribute votes until majority")
        for r, counts in enumerate(irv['rounds']):
            print(f"  Round {r+1}: ", end="")
            for party, count in sorted(counts.items(), key=lambda x: -x[1]):
                print(f"{party}={count}  ", end="")
            print()
        print(f"  Winner: {irv['winner']} (after {irv['num_rounds']} round(s))")

        # Approval
        appr = results['Approval']
        print(f"\n  --- 3. Approval Voting (top {appr['threshold']} approved) ---")
        print(f"  Rule: Each voter approves top {appr['threshold']} candidates")
        print(f"  Approvals: ", end="")
        for party, count in sorted(appr['counts'].items(), key=lambda x: -x[1]):
            pct = count / self.n_voters * 100
            print(f"{party}={count} ({pct:.1f}%)  ", end="")
        print(f"\n  Winner: {appr['winner']}")

        # Condorcet
        cw = results['Condorcet']
        print(f"\n  --- 4. Condorcet Winner (Theoretical Benchmark) ---")
        print(f"  Rule: Beats every other party in pairwise head-to-head")
        if cw:
            print(f"  Winner: {cw}")
        else:
            print(f"  No Condorcet winner exists (cycle detected)")

        # Summary Table
        print(f"\n  {'='*45}")
        print(f"  SUMMARY")
        print(f"  {'='*45}")
        print(f"  {'Mechanism':<25} {'Winner':<10}")
        print(f"  {'-'*45}")
        print(f"  {'FPTP':<25} {fptp['winner']:<10}")
        print(f"  {'IRV':<25} {irv['winner']:<10}")
        print(f"  {'Approval Voting':<25} {appr['winner']:<10}")
        print(f"  {'Condorcet (benchmark)':<25} {cw or 'None':<10}")
        print(f"  {'-'*45}")

        # Check if FPTP disagrees with others
        fptp_winner = fptp['winner']
        others = [irv['winner'], appr['winner'], cw]
        if any(w != fptp_winner and w is not None for w in others):
            print(f"\n  >> WARNING: FPTP produces a DIFFERENT winner than other methods!")
            print(f"  >> This means FPTP is vulnerable to strategic voting distortion.")
        else:
            print(f"\n  >> All methods agree. FPTP works fine for this preference profile.")

        print("\n" + "=" * 60)

        return results


# --- Run this file directly to test ---
if __name__ == "__main__":

    # Build voter preferences from the 3 blocs
    # Bloc X (35%): BJP > INC > SP
    # Bloc Y (25%): INC > SP > BJP
    # Bloc Z (40%): SP > INC > BJP
    preferences = (
        [['BJP', 'INC', 'SP']] * 35 +
        [['INC', 'SP', 'BJP']] * 25 +
        [['SP', 'INC', 'BJP']] * 40
    )

    print("\n>>> SCENARIO 1: Normal 3-bloc configuration <<<\n")
    vm = VotingMechanism(preferences)
    vm.print_comparison()

    # Scenario 2: What if Bloc Y splits (some go BJP strategically)?
    # 15 of Bloc Y's 25 voters switch to BJP
    preferences_split = (
        [['BJP', 'INC', 'SP']] * 35 +
        [['INC', 'SP', 'BJP']] * 10 +   # 10 stay with INC
        [['BJP', 'INC', 'SP']] * 15 +   # 15 switch to BJP strategically
        [['SP', 'INC', 'BJP']] * 40
    )

    print("\n>>> SCENARIO 2: 15 of 25 Bloc Y voters switch to BJP <<<\n")
    vm2 = VotingMechanism(preferences_split)
    vm2.print_comparison()