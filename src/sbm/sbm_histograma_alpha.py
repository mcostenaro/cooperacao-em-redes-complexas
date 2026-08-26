import networkx as nx
import numpy as np
import time
import sys
import matplotlib.pyplot as plt
from multiprocessing import Pool

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (diretorios, estatisticas, evoluir, geradores, processos, salvar_csv,
                   salvar_figura, semente_base, semente_de_ponto,
                   sementes_de_realizacoes)

SAIDA_CSV, SAIDA_FIG = diretorios('sbm')

# Rotulo desta simulacao nas sementes derivadas.
VARREDURA = 'sbm_histograma_alpha'

# Main simulation function
def dilema_prisioneiro(sizes, p, n, np_random, random_gen):
    # Fracao de cooperadores no instante inicial.
    p_i = 0.5

    # Grafo aleatorio
    G = nx.stochastic_block_model(
        sizes, p, nodelist=None, seed=np_random, directed=False, selfloops=False, sparse=True
    )

    # Dinamica compartilhada: o laco vive em comum.evoluir
    t_list, frac_coop = evoluir(G, p_i, np_random, random_gen, n)

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

    with Pool(processes=processos()) as pool:
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
