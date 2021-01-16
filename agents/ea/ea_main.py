import numpy as np
import yaml

from agents.ea.population import Population
from agents.Hyperparameters import Params_Anxious


def set_params(data, idx):
    Params_Anxious.ALPHA_DISTANCE_ENEMY_HEAD[idx] = data["HEAD"]
    Params_Anxious.BETA_DISTANCE_CORNERS[idx] = data["CORNERS"]
    Params_Anxious.GAMMA_DISTANCE_FOOD[idx] = data["FOOD"]
    Params_Anxious.EPSILON_NO_BORDER[idx] = data["NO_BORDER"]
    Params_Anxious.THETA_DISTANCE_MID[idx] = data["MID"]

    Params_Anxious.OMEGA_FLOOD_FILL_MAX[idx] = data["FLOOD_FILL_MAX"]
    Params_Anxious.OMEGA_FLOOD_FILL_MIN[idx] = data["FLOOD_FILL_MIN"]
    Params_Anxious.OMEGA_FLOOD_DEAD[idx] = data["FLOOD_FILL_DEAD"]
    Params_Anxious.RHO_ESCAPE_CORRIDOR[idx] = data["ESCAPE_CORRIDOR"]
    Params_Anxious.TAU_PATH_LENGTH[idx] = data["PATH_LENGTH"]


def main():
    index = 0
    mutation_probability = 1.0
    with open("params.yaml", 'r') as stream:
        data = yaml.safe_load(stream)
        set_params(data, index)

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
