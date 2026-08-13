import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time


#função para pegar um nó aleatório
def get_random_node(graph):
    return random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node):
    return random.choice(list(graph.neighbors(node)))

#função de recompensa ou punição
def calc_score(p1, p2):
    cooperacao_mutua = 1
    traicao_mutua = 3
    traido = 5
    traidor = 0

    if p1 == 0 and p2 == 0:
        # Ambos cooperam
        return cooperacao_mutua, cooperacao_mutua
    elif p1 == 1 and p2 == 1:
        # Ambos delatam
        return traicao_mutua, traicao_mutua
    elif p1 == 0 and p2 == 1:
        # p1 coopera, p2 delata
        return traido, traidor
    else:
        # p1 delata, p2 coopera
        return traidor, traido


#função principal
def dilema_prisioneiro():

    #parametros do grafo
    n = 1000
    m = 3

    #distribuição da quantidade de cooperadores iniciais, grau medio <k> = 2*m
    p = 0.5
    
    #tempo de evolucao
    t = 0
    t_list = [0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0


    #grafo aleatório
    G = nx.barabasi_albert_graph(n, m, seed=None, initial_graph=None)

    #atribuição de valores 
    for i in G.nodes():
        G.nodes[i]['value'] = 1*(np.random.random() < 1-p)
        G.nodes[i]['score'] = 0
        
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

        #score dos players
        score_p1, score_p2 = calc_score(p1_v, p2_v)

        #adicionando pontuação
        G.nodes[random_node]['score'] += score_p1
        G.nodes[random_neighbour]['score'] += score_p2

        #regra de atualização
        #o objetivo é que os players minimizem os pontos
        if G.nodes[random_node]['score'] > G.nodes[random_neighbour]['score']:
            if p1_v == 0:
                #para p2_v = 0 nao acontece nada
                if p2_v == 1: 
                    G.nodes[random_node]['value'] = 1
                    num_coop -= 1 
            else:
                if p2_v == 0:
                    G.nodes[random_neighbour]['value'] = 1
                    num_coop -= 1
                if p2_v == 1:
                    G.nodes[random_node]['value'] = 0
                    G.nodes[random_neighbour]['value'] = 0
                    num_coop += 2
        else:
            if p1_v == 0:
                if p2_v == 1:
                    G.nodes[random_node]['value'] = 1
                    num_coop -= 1
            if p1_v == 1:
                if p2_v == 0: 
                    G.nodes[random_neighbour]['value'] = 1
                    num_coop -= 1
                else:
                    G.nodes[random_node]['value'] = 0
                    G.nodes[random_neighbour]['value'] = 0
                    num_coop += 2




        '''#0 = coopera, 1 = delata
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
                num_coop += 2'''

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
    plt.title('Evolução temporal - Barabasi-albert')
    plt.xlabel('Tempo')
    plt.ylabel('Fração de cooperadores')
    plt.grid(True)
    plt.text(0.95, 0.01, f'm = {m}, <k> = {2*m}', 
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

    plt.show()

if __name__ == "__main__":
    start_time = time.time()
    dilema_prisioneiro()
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")


    