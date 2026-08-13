import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import csv

from pathlib import Path

# Diretorios de saida, resolvidos a partir da raiz do repositorio.
RAIZ = Path(__file__).resolve().parents[2]
SAIDA_CSV = RAIZ / 'resultados' / 'erdos_renyi' / 'csv'
SAIDA_FIG = RAIZ / 'resultados' / 'erdos_renyi' / 'figuras'
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
def dilema_prisioneiro(k):

    #parametros do grafo, grau medio <k> = p*N
    n = 1000
    p = k/n

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
    G = nx.erdos_renyi_graph(n, p)

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

    #descarte dos 1000 primeiros registros
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
    plt.title('Evolução Temporal - Erdos-renyi')
    plt.xlabel('Tempo')
    plt.ylabel('Fração de cooperadores')
    plt.grid(True)
    plt.text(0.95, 0.01, f'Prob. de conexão = {p}, <k> = {n*p}', 
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


    plt.savefig(SAIDA_FIG / f'Erdos_renyi_p_{p}.png')
    plt.close()
    #plt.show()

    return media_frac_coop, desvio_padrao_da_media

def loop():
    
    medias = []
    desvios = []
    graus_medios = []

    for k in range(2, 21, 2):
        start_loop_time = time.time()

        media, desvio = dilema_prisioneiro(k)
        medias.append(media)
        desvios.append(desvio)
        graus_medios.append(k)
        #print(medias, desvios, graus_medios)

        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"loop {round(k/2)} concluido em {loop_duration} segundos")
    
    with open(SAIDA_CSV / 'Dilema_erdos_results.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Grau_Medio', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'])
        for i in range(len(graus_medios)):
            csvwriter.writerow([graus_medios[i], medias[i], desvios[i]])
    
    
if __name__ == "__main__":
    start_time = time.time()
    loop()
    end_time = time.time()

    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")

''''
    # Plotando as médias e desvios em função do grau médio
    plt.figure(figsize=(10, 6))
    plt.errorbar(graus_medios, medias, yerr=desvios, label='Média da Fração de Cooperadores', capsize=5, fmt='o', markersize=2)
    plt.title('Modelo Erdös-Renyi')
    plt.xlabel('Grau Médio')
    plt.ylabel('Média da fração de colaboradores')
    plt.grid(True)
    plt.legend()
    plt.savefig('ER_Model.png')
    plt.show()

'''

    