import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import multiprocessing as mp

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (PASSOS_POR_REGISTRO, deve_registrar, diretorios, geradores,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   sementes_de_realizacoes, tempo, total_de_passos)

SAIDA_CSV, SAIDA_FIG = diretorios('watts_strogatz')
SAIDA_FIG = SAIDA_FIG / 'transiente'

# Registros mantidos da serie: 2000 registros = 200 varreduras.
REGISTROS_TRANSIENTE_PLOT = 2000

# Realizacoes promediadas em cada curva.
REALIZACOES = 30

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'ws_transiente'


#função para pegar um nó aleatório
def get_random_node(graph, gerador_random):
    return gerador_random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node, gerador_random):
    return gerador_random.choice(list(graph.neighbors(node)))


#função principal
def dilema_prisioneiro(k, p, semente):

    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #parametros do grafo
    n = 1000 
    #k (int):   Each node is joined with its k nearest neighbors in a ring topology.
    #p (float): The probability of rewiring each edge

    #distribuição da quantidade de cooperadores iniciais
    p_i = 0.5
    
    #tempo de evolucao, em varreduras
    t_list = [0.0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0


    #grafo aleatório
    G = nx.watts_strogatz_graph(n, k, p, seed=gerador_numpy)

    #atribuição de valores
    for i in G.nodes():
        G.nodes[i]['value'] = 1*(gerador_numpy.random() < 1-p_i)
        
        #adicionando numero de cooperadores à lista
        if G.nodes[i]['value'] == 0:
            num_coop += 1

    #lista em t = 0 de agentes cooperando
    coop.append(num_coop)

    #loop para evolucao temporal
    for i in range(total_de_passos(n)):

        #escolhendo nó e seu vizinho
        random_node = get_random_node(G, gerador_random)
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

    return t_list[:REGISTROS_TRANSIENTE_PLOT], frac_coop[:REGISTROS_TRANSIENTE_PLOT]

#funcao para fazer varias simulações do tempo transiente do modelo WA
def multiplas_simulacoes(k, p, semente):
    # Uma semente por realizacao, derivada do ponto (k, p) e passada como
    # argumento da tarefa. No Windows o start method e spawn: o filho reimporta
    # o modulo e nao herda gerador nenhum do pai.
    sementes = sementes_de_realizacoes(semente_de_ponto(semente, VARREDURA, k, p),
                                       REALIZACOES)
    with mp.Pool() as pool:
        args_list = [(k, p, semente_da_realizacao) for semente_da_realizacao in sementes]
        results = pool.starmap(dilema_prisioneiro, args_list)
    # Extrair 'frac_coop' dos resultados
    lista_multipla = [frac_coop for _, frac_coop in results]
    # Calcular a média
    lista_multipla = np.mean(lista_multipla, axis=0)
    return lista_multipla

def gerar_listas(k, p, semente, n=1000):
    lista_das_medias = multiplas_simulacoes(k, p, semente)
    # Tempo em varreduras: cada registro vale PASSOS_POR_REGISTRO/n varreduras.
    t_list = [i * PASSOS_POR_REGISTRO / n for i in range(len(lista_das_medias))]

    return t_list, lista_das_medias

def main(k, semente):
    curvas = []

    for p in [0, 0.02, 0.2, 1]:
        start_p_time = time.time()

        #for k in range(2, 11, 2):
         #   start_k_time = time.time()
          #  gerar_grafico(k, p)
           # end_k_time = time.time()

            #print(f"looping para {k} completo em: {round(end_k_time - start_k_time, 2)} segundos")

        t_list, medias = gerar_listas(k, p, semente)
        curvas.append((p, t_list, medias))

        salvar_csv(
            SAIDA_CSV / f'ws_transiente_k_{k}_p_{p}.csv',
            ['Tempo_varreduras', 'Media_Frac_Coop'],
            zip(t_list, medias),
            semente=semente,
        )

        end_p_time = time.time()
        print(f"looping para {p} completo em: {round(end_p_time - start_p_time, 2)} segundos")

    # Uma figura por k, com as quatro curvas de p sobrepostas.
    plt.figure(figsize=(10, 6))
    for p, t_list, medias in curvas:
        plt.plot(t_list, medias, label=f'p = {p}', linewidth=1.5)
    plt.title(f'Dinâmica do transiente - Watts-Strogatz (k = {k})', fontsize=15)
    plt.xlabel('Tempo (varreduras)', fontsize=15)
    plt.ylabel('Média da fração de cooperadores', fontsize=15)
    plt.ylim(0.4, 1.05)
    plt.grid(True)
    plt.legend(loc='upper right')
    plt.tick_params(axis='both', which='major', labelsize=13)
    salvar_figura(plt, SAIDA_FIG / f'ws_transiente_k_{k}.png')


def loop(semente):
    start_k_time = time.time()
    for k in [2, 6, 10]:
        main(k, semente)
    end_k_time = time.time()
    print(f"Tempo de execução: {round(end_k_time - start_k_time, 2)} segundos")

if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")


    