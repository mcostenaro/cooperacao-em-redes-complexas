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


#função para pegar um nó aleatório
def get_random_node(graph):
    return random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node):
    return random.choice(list(graph.neighbors(node)))

#função de atribuição


#função principal
def dilema_prisioneiro(sizes, p, n):
    
    #tempo de evolucao
    t = 0
    t_list = [0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0

    prob = 0.5

    #grafo aleatório
    G = nx.stochastic_block_model(sizes, p, nodelist=None, seed=None, directed=False, selfloops=False, sparse=True)

    #atribuição de valores 
    for i in G.nodes():
        G.nodes[i]['value'] = 1*(np.random.random() < 1-prob)
        
        #adicionando numero de cooperadores à lista
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    #lista em t = 0 de agentes cooperando
    coop.append(num_coop)

    #loop para evolucao temporal
    for i in range(1000*n):

        #escolhendo nó
        random_node = get_random_node(G)

        if G.degree[random_node] >= 1:
            #escolhendo vizinho 
            random_neighbour = get_random_neighbor(G, random_node)

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

        #passo
        if i%1000 == 0 and i != 0:
            t += 1
            t_list.append(t)
            coop.append(num_coop)


    #fracao de cooperadores
    frac_coop = [x/n for x in coop]

    #descarte dos 100 primeiros registros
    coop_resultante = frac_coop[100:]

    # Desvio padrão dos cooperadores
    desvio_padrao = np.std(coop_resultante)

    # Desvio padrão da média
    N = len(coop_resultante)
    desvio_padrao_da_media = desvio_padrao / np.sqrt(N)

    #media dos cooperadores 
    media_frac_coop = np.mean(coop_resultante)

    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(t_list, frac_coop, color='blue')
    plt.title('Evolução temporal - SBM')
    plt.xlabel('Tempo')
    plt.ylabel('Fração de cooperadores')
    plt.grid(True)

    plt.text(0.25, 0.01, f'média = {round(media_frac_coop, 3)}', 
             verticalalignment='bottom', horizontalalignment='right', 
             transform=plt.gca().transAxes,
             color='black', fontsize=12)
    
    plt.text(0.5, 0.01, f'desvio = {round(desvio_padrao_da_media, 3)}', 
             verticalalignment='bottom', horizontalalignment='right', 
             transform=plt.gca().transAxes,
             color='black', fontsize=12)

    plt.savefig(SAIDA_FIG / 'SBM_verificacao.png')
    plt.close()

    return media_frac_coop, desvio_padrao_da_media

def loop():

    sizes = [250, 250, 250, 250]
    k = 4
    n = sum(sizes)

    medias = []
    desvios = []
    alpha_list = [] 


    for alpha in np.arange(0.1, 1, 0.1):
        start_time_alpha = time.time()

        pd = 4 * k / (n * (1 + 3*alpha))
        diag = pd
        n_diag = alpha * pd


        p = [[diag, n_diag, n_diag, n_diag], [n_diag, diag, n_diag, n_diag], [n_diag, n_diag, diag, n_diag], [n_diag, n_diag, n_diag, diag]]

        media_frac_coop, desvio_padrao_da_media = dilema_prisioneiro(sizes, p, n)

        medias.append(media_frac_coop)
        desvios.append(desvio_padrao_da_media)
        alpha_list.append(alpha)

        end_time_alpha = time.time()

        print(f"Tempo de execução para alpha = {round(alpha,1)}: {round(end_time_alpha - start_time_alpha, 2)} segundos")

    print(medias, "\n", desvios)

    # Salvando as listas em um arquivo CSV
    with open(SAIDA_CSV / f'sbm_alpha_k_{k}_1sim.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['alpha', 'Media da fração de coooperadores', 'Desvio_Padrao_da_Media'])
        for i in range(len(alpha_list)):
            csvwriter.writerow([round(alpha_list[i], 1), medias[i], desvios[i]])


if __name__ == "__main__":
    start_time = time.time()
    loop()
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
