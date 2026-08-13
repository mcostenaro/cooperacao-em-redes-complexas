import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import csv

from pathlib import Path

# Diretorios de saida, resolvidos a partir da raiz do repositorio.
RAIZ = Path(__file__).resolve().parents[2]
SAIDA_CSV = RAIZ / 'resultados' / 'watts_strogatz' / 'csv'
SAIDA_FIG = RAIZ / 'resultados' / 'watts_strogatz' / 'figuras'
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
def dilema_prisioneiro(k, p):

    #parametros do grafo
    n = 1000 
    #k (int):   Each node is joined with its k nearest neighbors in a ring topology.
    #p (float): The probability of rewiring each edge

    #distribuição da quantidade de cooperadores iniciais
    p_i = 0.5
    
    #tempo de evolucao
    t = 0
    t_list = [0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0


    #grafo aleatório
    G = nx.watts_strogatz_graph(n, k, p, seed=None)

    #atribuição de valores 
    for i in G.nodes():
        G.nodes[i]['value'] = 1*(np.random.random() < 1-p_i)
        
        #adicionando numero de cooperadores à lista
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    #lista em t = 0 de agentes cooperando
    coop.append(num_coop)

    #loop para evolucao temporal
    for i in range(1100*n):

        #escolhendo nó e seu vizinho
        random_node = get_random_node(G) 
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

    #descarte dos 1000 primeiros registros
    coop_resultante = frac_coop[1000:]

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
    plt.title('Evolução Temporal - Watts-Strogatz')
    plt.xlabel('Tempo')
    plt.ylabel('Fração de cooperadores')
    plt.grid(True)
    plt.text(0.95, 0.01, f'grau médio <k> = {k}', 
             verticalalignment='bottom', horizontalalignment='right', 
             transform=plt.gca().transAxes,
             color='black', fontsize=12)

    plt.text(0.25, 0.01, f'média = {round(media_frac_coop, 3)}', 
             verticalalignment='bottom', horizontalalignment='right', 
             transform=plt.gca().transAxes,
             color='black', fontsize=12)
    
    plt.text(0.5, 0.01, f'desvio = {round(desvio_padrao_da_media, 3)}', 
             verticalalignment='bottom', horizontalalignment='right', 
             transform=plt.gca().transAxes,
             color='black', fontsize=12)


    plt.savefig(SAIDA_FIG / f'Watts_strogatz_k_{k}_p_{round(p, 2)}.png')
    plt.close()
    #plt.show()

    return media_frac_coop, desvio_padrao_da_media


def loop(p):
    medias = []
    desvios = []
    grau_medios = []
    
    i = 0

#p = 0.0, 0.02, 1
#k = 2, 4, 6, 8, 10, 12, 14, 16, 18 e 20

    for k in range(2, 21, 2):
        start_loop_time = time.time()
        i = i+1

        media, desvio = dilema_prisioneiro(k, p)
        medias.append(media)
        desvios.append(desvio)
        grau_medios.append(k)
        #print(medias, desvios, ps)

        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"loop {i} concluido em {loop_duration} segundos")
    
    with open(SAIDA_CSV / f'WA_p_{p}.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['k', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'])
        for i in range(len(grau_medios)):
            csvwriter.writerow([round(grau_medios[i], 2), medias[i], desvios[i]])


def loop_p():
    start_p_time = time.time()
    for p in [0, 0.02, 0.2, 0.6, 1]:
        loop(p)
    end_p_time = time.time()

    print(f"Tempo de execução: {round(end_p_time - start_p_time, 2)} segundos")

    
if __name__ == "__main__":
    start_time = time.time()

    loop_p()
    
    end_time = time.time()

    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")


    