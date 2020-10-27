from agents import Victim
from agents import Aggressor
import random


class GunSIM:
    def __init__(self, policy_mugger, policy_victim):
        self.policy_mugger = policy_mugger
        self.policy_victim = policy_victim
        self.victims = list()
        self.muggers = list()
        self.i = 0
        self.ii = 0
        self.iii = 0
        self.iv = 0
        self.homicide = 0
        self.jailed = 0

    def grow_victims(self, n=500):
        """
        Function that generates agents Victims
        :param n: number of agents of this type
        :return:
        """
        for i in range(n):
            self.victims.append(Victim(unique_id=i))
            # If a gun policy is active, there is a probability that the agent will posses a gun.
            if self.policy_victim:
                self.victims[i].has_gun = random.choices([True, False], [.1, .9])
            else:
                self.victims[i].has_gun = False

    def grow_robbers(self, n=15):
        """
        Function that generates the agents Aggressors
        :param n: number of agents of this type
        :return:
        """
        for i in range(n):
            self.muggers.append(Aggressor(unique_id=i))

    def theory_moves(self, victim, mugger):
        """
        A function that may change the agent's strategy based on Theory of Moves from Steven Brams(1993)
        :param victim:
        :param mugger:
        :return:
        """
        # Once each agent, mugger and victim, set a initial strategy, according to Theory of Moves(BRAMS, 1993),
        # individuals can make 'moves' in his initial position, changing the strategy base in a rational calculation
        # that leads to a better final outcome. Here, the changes may happen according to a probability.
        if mugger.s_aggressor[0] == 'nForce' and victim.s_victim[0] == 'Coop':
            victim.s_victim[0] = 'Coop' if random.random() < .90 else 'React'
        elif mugger.s_aggressor[0] == 'nForce' and victim.s_victim[0] == 'React':
            victim.s_victim[0] = 'React' if random.random() < .05 else 'Coop'
        elif mugger.s_aggressor[0] == 'Force' and victim.s_victim[0] == 'Coop':
            victim.s_victim[0] = 'Coop' if random.random() < .85 else 'React'
        elif mugger.s_aggressor[0] == 'Force' and victim.s_victim[0] == 'React':
            victim.s_victim[0] = 'React' if random.random() < .38 else 'Coop'

        # if mugger.s_aggressor[0] == 'nForce':
        #     victim.s_victim[0] = 'Coop' if random.random() < .92 else 'React'
        # elif mugger.s_aggressor[0] == 'Force':
        #     victim.s_victim[0] = 'React' if random.random() < .08 else 'Coop'
        # elif victim.s_victim[0] == 'Coop':
        #     mugger.s_aggressor[0] = 'Force' if random.random() < .14 else 'nForce'
        # elif victim.s_victim[0] == 'React':
        #     mugger.s_aggressor[0] = 'Force' if random.random() < .86 else 'nForce'
        # Since the agents are satisfied with their chosen strategies we call a method to give the outcome to each
        # player. This distribution of rewards follows the structure of the Mugging Game(BRAMS, 1993)
        self.mugging_game(victim, mugger)

    def mugging_game(self, victim, mugger):
        """
        The payoff results from Mugging Game by Steven Brams(1993)
        :param victim:
        :param mugger:
        :return:
        """
        # I Fight: (2,2). The victim resists, and the mugger uses force. The mugger gets the victim's money but may
        # attract attention, whereas the victim is injured and loses its money. Nonetheless, the victim has achieved
        # its tertiary goal of increasing the probability of the mugger's arrest.
        if victim.s_victim[0] == 'React' and mugger.s_aggressor[0] == 'Force':
            mugger.wallet += victim.wallet
            self.i += 1
            if random.choices(['survive', 'perish'], [.82, .18]) == ['perish']:
                self.victims.remove(victim)
                self.homicide += 1
            if random.choices(['flew', 'caught'], [.5, .5]) == ['caught']:
                self.muggers.remove(mugger)
                self.jailed += 1
        # II Mugger fails: (4, 1). The victim resists the mugger, who is frightened away, and achieves all its goals.
        # The mugger achieves only its tertiary goal.
        elif victim.s_victim[0] == 'React' and mugger.s_aggressor[0] == 'nForce':
            self.ii += 1
            if random.choices(['flew', 'caught'], [.7, .3]) == ['caught']:
                self.muggers.remove(mugger)
                self.jailed += 1
        # III Voluntary submission: (3,4). The victim gives up its money, and the mugger leaves the victim
        # unharmed. The mugger achieves all its goals, whereas the victim achieves its primary goal of escaping
        # unharmed.
        elif victim.s_victim[0] == 'Coop' and mugger.s_aggressor[0] == 'nForce':
            self.iii += 1
            mugger.wallet += victim.wallet
        # IV Involuntary submission: ( 1 ,3). The victim gives up its money, but the mugger uses force anyway. The
        # victim achieves none of its goals, whereas the mugger achieves its two most important goals, sacrificing
        # only its tertiary goal by taking a greater risk of getting caught.
        elif victim.s_victim[0] == 'Coop' and mugger.s_aggressor[0] == 'Force':
            self.iv += 1
            mugger.wallet += victim.wallet
            if random.choices(['survive', 'perish'], [.95, .05]) == ['perish']:
                self.victims.remove(victim)
                self.homicide += 1
            if random.choices(['flew', 'caught'], [.5, .5]) == ['caught']:
                self.muggers.remove(mugger)
                self.jailed += 1

    def return_counter(self):
        return self.i, self.ii, self.iii, self.iv, self.homicide, self.jailed

    def step(self):
        """
        A function that mimics a unit of time. All the interactions are executed
        :return:
        """
        # Each victim from a list of victims have a 33% of chance of being mugged(e.g. being matched with a mugger).
        for victim in self.victims:
            match = random.random() < .33
            # Each match of a potential victim with a potential mugger can trigger a criminal activity
            if match:
                mugger = random.choice(self.muggers)
                if mugger.is_active():
                    # If criminal activity is triggered aggressor and victim make a initial decision on its response
                    # strategy. Note that agents take into account the existence of a policy.
                    mugger.set_strategy(suspicious=self.policy_mugger)
                    victim.set_strategy(prob_armed=self.policy_victim)
                    # Next its applied the Theory of Moves(BRAMS, 1993), a rationale for changing or not the previous
                    # strategy set by victim and aggressor
                    self.theory_moves(victim, mugger)


if __name__ == '__main__':
    brazil = GunSIM(policy_victim=True, policy_mugger=True)
    brazil.grow_robbers()
    brazil.grow_victims()
    brazil.step()
    print(brazil.return_counter())
