import nashpy as nash
import numpy as np


def anti_bjp_coordination_game():
    """
    Models the coordination dilemma between Bloc Y (INC supporters)
    and Bloc Z (SP supporters).

    The question: If both blocs want to defeat BJP, should they
    unite behind SP or behind INC?

    This is a STAG HUNT / Coordination Game:
    - If both pick SP  --> SP wins (good for Z, okay for Y)
    - If both pick INC --> INC wins (great for Y, okay for Z)
    - If they split    --> BJP wins (bad for both)

    Payoff matrices:
                        Bloc Z votes SP     Bloc Z votes INC
    Bloc Y votes SP  [    (7, 10)               (2, 1)      ]
    Bloc Y votes INC [    (2, 1)                (10, 6)      ]
    """

    # Bloc Y's payoffs (Row player)
    payoff_Y = np.array([
        [7, 2],     # Y votes SP:  if Z also SP -> SP wins (7), if Z goes INC -> BJP wins (2)
        [2, 10]     # Y votes INC: if Z goes SP -> BJP wins (2), if Z also INC -> INC wins (10)
    ])

    # Bloc Z's payoffs (Column player)
    payoff_Z = np.array([
        [10, 1],    # Z votes SP:  if Y also SP -> SP wins (10), if Y goes INC -> BJP wins (1)
        [1, 6]      # Z votes INC: if Y goes SP -> BJP wins (1),  if Y also INC -> INC wins (6)
    ])

    game = nash.Game(payoff_Y, payoff_Z)
    equilibria = list(game.support_enumeration())

    return game, payoff_Y, payoff_Z, equilibria


def print_equilibria_analysis():
    """Run the coordination game and print detailed results."""

    game, payoff_Y, payoff_Z, equilibria = anti_bjp_coordination_game()

    print("=" * 60)
    print("  ANTI-BJP COORDINATION GAME (Mixed Strategy Analysis)")
    print("=" * 60)

    print("\n--- Payoff Matrices ---")
    print("\nBloc Y's Payoffs:")
    print(f"                   Z votes SP    Z votes INC")
    print(f"  Y votes SP  [     {payoff_Y[0][0]}              {payoff_Y[0][1]}       ]")
    print(f"  Y votes INC [     {payoff_Y[1][0]}              {payoff_Y[1][1]}      ]")

    print(f"\nBloc Z's Payoffs:")
    print(f"                   Z votes SP    Z votes INC")
    print(f"  Y votes SP  [     {payoff_Z[0][0]}              {payoff_Z[0][1]}       ]")
    print(f"  Y votes INC [     {payoff_Z[1][0]}              {payoff_Z[1][1]}       ]")

    print(f"\n--- Nash Equilibria Found: {len(equilibria)} ---")

    for i, (sigma_Y, sigma_Z) in enumerate(equilibria):
        print(f"\n  Equilibrium #{i+1}:")
        print(f"    Bloc Y: P(vote SP) = {sigma_Y[0]:.4f}, P(vote INC) = {sigma_Y[1]:.4f}")
        print(f"    Bloc Z: P(vote SP) = {sigma_Z[0]:.4f}, P(vote INC) = {sigma_Z[1]:.4f}")

        # Classify the equilibrium
        if sigma_Y[0] == 1.0 and sigma_Z[0] == 1.0:
            print(f"    >> PURE NE: Both unite behind SP --> SP wins")
        elif sigma_Y[1] == 1.0 and sigma_Z[1] == 1.0:
            print(f"    >> PURE NE: Both unite behind INC --> INC wins")
        else:
            print(f"    >> MIXED NE: Blocs randomize --> Risk of vote split (BJP could win)")

            # Calculate expected payoffs under mixed strategy
            eu_Y = sigma_Y @ payoff_Y @ sigma_Z
            eu_Z = sigma_Y @ payoff_Z @ sigma_Z
            print(f"    >> Expected Payoff: Bloc Y = {eu_Y:.4f}, Bloc Z = {eu_Z:.4f}")

            # Calculate probability of BJP winning (when they split)
            # BJP wins when Y and Z pick different parties
            p_split = sigma_Y[0] * sigma_Z[1] + sigma_Y[1] * sigma_Z[0]
            print(f"    >> Probability of vote split (BJP wins) = {p_split:.4f}")
            print(f"    >> Probability of coordination (BJP loses) = {1 - p_split:.4f}")

    # Key Insight
    print("\n--- KEY INSIGHT ---")
    print("  This is a COORDINATION GAME (Stag Hunt), not a Prisoner's Dilemma!")
    print("  Both 'unite behind SP' and 'unite behind INC' are Nash Equilibria.")
    print("  The MIXED equilibrium shows what happens when blocs CAN'T coordinate:")
    print("  there's a significant probability of vote splitting, letting BJP win")
    print("  even though a MAJORITY of voters prefer someone else.")

    print("\n" + "=" * 60)


# --- Run this file directly to test ---
if __name__ == "__main__":
    print_equilibria_analysis()