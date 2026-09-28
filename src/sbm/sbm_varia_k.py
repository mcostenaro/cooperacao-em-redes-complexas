import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (diretorios, estatisticas, evoluir, geradores, salvar_csv,
                   salvar_figura, semente_base, semente_de_ponto)

SAIDA_CSV, SAIDA_FIG = diretorios('sbm')

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'sbm_varia_k'



#função principal
def dilema_prisioneiro(sizes, p, n, semente):
    # Fracao de cooperadores no instante inicial.
    p_i = 0.5


    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #grafo aleatorio
    G = nx.stochastic_block_model(sizes, p, nodelist=None, seed=gerador_numpy, directed=False, selfloops=False, sparse=True)

    #dinamica compartilhada: o laco vive em comum.evoluir
    t_list, frac_coop = evoluir(G, p_i, gerador_numpy, gerador_random, n)

    #media e desvio, ja descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    return media_frac_coop, desvio_padrao_da_media

def loop(semente):

    sizes = [250, 250, 250, 250]
    alpha = 0.5
    n = sum(sizes)

    medias = []
    desvios = []
    k_list = []

    for k in range(2, 22, 2):
        start_time_k = time.time()

        pd = 4 * k / (n * (1 + 3*alpha))
        diag = pd
        n_diag = alpha * pd


        p = [[diag, n_diag, n_diag, n_diag], [n_diag, diag, n_diag, n_diag], [n_diag, n_diag, diag, n_diag], [n_diag, n_diag, n_diag, diag]]

        media_frac_coop, desvio_padrao_da_media = dilema_prisioneiro(
            sizes, p, n, semente_de_ponto(semente, VARREDURA, alpha, k))

        medias.append(media_frac_coop)
        desvios.append(desvio_padrao_da_media)
        k_list.append(k)

        end_time_k = time.time()

        print(f"Tempo de execução para k = {k}: {round(end_time_k - start_time_k, 2)} segundos")

    print(medias, "\n", desvios)

    # Salvando as listas em um arquivo CSV
    salvar_csv(
        SAIDA_CSV / f'sbm_grau_medio_alpha_{alpha}.csv',
        ['Grau_Medio', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'],
        ([round(k_list[i], 1), medias[i], desvios[i]] for i in range(len(k_list))),
        semente=semente,
    )

    plt.figure(figsize=(8, 5))
    plt.errorbar(k_list, medias, yerr=desvios, fmt='o', capsize=5, markersize=5)
    plt.title(f'SBM: fração de cooperadores x grau médio (alpha = {alpha})', fontsize=13)
    plt.xlabel('Grau médio', fontsize=14)
    plt.ylabel('Média da fração de cooperadores', fontsize=14)
    plt.ylim(0, 1)
    plt.grid(True)
    salvar_figura(plt, SAIDA_FIG / f'sbm_grau_medio_alpha_{alpha}.png')


if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
