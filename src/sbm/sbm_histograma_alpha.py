import networkx as nx
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (deve_registrar, diretorios, estatisticas, geradores,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   sementes_de_realizacoes, tempo, total_de_passos)

SAIDA_CSV, SAIDA_FIG = diretorios('sbm')

# Rotulo desta simulacao nas sementes derivadas.
VARREDURA = 'sbm_histograma_alpha'

# Function to get a random node
def get_random_node(graph, random_gen):
    return random_gen.choice(list(graph.nodes()))

# Function to get a random neighbor of a node
def get_random_neighbor(graph, node, random_gen):
    return random_gen.choice(list(graph.neighbors(node)))

# Main simulation function
def dilema_prisioneiro(sizes, p, n, np_random, random_gen):
    t_list = [0.0]
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

    for i in range(total_de_passos(n)):
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

        if deve_registrar(i):
            t_list.append(tempo(i, n))
            coop.append(num_coop)

    frac_coop = [x / n for x in coop]

    # Média e desvio, já descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    return media_frac_coop, desvio_padrao_da_media

# Function to run a single simulation
def run_simulation(args):
    # A semente vem como argumento da tarefa, nao do estado do processo pai: no
    # Windows o start method e spawn, o filho reimporta este modulo do zero e
    # nao herda gerador nenhum. Antes daqui saia um SeedSequence() sem entropia
    # fixa, o que tornava cada execucao irrepetivel.
    sizes, p, n, semente = args
    np_random, random_gen = geradores(semente)
    media_frac_coop, _ = dilema_prisioneiro(sizes, p, n, np_random, random_gen)
    return media_frac_coop

# Main function adapted for a fixed value of alpha
def loop(semente):
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

    # Uma semente por realizacao, derivada do ponto (k, alpha)
    sementes = sementes_de_realizacoes(
        semente_de_ponto(semente, VARREDURA, k, alpha), num_simulations)

    num_processes = min(8, cpu_count() - 2)  # Use up to 8 processes, leaving 2 CPUs free
    with Pool(processes=num_processes) as pool:
        resultados_simulacoes = pool.map(
            run_simulation,
            [(sizes, p, n, semente_da_realizacao) for semente_da_realizacao in sementes]
        )

    end_sim_time = time.time()
    print(f"Simulations completed in {round(end_sim_time - start_sim_time, 2)} seconds.")

    media_final = np.mean(resultados_simulacoes)
    desvio_padrao_final = np.std(resultados_simulacoes) / np.sqrt(num_simulations)

    print(f"Mean fraction of cooperators: {media_final}")
    print(f"Standard deviation of the mean: {desvio_padrao_final}")

    # Salva as realizacoes brutas, para poder refazer o histograma sem resimular.
    salvar_csv(
        SAIDA_CSV / f'sbm_histograma_alpha_{alpha}_k_{k}.csv',
        ['Realizacao', 'Media_Frac_Coop'],
        enumerate(resultados_simulacoes),
        semente=semente,
    )

    # Generate the histogram
    print("Generating histogram...")
    hist_start_time = time.time()

    plt.figure(figsize=(8, 5))
    plt.hist(resultados_simulacoes, bins=20, alpha=0.75, edgecolor='black')
    plt.title(f'Histograma da fração de cooperadores (alpha = {alpha}, {num_simulations} realizações)', fontsize=12)
    plt.xlabel('Média da fração de cooperadores', fontsize=13)
    plt.ylabel('Frequência', fontsize=13)
    plt.grid(True)
    salvar_figura(plt, SAIDA_FIG / f'sbm_histograma_alpha_{alpha}_k_{k}.png')

    hist_end_time = time.time()
    print(f"Histogram generated in {round(hist_end_time - hist_start_time, 2)} seconds.")

# Code execution
if __name__ == "__main__":
    start_time = time.time()
    print("Starting code execution...")

    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)

    end_time = time.time()
    print(f"Total execution time: {round(end_time - start_time, 2)} seconds.")
    print(f"Total execution time: {round((end_time - start_time)/60, 2)} minutes.")
