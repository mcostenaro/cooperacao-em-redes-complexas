import networkx as nx
import random
import numpy as np
import time
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

# Function to get a random node
def get_random_node(graph, random_gen):
    return random_gen.choice(list(graph.nodes()))

# Function to get a random neighbor of a node
def get_random_neighbor(graph, node, random_gen):
    return random_gen.choice(list(graph.neighbors(node)))

# Main simulation function
def dilema_prisioneiro(sizes, p, n, np_random, random_gen):
    t = 0
    coop = []
    num_coop = 0

    prob = 0.5

    # Use np_random as seed for the stochastic_block_model
    G = nx.stochastic_block_model(
        sizes, p, nodelist=None, seed=np_random, directed=False, selfloops=False, sparse=True
    )

    # Assign initial strategies to nodes
    for i in G.nodes():
        G.nodes[i]['value'] = 1 * (np_random.random() < 1 - prob)
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    coop.append(num_coop)

    for i in range(1000 * n):
        random_node = get_random_node(G, random_gen)
        if G.degree[random_node] >= 1:
            random_neighbour = get_random_neighbor(G, random_node, random_gen)
            p1_v = G.nodes[random_node]['value']
            p2_v = G.nodes[random_neighbour]['value']

            if p1_v == 0 and p2_v == 1:
                G.nodes[random_node]['value'] = 1
                num_coop -= 1
            elif p1_v == 1 and p2_v == 0:
                G.nodes[random_neighbour]['value'] = 1
                num_coop -= 1
            elif p1_v == 1 and p2_v == 1:
                G.nodes[random_node]['value'] = 0
                G.nodes[random_neighbour]['value'] = 0
                num_coop += 2

        if i % 1000 == 0 and i != 0:
            t += 1
            coop.append(num_coop)

    frac_coop = [x / n for x in coop]
    coop_resultante = frac_coop[100:]

    desvio_padrao = np.std(coop_resultante)
    desvio_padrao_da_media = desvio_padrao / np.sqrt(len(coop_resultante))
    media_frac_coop = np.mean(coop_resultante)

    return media_frac_coop, desvio_padrao_da_media

# Function to run a single simulation
def run_simulation(args):
    sizes, p, n = args
    # Initialize a unique SeedSequence for each process
    seed_seq = np.random.SeedSequence()
    np_random = np.random.default_rng(seed_seq)
    # Generate a seed for the random module and convert it to int
    random_seed = int(seed_seq.generate_state(1)[0])
    random_gen = random.Random(random_seed)
    media_frac_coop, _ = dilema_prisioneiro(sizes, p, n, np_random, random_gen)
    return media_frac_coop

# Main function adapted for a fixed value of alpha
def loop():
    sizes = [250, 250, 250, 250]
    k = 4
    n = sum(sizes)
    num_simulations = 200  # Number of simulations

    # Fixed value of alpha
    alpha = 0.5  # Adjust the value as desired

    pd = 4 * k / (n * (1 + 3 * alpha))
    diag = pd
    n_diag = alpha * pd

    p = [
        [diag, n_diag, n_diag, n_diag],
        [n_diag, diag, n_diag, n_diag],
        [n_diag, n_diag, diag, n_diag],
        [n_diag, n_diag, n_diag, diag],
    ]

    print(f"Starting simulations for alpha = {alpha}...")
    start_sim_time = time.time()

    num_processes = min(8, cpu_count() - 2)  # Use up to 8 processes, leaving 2 CPUs free
    with Pool(processes=num_processes) as pool:
        resultados_simulacoes = pool.map(
            run_simulation, [(sizes, p, n) for _ in range(num_simulations)]
        )

    end_sim_time = time.time()
    print(f"Simulations completed in {round(end_sim_time - start_sim_time, 2)} seconds.")

    media_final = np.mean(resultados_simulacoes)
    desvio_padrao_final = np.std(resultados_simulacoes) / np.sqrt(num_simulations)

    print(f"Mean fraction of cooperators: {media_final}")
    print(f"Standard deviation of the mean: {desvio_padrao_final}")

    # Generate the histogram
    print("Generating histogram...")
    hist_start_time = time.time()

    plt.hist(resultados_simulacoes, bins=20, alpha=0.75, edgecolor='black')
    plt.title('Histograma da média da fração de cooperadores para alpha fixo')
    plt.xlabel('Média da fração de cooperadores')
    plt.ylabel('Frequência')
    plt.grid(True)
    plt.show()

    hist_end_time = time.time()
    print(f"Histogram generated in {round(hist_end_time - hist_start_time, 2)} seconds.")

# Code execution
if __name__ == "__main__":
    start_time = time.time()
    print("Starting code execution...")

    loop()

    end_time = time.time()
    print(f"Total execution time: {round(end_time - start_time, 2)} seconds.")
    print(f"Total execution time: {round((end_time - start_time)/60, 2)} minutes.")
