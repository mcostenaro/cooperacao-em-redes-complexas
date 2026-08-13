import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np
import time
import csv

from pathlib import Path

# Diretorios de saida, resolvidos a partir da raiz do repositorio.
RAIZ = Path(__file__).resolve().parents[2]
SAIDA_CSV = RAIZ / 'resultados' / 'barabasi_albert' / 'csv'
SAIDA_FIG = RAIZ / 'resultados' / 'barabasi_albert' / 'figuras'
SAIDA_CSV.mkdir(parents=True, exist_ok=True)
SAIDA_FIG.mkdir(parents=True, exist_ok=True)


#função para pegar um nó aleatório
def get_random_node(graph):
    return random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node):
    return random.choice(list(graph.neighbors(node)))

#função principal
def dilema_prisioneiro(n, m):

    #distribuição da quantidade de cooperadores iniciais, grau medio <k> = 2*m
    p = 0.9
    
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

    #descarte dos 1000 primeiros registros
    coop_resultante = frac_coop[100:]

    # Desvio padrão dos cooperadores
    desvio_padrao = np.std(coop_resultante)

    # Desvio padrão da média
    N = len(coop_resultante)
    desvio_padrao_da_media = desvio_padrao / np.sqrt(N)

    #media dos cooperadores 
    media_frac_coop = np.mean(coop_resultante)

    #lista de cooperadores transientes
    coop_trans = frac_coop[:200]
    t_list_trans = t_list[:200]

    # Salvar os dados em um arquivo CSV
    with open(SAIDA_CSV / f'fracao_de_cooperadores{p}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Tempo', 'Fracao_Cooperadores'])
        writer.writerows(zip(t_list_trans, coop_trans))
    print("Dados salvos em 'fracao_de_cooperadores.csv'.")
    
    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(t_list_trans, coop_trans, color='blue')
    plt.title('Evolução temporal - Barabási-Albert', fontsize=26)  # Aumentar o título
    plt.xlabel('Tempo', fontsize=20)  # Aumentar o rótulo do eixo X
    plt.ylabel('Fração de cooperadores', fontsize=20)  # Aumentar o rótulo do eixo Y
    plt.ylim(0, 1)  # Definindo o limite do eixo Y entre 0 e 1
    plt.xlim(0, None)
    plt.grid(True)

    # Ajustar o tamanho dos números dos ticks dos eixos
    plt.tick_params(axis='both', which='major', labelsize=20)

    # Adicionar texto no gráfico, incluindo a probabilidade inicial p_0
    plt.text(0.95, 0.01, f'<k> = {2*m}, $P_{{0}}$ =  {p}', 
            verticalalignment='bottom', horizontalalignment='right', 
            transform=plt.gca().transAxes,
            color='black', fontsize=20)

    # Salvar o gráfico
    plt.savefig(SAIDA_FIG / f'barabasi_albert_m_{m}.png')
    plt.close()



    return media_frac_coop, desvio_padrao_da_media

def loop():

    medias = []
    desvios = []
    graus_medios = []

    for m in range(1, 11):
        start_loop_time = time.time()

        media, desvio = dilema_prisioneiro(1000, m)
        medias.append(media)
        desvios.append(desvio)
        graus_medios.append(2*m)
    
        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"loop {round(m)} concluido em {loop_duration} segundos")
    
    with open(SAIDA_CSV / 'Dilema_Barabasi_p09.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Grau_Medio', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'])
        for i in range(len(graus_medios)):
            csvwriter.writerow([graus_medios[i], medias[i], desvios[i]])

if __name__ == "__main__":
    start_time = time.time()
    #loop()
    dilema_prisioneiro(1000, 4)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")



'''
  # Plotando as médias e desvios em função do grau médio
    plt.figure(figsize=(10, 6))
    plt.errorbar(graus_medios, medias, yerr=desvios, label='Média da Fração de Cooperadores', capsize=5, fmt='o', markersize=2)
    plt.title('Modelo Barabasi-Albert')
    plt.xlabel('Grau Médio')
    plt.ylabel('Desvio Padrão da Média')
    plt.grid(True)
    plt.legend()
    plt.savefig('BA_Model.png')
    plt.show()'''