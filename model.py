from agents import Victim
from agents import Aggressor
import random


def start_sankey(agent_m, agent_v):
    with open('start.txt', 'a') as f:
        f.write(f'{agent_m.s_aggressor[0]}\n')
        f.write(f'{agent_v.s_victim[0]}\n')


def target_sankey(agent_m, agent_v):
    with open('target.txt', 'a') as f:
        f.write(f'{agent_m.s_aggressor[0]}\n')
        f.write(f'{agent_v.s_victim[0]}\n')


class GunSIM:
    def __init__(self, policy_mugger, policy_victim, has_gun=.5, prob_matching=.33):
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
        self.guns = 0
        # Preparing for sensitivity analysis
        self.has_gun = has_gun
        self.prob_matching = prob_matching

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
                self.victims[i].has_gun = random.choices([True, False], [self.has_gun, 1 - self.has_gun])
                if self.victims[i].has_gun[0]:
                    self.guns += 1
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

        # According to Brams the initial states are (4, 1 )("mugger fails") or (3,4) ("voluntary submission")
        if mugger.s_aggressor[0] == 'nForce':
            if victim.s_victim[0] == 'Coop':  # It is rational to prefer stand in (3,4) ("voluntary submission")
                victim.s_victim[0] = 'Coop' if random.random() < .86 else 'React'
            elif victim.s_victim[0] == 'React':  # So it is changing from (4,1) ("voluntary submission") to (3,4)
                victim.s_victim[0] = 'Coop' if random.random() < .9 else 'React'
                if victim.s_victim[0] == 'React':  # But if victim remain resistant, it is rational to mugger use force
                    mugger.s_aggressor[0] = 'Force' if random.random() < .9 else 'nForce'
        elif mugger.s_aggressor[0] == 'Force':
            victim.s_victim[0] = 'Coop' if random.random() < .95 else 'React'
        target_sankey(mugger, victim)
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
            if random.choices(['survive', 'perish'], [.9, .1]) == ['perish']:
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
            if random.choices(['survive', 'perish'], [.93, .07]) == ['perish']:
                self.victims.remove(victim)
                self.homicide += 1
            if random.choices(['flew', 'caught'], [.5, .5]) == ['caught']:
                self.muggers.remove(mugger)
                self.jailed += 1

    def return_counter(self):
        return self.i, self.ii, self.iii, self.iv, self.homicide, self.jailed, self.guns, self.has_gun

    def step(self):
        """
        A function that mimics a unit of time. All the interactions are executed
        :return:
        """
        # Each victim from a list of victims have a 33% of chance of being mugged(e.g. being matched with a mugger).
        for victim in self.victims:
            match = random.random() < self.prob_matching
            # Each match of a potential victim with a potential mugger can trigger a criminal activity
            if match:
                mugger = random.choice(self.muggers)
                if mugger.is_active():
                    # If criminal activity is triggered aggressor and victim make a initial decision on its response
                    # strategy. Note that agents take into account the existence of a policy.
                    mugger.set_strategy(suspicious=self.policy_mugger)
                    victim.set_strategy(prob_armed=self.policy_victim)
                    start_sankey(mugger, victim)
                    # Next its applied the Theory of Moves(BRAMS, 1993), a rationale for changing or not the previous
                    # strategy set by victim and aggressor
                    self.theory_moves(victim, mugger)


if __name__ == '__main__':
    brazil = GunSIM(policy_victim=True, policy_mugger=True)
    brazil.grow_robbers()
    brazil.grow_victims()
    brazil.step()
    print(brazil.return_counter())
