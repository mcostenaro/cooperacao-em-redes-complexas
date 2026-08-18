import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (deve_registrar, diretorios, estatisticas, geradores,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   tempo, total_de_passos)

SAIDA_CSV, SAIDA_FIG = diretorios('comparacoes')

# Rotulos desta comparacao nas sementes derivadas. Um por modelo: os dois rodam
# no mesmo ponto da varredura e nao devem compartilhar a corrente aleatoria.
VARREDURA_BA = 'ba_vs_er/ba'
VARREDURA_ER = 'ba_vs_er/er'


#função para pegar um nó aleatório
def get_random_node(graph, gerador_random):
    return gerador_random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node, gerador_random):
    return gerador_random.choice(list(graph.neighbors(node)))


########################################################################################
#MODELO BARABASI-ALBERT

def dilema_BA(m, semente):

    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #numero de nós
    n = 1000

    #distribuição da quantidade de cooperadores iniciais, grau medio <k> = 2*m
    p = 0.5
    
    #tempo de evolucao, em varreduras
    t_list = [0.0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0


    #grafo aleatório
    G = nx.barabasi_albert_graph(n, m, seed=gerador_numpy, initial_graph=None)

    #atribuição de valores
    for i in G.nodes():
        G.nodes[i]['value'] = 1*(gerador_numpy.random() < 1-p)
        
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

     #passo
        if deve_registrar(i):
            t_list.append(tempo(i, n))
            coop.append(num_coop)


    #fracao de cooperadores
    frac_coop = [x/n for x in coop]

    #media e desvio, ja descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    return media_frac_coop, desvio_padrao_da_media

##############################################################
#MODELO Erdös-Renyi

def dilema_ER(k, semente):

    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #parametros do grafo, grau medio <k> = p*N
    n = 1000
    p = k/n

    #distribuição da quantidade de cooperadores iniciais
    p_i = 0.5
    
    #tempo de evolucao, em varreduras
    t_list = [0.0]
    #lista de cooperacao
    coop = []
    #numero de agentes cooperando
    num_coop = 0


    #grafo aleatório
    G = nx.erdos_renyi_graph(n, p, seed=gerador_numpy)

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

        #escolhendo nó
        random_node = get_random_node(G, gerador_random)

        if G.degree[random_node] >= 1:
            #escolhendo vizinho
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

        #passo
        if deve_registrar(i):
            t_list.append(tempo(i, n))
            coop.append(num_coop)


    #fracao de cooperadores
    frac_coop = [x/n for x in coop]

    #media e desvio, ja descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    return media_frac_coop, desvio_padrao_da_media

def loop(semente):

    medias_BA = []
    desvios_BA = []
    graus_medios_BA = []

    medias_ER = []
    desvios_ER = []
    graus_medios_ER = []

    for k in range(2, 21, 2):
        start_loop_time = time.time()

        media_ER, desvio_ER = dilema_ER(k, semente_de_ponto(semente, VARREDURA_ER, k))
        media_BA, desvio_BA = dilema_BA(round(k/2), semente_de_ponto(semente, VARREDURA_BA, k))
        medias_BA.append(media_BA)
        desvios_BA.append(desvio_BA)
        graus_medios_BA.append(k)
        medias_ER.append(media_ER)
        desvios_ER.append(desvio_ER)
        graus_medios_ER.append(k)
    
        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"loop {round(k/2)} concluido em {loop_duration} segundos")


    salvar_csv(
        SAIDA_CSV / 'ba_vs_er.csv',
        ['Grau_Medio', 'BA_Media_Frac_Coop', 'BA_Desvio_Padrao_da_Media',
         'ER_Media_Frac_Coop', 'ER_Desvio_Padrao_da_Media'],
        zip(graus_medios_BA, medias_BA, desvios_BA, medias_ER, desvios_ER),
        semente=semente,
    )

    plt.figure(figsize=(10, 6))
    plt.errorbar(graus_medios_BA, medias_BA, yerr=desvios_BA, label='BA_Model', capsize=5, fmt='o', markersize=2)
    plt.errorbar(graus_medios_ER, medias_ER, yerr=desvios_ER, label='ER_Model', capsize=5, fmt='o', markersize=2)
    plt.title('Comparação entre os gráficos')
    plt.xlabel('Grau Médio')
    plt.ylabel('Média da fração de cooperadores')
    plt.ylim(0, 1)
    plt.grid(True)
    plt.legend()
    salvar_figura(plt, SAIDA_FIG / 'comparacao_modelos.png')

"""""
#função que recebe uma função com quantidade de argumentos varia
def graph_image(funcao, *args, **kwargs):
    def get_t_list():
        funcao(*args, **kwargs)
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
"""
if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")