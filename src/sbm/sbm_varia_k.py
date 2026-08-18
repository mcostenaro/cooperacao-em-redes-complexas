import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (deve_registrar, diretorios, estatisticas, geradores,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   tempo, total_de_passos)

SAIDA_CSV, SAIDA_FIG = diretorios('sbm')

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'sbm_varia_k'


#função para pegar um nó aleatório
def get_random_node(graph, gerador_random):
    return gerador_random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node, gerador_random):
    return gerador_random.choice(list(graph.neighbors(node)))

#função principal
def dilema_prisioneiro(sizes, p, n, semente):

    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #tempo de evolucao, em varreduras
    t_list = [0.0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0

    prob = 0.5

    #grafo aleatório
    G = nx.stochastic_block_model(sizes, p, nodelist=None, seed=gerador_numpy, directed=False, selfloops=False, sparse=True)

    #atribuição de valores
    for i in G.nodes():
        G.nodes[i]['value'] = 1*(gerador_numpy.random() < 1-prob)
        
        #adicionando numero de cooperadores à lista
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    #lista em t = 0 de agentes cooperando
    coop.append(num_coop)

    #loop para evolucao temporal
    for i in range(total_de_passos(n)):

        #escolhendo nó
        random_node = get_random_node(G, gerador_random)

        if G.degree[random_node] >= 1:
            #escolhendo vizinho
            random_neighbour = get_random_neighbor(G, random_node, gerador_random)

            #valor do player 1 e 2
            p1_v = G.nodes[random_node]['value']
            p2_v = G.nodes[random_neighbour]['value']

            #0 = coopera, 1 = delata
            if p1_v == 0:
                #se p2_v = 0, ambos cooperam  
                if p2_v == 1:
                    #p1 deixa de cooperar
                    G.nodes[random_node]['value'] = 1
                    num_coop -= 1
            else:
                if p2_v == 0:
                    #p2 deixa de cooperar
                    G.nodes[random_neighbour]['value'] = 1
                    num_coop -= 1
                else:
                    #ambos delatam
                    G.nodes[random_node]['value'] = 0
                    G.nodes[random_neighbour]['value'] = 0
                    num_coop += 2

        #registro da serie temporal
        if deve_registrar(i):
            t_list.append(tempo(i, n))
            coop.append(num_coop)


    #fracao de cooperadores
    frac_coop = [x/n for x in coop]

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
        SAIDA_CSV / f'Dilema_SBM_results_alpha_{alpha}.csv',
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
    salvar_figura(plt, SAIDA_FIG / f'sbm_varia_k_alpha_{alpha}.png')


if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
