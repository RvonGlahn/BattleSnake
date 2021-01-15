
class Individual:
    def __init__(self, initial_genome):
        # Genome should be 1D numpy array
        assert len(initial_genome.shape) == 1

        self.fitness = None
        self.genome = initial_genome

    def __str__(self):
        return "Individual(fitness={}, genome={})".format(self.fitness, self.genome)
