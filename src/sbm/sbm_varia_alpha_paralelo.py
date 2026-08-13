import networkx as nx
import random
import numpy as np
import time
import csv
from multiprocessing import Pool

from pathlib import Path

# Diretorios de saida, resolvidos a partir da raiz do repositorio.
RAIZ = Path(__file__).resolve().parents[2]
SAIDA_CSV = RAIZ / 'resultados' / 'sbm' / 'csv'
SAIDA_FIG = RAIZ / 'resultados' / 'sbm' / 'figuras'
SAIDA_CSV.mkdir(parents=True, exist_ok=True)
SAIDA_FIG.mkdir(parents=True, exist_ok=True)


# Função para pegar um nó aleatório
def get_random_node(graph, random_gen):
    return random_gen.choice(list(graph.nodes()))

# Função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node, random_gen):
    return random_gen.choice(list(graph.neighbors(node)))

# Função principal de simulação
def dilema_prisioneiro(sizes, p, n, np_random, random_gen):
    # Tempo de evolução
    t = 0
    t_list = [0]
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
    for i in range(1000 * n):  # Ajuste o número de passos se necessário

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

        # Passo de registro
        if i % 1000 == 0 and i != 0:
            t += 1
            t_list.append(t)
            coop.append(num_coop)

    # Fração de cooperadores
    frac_coop = [x / n for x in coop]

    # Descartar os primeiros 1000 registros, mantendo a maior parte dos dados
    coop_resultante = frac_coop[100:]

    # Desvio padrão dos cooperadores
    desvio_padrao = np.std(coop_resultante)

    # Desvio padrão da média
    N = len(coop_resultante)
    desvio_padrao_da_media = desvio_padrao / np.sqrt(N)

    # Média dos cooperadores
    media_frac_coop = np.mean(coop_resultante)

    return media_frac_coop, desvio_padrao_da_media

# Função para rodar uma simulação, retornando apenas a média da fração de cooperadores
def run_simulation(args):
    sizes, p, n = args
    # Inicializa geradores de números aleatórios independentes para cada processo
    seed_seq = np.random.SeedSequence()
    np_random = np.random.default_rng(seed_seq)
    # Gera um seed para o módulo random e converte para int
    random_seed = int(seed_seq.generate_state(1)[0])
    random_gen = random.Random(random_seed)
    media_frac_coop, _ = dilema_prisioneiro(sizes, p, n, np_random, random_gen)
    return media_frac_coop

# Função principal que executa o loop de variação de alpha e simulações paralelas
def loop(k):
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

        # Usando Pool para paralelizar as simulações
        with Pool(processes=8) as pool:  # Ajuste o número de processos conforme o número de núcleos disponíveis
            resultados_simulacoes = pool.map(
                run_simulation, [(sizes, p, n) for _ in range(num_simulations)]
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
    with open(SAIDA_CSV / f'SBM_50s_{k}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['alpha', 'Media da fração de coooperadores', 'Desvio_Padrao_da_Media'])
        for i in range(len(alpha_list)):
            csvwriter.writerow([round(alpha_list[i], 1), medias[i], desvios[i]])


def loop_k():
    for k in range(2, 21, 2):
        start_time_k = time.time()
        loop(k)
        end_time_k = time.time()
        print(f"Tempo de execução: {round(end_time_k - start_time_k, 2)} segundos")
        print(f"Tempo de execução: {round((end_time_k - start_time_k)/60, 2)} minutos")


# Execução do código
if __name__ == "__main__":
    start_time = time.time()
    loop_k()
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
    print(f"Tempo de execução: {round((end_time - start_time)/60, 2)} minutos")
