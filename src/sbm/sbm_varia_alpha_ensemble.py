import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import csv

from pathlib import Path

# Diretorios de saida, resolvidos a partir da raiz do repositorio.
RAIZ = Path(__file__).resolve().parents[2]
SAIDA_CSV = RAIZ / 'resultados' / 'sbm' / 'csv'
SAIDA_FIG = RAIZ / 'resultados' / 'sbm' / 'figuras'
SAIDA_CSV.mkdir(parents=True, exist_ok=True)
SAIDA_FIG.mkdir(parents=True, exist_ok=True)


# Função para pegar um nó aleatório
def get_random_node(graph):
    return random.choice(list(graph.nodes()))

# Função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node):
    return random.choice(list(graph.neighbors(node)))

# Função principal
def dilema_prisioneiro(sizes, p, n):
    # Tempo de evolução
    t = 0
    t_list = [0]
    # Lista de cooperação
    coop = []
    # Número de agentes cooperando
    num_coop = 0

    prob = 0.5

    # Grafo aleatório
    G = nx.stochastic_block_model(sizes, p, nodelist=None, seed=None, directed=False, selfloops=False, sparse=True)

    # Atribuição de valores 
    for i in G.nodes():
        G.nodes[i]['value'] = 1 * (np.random.random() < 1 - prob)
        
        # Adicionando número de cooperadores à lista
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    # Lista em t = 0 de agentes cooperando
    coop.append(num_coop)

    # Loop para evolução temporal
    for i in range(1100 * n):
        # Escolhendo nó
        random_node = get_random_node(G)

        if G.degree[random_node] >= 1:
            # Escolhendo vizinho 
            random_neighbour = get_random_neighbor(G, random_node)

            # Valor do player 1 e 2
            p1_v = G.nodes[random_node]['value']
            p2_v = G.nodes[random_neighbour]['value']

            # 0 = coopera, 1 = delata
            if p1_v == 0:
                # Se p2_v = 0, ambos cooperam  
                if p2_v == 1:
                    # p1 deixa de cooperar
                    G.nodes[random_node]['value'] = 1
                    num_coop -= 1
            else:
                if p2_v == 0:
                    # p2 deixa de cooperar
                    G.nodes[random_neighbour]['value'] = 1
                    num_coop -= 1
                else:
                    # Ambos delatam
                    G.nodes[random_node]['value'] = 0
                    G.nodes[random_neighbour]['value'] = 0
                    num_coop += 2

        # Passo
        if i % 1000 == 0 and i != 0:
            t += 1
            t_list.append(t)
            coop.append(num_coop)

    # Fração de cooperadores
    frac_coop = [x / n for x in coop]

    # Descarte dos 1000 primeiros registros
    coop_resultante = frac_coop[1000:]

    # Desvio padrão dos cooperadores
    desvio_padrao = np.std(coop_resultante)

    # Desvio padrão da média
    N = len(coop_resultante)
    desvio_padrao_da_media = desvio_padrao / np.sqrt(N)

    # Média dos cooperadores 
    media_frac_coop = np.mean(coop_resultante)

    return media_frac_coop, desvio_padrao_da_media

def loop():
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

        # Executando várias simulações para cada valor de alpha
        for _ in range(num_simulations):
            media_frac_coop, desvio_padrao_da_media = dilema_prisioneiro(sizes, p, n)
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
    with open(SAIDA_CSV / f'sbm_alpha_k_{k}_20sim.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['alpha', 'Media da fração de coooperadores', 'Desvio_Padrao_da_Media'])
        for i in range(len(alpha_list)):
            csvwriter.writerow([round(alpha_list[i], 1), medias[i], desvios[i]])

if __name__ == "__main__":
    start_time = time.time()
    loop()
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
