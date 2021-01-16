import numpy as np

from agents.ea.population import Population


def main():
    mutation_probability = 1.0

    population = Population(population_size=10, genome_size=10, low=0.0, high=10.0)

    num_generations = 1
    for g in range(num_generations):
        population.crossover(cx_prob=0.65)
        population.mutate(scale=2, mut_prob=mutation_probability, only_new=True)
        population.evaluate()
        population.select()

        fitnesses = [g.fitness for g in population.individuals]
        avg_fitness = np.average(fitnesses)

        mutation_probability = 0.2

        mutation_probability = np.exp(-2 * (1.0 + avg_fitness))

        print("{:<15} {:<21} {:<25} {:>25}".format(f"Generation {g + 1}:",
                                                   f"max fitness {np.max(fitnesses):.3f}",
                                                   f"average fitness {avg_fitness:.3f}",
                                                   f"mutation probability {mutation_probability:.3f}"))


if __name__ == "__main__":
    main()
