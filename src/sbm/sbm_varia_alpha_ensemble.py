import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (diretorios, estatisticas, evoluir, geradores, salvar_csv,
                   salvar_figura, semente_base, semente_de_ponto,
                   sementes_de_realizacoes)

SAIDA_CSV, SAIDA_FIG = diretorios('sbm')

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'sbm_varia_alpha_ensemble'



# Função principal
def dilema_prisioneiro(sizes, p, n, semente):
    # Fracao de cooperadores no instante inicial.
    p_i = 0.5

    # Geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #grafo aleatorio
    G = nx.stochastic_block_model(sizes, p, nodelist=None, seed=gerador_numpy, directed=False, selfloops=False, sparse=True)

    #dinamica compartilhada: o laco vive em comum.evoluir
    t_list, frac_coop = evoluir(G, p_i, gerador_numpy, gerador_random, n)

    # Média e desvio, já descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    return media_frac_coop, desvio_padrao_da_media

def loop(semente):
    sizes = [250, 250, 250, 250]
    k = 4
    n = sum(sizes)

    num_simulations = 20  # Número de simulações por valor de alpha

    medias = []
    desvios = []
    alpha_list = []

    for alpha in np.arange(0.1, 1, 0.1):
        start_time_alpha = time.time()

        pd = 4 * k / (n * (1 + 3 * alpha))
        diag = pd
        n_diag = alpha * pd

        p = [[diag, n_diag, n_diag, n_diag], 
             [n_diag, diag, n_diag, n_diag], 
             [n_diag, n_diag, diag, n_diag], 
             [n_diag, n_diag, n_diag, diag]]

        # Listas para armazenar os resultados de cada simulação
        resultados_simulacoes = []

        # Uma semente por realizacao, derivada do ponto (k, alpha)
        sementes = sementes_de_realizacoes(
            semente_de_ponto(semente, VARREDURA, k, alpha), num_simulations)

        # Executando várias simulações para cada valor de alpha
        for semente_da_realizacao in sementes:
            media_frac_coop, desvio_padrao_da_media = dilema_prisioneiro(
                sizes, p, n, semente_da_realizacao)
            resultados_simulacoes.append(media_frac_coop)

        # Calculando a média e o desvio padrão da média das simulações
        media_final = np.mean(resultados_simulacoes)
        desvio_padrao_final = np.std(resultados_simulacoes) / np.sqrt(num_simulations)

        medias.append(media_final)
        desvios.append(desvio_padrao_final)
        alpha_list.append(alpha)

        end_time_alpha = time.time()
        print(f"Tempo de execução para alpha = {round(alpha, 1)}: {round(end_time_alpha - start_time_alpha, 2)} segundos")

    print(medias, "\n", desvios)

    # Salvando as listas em um arquivo CSV
    salvar_csv(
        SAIDA_CSV / f'sbm_alpha_k_{k}_20sim.csv',
        ['Alpha', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'],
        ([round(alpha_list[i], 1), medias[i], desvios[i]] for i in range(len(alpha_list))),
        semente=semente,
    )

    plt.figure(figsize=(8, 5))
    plt.errorbar(alpha_list, medias, yerr=desvios, fmt='o', capsize=5, markersize=5)
    plt.title(f'SBM: fração de cooperadores x alpha ({num_simulations} realizações)', fontsize=13)
    plt.xlabel('Alpha', fontsize=14)
    plt.ylabel('Média da fração de cooperadores', fontsize=14)
    plt.ylim(0, 1)
    plt.grid(True)
    salvar_figura(plt, SAIDA_FIG / f'sbm_alpha_k_{k}_{num_simulations}sim.png')

if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
