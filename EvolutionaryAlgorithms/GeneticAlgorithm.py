import random
from tqdm import tqdm
import pandas as pd
import numpy as np
from scipy import stats
import warnings
import time
import sys
import os

from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import hamming_loss, classification_report
from sklearn.metrics import (
    accuracy_score,
    label_ranking_loss,
    coverage_error,
    average_precision_score,
    zero_one_loss,
)
from sklearn.metrics import label_ranking_average_precision_score
from sklearn.metrics import jaccard_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score

from numba import jit, njit, vectorize, cuda, uint32, f8, uint8

warnings.filterwarnings("ignore")


class GeneticAlgorithm:
    def __init__(self, chromosome_size, conditional_entropy_matrix) -> None:
        #print("GA Activated!")
        self.chromosome_size = chromosome_size
        self.conditional_entropy_matrix = conditional_entropy_matrix
        self.gene_pool = [i + 1 for i in range(chromosome_size)]

    def fitness_fn(self, chromosome):
        # This fitness function calculates the upper triangular matrix of Conditional Entropy
        # after it is rearranged according to the given chromosome / permutation

        # Reaarangement
        fitness_val = 0
        for i,idx1 in enumerate(chromosome):
            for j,idx2 in enumerate(chromosome):
                if i < j:
                    fitness_val = fitness_val + self.conditional_entropy_matrix[idx1 - 1][idx2 - 1]

        return fitness_val
        # Permute matrix according to row and column order
        # with tf.Session() as sess:
        #   order = tf.constant(chromosome)
        #   permuted_rows = tf.gather(self.conditional_entropy_matrix, order)
        #   output_matrix = tf.transpose(tf.gather(tf.transpose(permuted_rows), order))
        #   upper_triangular = tf.matrix_band_part(output_matrix, 0, -1)
        #   return tf.reduce_sum(upper_triangular).eval(session=sess)

    def generate_individual(self):
        # Generate a random permutation of the gene pool
        individual = self.gene_pool.copy()
        random.shuffle(individual)
        return individual

    # def tournament_selection(self, population, fitness_scores):
    #     # Select parents using tournament selection
    #     num_parents = len(population)
    #     parents = []
    #     for i in range(num_parents):
    #         competitors = random.sample(list(enumerate(population)), k=2)
    #         winner = max(competitors, key=lambda x: fitness_scores[x[0]])
    #         parents.append(winner[1])
    #     return parents

    def roulette_selection(self, population, fitness_scores):
        num_parents = len(population)
        parents = []
        for i in range(num_parents):
            prob = random.uniform(0, sum(fitness_scores))
            for j, fitness_val in enumerate(fitness_scores):
                if prob <= 0:
                    break
                prob -= fitness_val
            parents.append(population[j])
        return parents

    def crossover_helper(self, parent1, parent2, start, end):
        child = []
        for i in range(start):
            if parent2[i] not in parent1[start : end]:
                child.append(parent2[i])

        child = child + parent1[start : end]
        for i in range(start, self.chromosome_size):
            if parent2[i] not in parent1[start : end]:
                child.append(parent2[i])

        return child


    def find_cycles(self,chromosome,index,seen,path):
        seen.add(index)
        path.append(index)
        next = chromosome[index]

        if next not in seen:
          self.find_cycles(chromosome,next,seen,path)

    def cyclic_shift(self,array,shift):
        shift %= len(array)
        return array[shift:] + array[:shift]

    def cyclic_mutation(self,chromosome,mutation_rate,swap = False):
        seen = set()
        gene = [value - 1 for value in chromosome]
        chromosome = gene.copy()

        for i,value in enumerate(gene):
          if i not in seen:
            path = []
            self.find_cycles(chromosome,i,seen,path)
            if random.random() <= mutation_rate:
              if swap is True:
                first,last = path[0],path[-1]
                gene[first],gene[last] = gene[last],gene[first]
              else:
                shift = random.choice(list(range(len(chromosome))))
                shifted_path = self.cyclic_shift(path,shift)

                for src_index,dest_index in zip(path,shifted_path):
                  gene[src_index] = chromosome[dest_index]

        chromosome = [value + 1 for value in chromosome]
        return [value + 1 for value in gene]

    def ordered_crossover(self, population, parent1, parent2, crossover_rate):
        # Ordered Crossover by selecting a random section of the parents
        start = random.randint(0, self.chromosome_size - 1)
        end = random.randint(start + 1, self.chromosome_size)
        child1 = []
        child2 = []
        if random.random() < crossover_rate:
            # print("Crossover")
            # print(parent1,parent2)
            child1 = self.crossover_helper(parent1, parent2, start, end)
            child2 = self.crossover_helper(parent2, parent1, start, end)
            #print(child1,child2)
        else:
            child1, child2 = random.sample(population, k = 2)
        return child1, child2

    def mutate(self, chromosome, mutation_rate):
        # Mutate by randomly swapping two genes with the given mutation rate
        #print("Mutation: ")
        mutated_individual = chromosome.copy()
        if random.random() < mutation_rate:
            # print(mutated_individual)
            i = random.randint(0, len(mutated_individual) - 1)
            j = random.randint(0, len(mutated_individual) - 1)
            mutated_individual[i], mutated_individual[j] = mutated_individual[j], mutated_individual[i]
            #print(mutated_individual)
        return mutated_individual

    def reproduction(self, parents, population, population_size, crossover_rate):
        # Reproduce by randomly combining pairs of parents and performing crossover
        temp_parents = parents.copy()
        offspring = []
        while len(offspring) < population_size:
            father, mother = random.sample(temp_parents, k = 2)
            child1, child2 = self.ordered_crossover(population, father, mother, crossover_rate)
            offspring.append(child1)
            offspring.append(child2)
            temp_parents.remove(father)
            temp_parents.remove(mother)
        return offspring

    def refine_population(self, offspring, parents, elitism_rate, population_size):
        prev_gen = parents.copy()
        new_gen = offspring.copy()
        prev_gen.sort(key = self.fitness_fn, reverse = True)
        new_gen.sort(key = self.fitness_fn, reverse = True)

        new_population = prev_gen[:elitism_rate] + new_gen[:population_size - elitism_rate]
        return new_population

    def genetic_algorithm(self, population_size = 5, num_generations = 1, mutation_rate = 0.01, crossover_rate = 0.9, elitism_rate = 5):
        # Initialize the population
        population = [self.generate_individual() for i in range(population_size)]
        # print("Population:-")
        # print(population)
        #with tf.Session() as sess:
        for i in range(num_generations):
            # Evaluate the fitness of each individual
            #print("Doing generation")
            fitness_scores = [self.fitness_fn(chromosome) for chromosome in population]
            #print(fitness_scores)
            # Select the parents for the next generation
            parents = self.roulette_selection(population, fitness_scores)
            #print(f"Parents: {parents}")

            # Reproduce to create the next generation
            offspring = self.reproduction(parents, population, population_size, crossover_rate)
            #print(f"Offsprings: {offspring}")

            # Mutate the offspring
            # mutated_offspring = [self.mutate(chromosome, mutation_rate) for chromosome in offspring]
            mutated_offspring = [self.cyclic_mutation(chromosome, mutation_rate) for chromosome in offspring]
            #print(f"Mutation: {mutated_offspring}")

            # Generate the new population using elitism
            population = self.refine_population(mutated_offspring, parents, elitism_rate, population_size)
            #print(f"New pop: {population}")
            #break
        #sess.close()
        print("GEN DONE")
        # Return the fittest individual
        return max(population, key = self.fitness_fn)
