import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import csv
import multiprocessing as mp

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
    for i in range(1000*n):

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
        if i%100 == 0 and i != 0:
            t += 1
            t_list.append(t)
            coop.append(num_coop)

    #fracao de cooperadores
    frac_coop = [x/n for x in coop]

    return t_list[:2000], frac_coop[:2000]

#funcao para fazer varias simulações do tempo transiente do modelo WA
def multiplas_simulacoes(k, p):
    with mp.Pool() as pool:
        args_list = [(k, p) for _ in range(30)]
        results = pool.starmap(dilema_prisioneiro, args_list)
    # Extrair 'frac_coop' dos resultados
    lista_multipla = [frac_coop for _, frac_coop in results]
    # Calcular a média
    lista_multipla = np.mean(lista_multipla, axis=0)
    return lista_multipla

def gerar_listas(k, p):
    lista_das_medias = multiplas_simulacoes(k, p)
    print(lista_das_medias)
    t_list = list(range(len(lista_das_medias)))

    return t_list, lista_das_medias

def main(k):
    for p in [0, 0.02, 0.2, 1]:
        start_p_time = time.time()

        #for k in range(2, 11, 2):
         #   start_k_time = time.time()
          #  gerar_grafico(k, p)
           # end_k_time = time.time()

            #print(f"looping para {k} completo em: {round(end_k_time - start_k_time, 2)} segundos")

        t_list, medias = gerar_listas(k, p)

        with open(SAIDA_CSV / f'WA_transiente_k_{k}_p_{p}.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['tempo', 'medias_das_fracoes'])
            for i in range(len(t_list)):
                csvwriter.writerow([t_list[i], medias[i]])

        end_p_time = time.time()
        print(f"looping para {p} completo em: {round(end_p_time - start_p_time, 2)} segundos")


def loop():
    start_k_time = time.time()
    for k in [2, 6, 10]:
        main(k)
    end_k_time = time.time()
    print(f"Tempo de execução: {round(end_k_time - start_k_time, 2)} segundos")

if __name__ == "__main__":
    start_time = time.time()
    loop()
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")


    