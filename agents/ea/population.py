import numpy as np
from agents.ea.individual import Individual
from random import shuffle


class Population:

    def __init__(self, population_size: int, genome_size: int, low: float, high: float):

        self.genome_size = genome_size
        self.population_size = population_size
        self.low = low
        self.high = high

        self.individuals = []
        for i in range(population_size):
            genome_array = np.random.uniform(low=self.low, high=self.high, size=genome_size)
            ind = Individual(genome_array)
            self.individuals.append(ind)

    def crossover(self, cx_prob: float = 1.0):

        shuffle(self.individuals)

        if self.population_size % 2 == 0:
            x = self.population_size
        else:
            x = self.population_size - 1

        for i in range(0, x, 2):
            chance = np.random.uniform(0, 1)
            if chance < cx_prob:
                indiv_1 = self.individuals[i].genome
                indiv_2 = self.individuals[i + 1].genome
                cut = np.random.randint(1, self.genome_size-1)
                new_1 = np.concatenate((indiv_1[:cut], (indiv_2[cut:])))
                new_2 = np.concatenate((indiv_2[:cut], (indiv_1[cut:])))
                self.individuals = np.append(self.individuals, Individual(new_1))
                self.individuals = np.append(self.individuals, Individual(new_2))

        # All population entries should still have the correct genome size
        assert all((i.genome.shape == (self.genome_size,) for i in self.individuals))

    def mutate(self, scale: float, mut_prob: float = None, only_new: bool = False):
        """
        Wikipedia:
        This operator adds a unit Gaussian distributed random value to the chosen gene.
        If it falls outside of the user-specified lower or upper bounds for that gene, the new gene value is clipped.
        This mutation operator can only be used for integer and float genes.
        """
        if mut_prob is None:
            mut_prob = 1.0 / self.genome_size

        # Step 1: If only_new is True, only mutate individuals that were appended by a crossover
        mut = self.individuals if not only_new else self.individuals[self.population_size:]
        
        for ind in mut:
            for i in range(self.genome_size):
                chance = np.random.uniform(0, 1)
                if chance < mut_prob:
                    ind.genome[i] += np.random.normal(0, scale)
                    if ind.genome[i] > self.high:
                        ind.genome[i] = self.high
                    if ind.genome[i] < self.low:
                        ind.genome[i] = self.low

    def evaluate(self, evaluator):

        for i in self.individuals:
            i.fitness = evaluator(i.genome)

    def select(self):

        value_list = []
        for ind in self.individuals:
            value_list.append(ind.fitness)
        index_list = np.argsort(value_list)
        self.individuals = self.individuals[index_list]
        self.individuals = self.individuals[::-1]            # Array umdrehen

        self.individuals = self.individuals[:self.population_size]
