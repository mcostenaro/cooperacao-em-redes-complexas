import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
from multiprocessing import Pool

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (deve_registrar, diretorios, estatisticas, geradores,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   sementes_de_realizacoes, tempo, total_de_passos)

SAIDA_CSV, SAIDA_FIG = diretorios('sbm')

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'sbm_varia_alpha_paralelo'


# Função para pegar um nó aleatório
def get_random_node(graph, random_gen):
    return random_gen.choice(list(graph.nodes()))

# Função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node, random_gen):
    return random_gen.choice(list(graph.neighbors(node)))

# Função principal de simulação
def dilema_prisioneiro(sizes, p, n, np_random, random_gen):
    # Tempo de evolução, em varreduras
    t_list = [0.0]
    # Lista de cooperação
    coop = []
    # Número de agentes cooperando
    num_coop = 0

    prob = 0.5

    # Grafo aleatório
    G = nx.stochastic_block_model(
        sizes, p, nodelist=None, seed=np_random, directed=False, selfloops=False, sparse=True
    )

    # Atribuição de valores
    for i in G.nodes():
        G.nodes[i]['value'] = 1 * (np_random.random() < 1 - prob)

        # Adicionando número de cooperadores à lista
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    # Lista em t = 0 de agentes cooperando
    coop.append(num_coop)

    # Loop para evolução temporal
    for i in range(total_de_passos(n)):

        # Escolhendo nó
        random_node = get_random_node(G, random_gen)

        if G.degree[random_node] >= 1:
            # Escolhendo vizinho
            random_neighbour = get_random_neighbor(G, random_node, random_gen)

            # Valor do player 1 e 2
            p1_v = G.nodes[random_node]['value']
            p2_v = G.nodes[random_neighbour]['value']

            # 0 = coopera, 1 = delata
            if p1_v == 0:
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
                    # Ambos delatam e mudam para cooperação
                    G.nodes[random_node]['value'] = 0
                    G.nodes[random_neighbour]['value'] = 0
                    num_coop += 2

        # Registro da série temporal
        if deve_registrar(i):
            t_list.append(tempo(i, n))
            coop.append(num_coop)

    # Fração de cooperadores
    frac_coop = [x / n for x in coop]

    # Média e desvio, já descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    return media_frac_coop, desvio_padrao_da_media

# Função para rodar uma simulação, retornando apenas a média da fração de cooperadores
def run_simulation(args):
    # A semente vem como argumento da tarefa, nao do estado do processo pai: no
    # Windows o start method e spawn, o filho reimporta este modulo do zero e
    # nao herda gerador nenhum. Antes daqui saia um SeedSequence() sem entropia
    # fixa, o que tornava cada execucao irrepetivel.
    sizes, p, n, semente = args
    np_random, random_gen = geradores(semente)
    media_frac_coop, _ = dilema_prisioneiro(sizes, p, n, np_random, random_gen)
    return media_frac_coop

# Função principal que executa o loop de variação de alpha e simulações paralelas
def loop(k, semente):
    sizes = [250, 250, 250, 250]
    n = sum(sizes)
    num_simulations = 25  # Número de simulações por valor de alpha

    medias = []
    desvios = []
    alpha_list = []

    for alpha in np.arange(0.1, 1, 0.1):
        start_time_alpha = time.time()

        pd = 4 * k / (n * (1 + 3 * alpha))
        diag = pd
        n_diag = alpha * pd

        # Matriz de probabilidades entre blocos
        p = [
            [diag, n_diag, n_diag, n_diag],
            [n_diag, diag, n_diag, n_diag],
            [n_diag, n_diag, diag, n_diag],
            [n_diag, n_diag, n_diag, diag],
        ]

        # Uma semente por realizacao, derivada do ponto (k, alpha)
        sementes = sementes_de_realizacoes(
            semente_de_ponto(semente, VARREDURA, k, alpha), num_simulations)

        # Usando Pool para paralelizar as simulações
        with Pool(processes=8) as pool:  # Ajuste o número de processos conforme o número de núcleos disponíveis
            resultados_simulacoes = pool.map(
                run_simulation,
                [(sizes, p, n, semente_da_realizacao) for semente_da_realizacao in sementes]
            )

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
        SAIDA_CSV / f'SBM_50s_{k}.csv',
        ['Alpha', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'],
        ([round(alpha_list[i], 1), medias[i], desvios[i]] for i in range(len(alpha_list))),
        semente=semente,
    )

    plt.figure(figsize=(8, 5))
    plt.errorbar(alpha_list, medias, yerr=desvios, fmt='o', capsize=5, markersize=5)
    plt.title(f'SBM: fração de cooperadores x alpha (<k> = {k}, {num_simulations} realizações)', fontsize=12)
    plt.xlabel('Alpha', fontsize=14)
    plt.ylabel('Média da fração de cooperadores', fontsize=14)
    plt.ylim(0, 1)
    plt.grid(True)
    salvar_figura(plt, SAIDA_FIG / f'SBM_alpha_k_{k}_{num_simulations}sim.png')


def loop_k(semente):
    for k in range(2, 21, 2):
        start_time_k = time.time()
        loop(k, semente)
        end_time_k = time.time()
        print(f"Tempo de execução: {round(end_time_k - start_time_k, 2)} segundos")
        print(f"Tempo de execução: {round((end_time_k - start_time_k)/60, 2)} minutos")


# Execução do código
if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop_k(SEMENTE)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
    print(f"Tempo de execução: {round((end_time - start_time)/60, 2)} minutos")
