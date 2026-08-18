import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (deve_registrar, diretorios, estatisticas, geradores,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   tempo, total_de_passos)

SAIDA_CSV, SAIDA_FIG = diretorios('watts_strogatz')
# Subpasta propria: ws_varia_p.py gera as mesmas combinacoes (k, p) e antes
# as duas varreduras gravavam no mesmo nome de arquivo.
SAIDA_FIG = SAIDA_FIG / 'varia_k'

# Rotulo desta varredura nas sementes derivadas. Distinto do de ws_varia_p.py:
# as duas passam pelas mesmas combinacoes (k, p) e nao devem repetir a mesma
# realizacao.
VARREDURA = 'ws_varia_k'


#função para pegar um nó aleatório
def get_random_node(graph, gerador_random):
    return gerador_random.choice(list(graph.nodes()))

#função para pegar um vizinho aleatório do nó escolhido
def get_random_neighbor(graph, node, gerador_random):
    return gerador_random.choice(list(graph.neighbors(node)))

#função de atribuição


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

    #media e desvio, ja descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)


    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(t_list, frac_coop, color='blue')
    plt.title('Evolução Temporal - Watts-Strogatz')
    plt.xlabel('Tempo (varreduras)')
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


    salvar_figura(plt, SAIDA_FIG / f'Watts_strogatz_k_{k}_p_{round(p, 2)}.png')

    return media_frac_coop, desvio_padrao_da_media


def loop(p, semente):
    medias = []
    desvios = []
    grau_medios = []

    i = 0

#p = 0.0, 0.02, 1
#k = 2, 4, 6, 8, 10, 12, 14, 16, 18 e 20

    for k in range(2, 21, 2):
        start_loop_time = time.time()
        i = i+1

        media, desvio = dilema_prisioneiro(k, p, semente_de_ponto(semente, VARREDURA, p, k))
        medias.append(media)
        desvios.append(desvio)
        grau_medios.append(k)
        #print(medias, desvios, ps)

        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"loop {i} concluido em {loop_duration} segundos")
    
    salvar_csv(
        SAIDA_CSV / f'WA_p_{p}.csv',
        ['k', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'],
        ([round(grau_medios[i], 2), medias[i], desvios[i]] for i in range(len(grau_medios))),
        semente=semente,
    )


def loop_p(semente):
    start_p_time = time.time()
    for p in [0, 0.02, 0.2, 0.6, 1]:
        loop(p, semente)
    end_p_time = time.time()

    print(f"Tempo de execução: {round(end_p_time - start_p_time, 2)} segundos")


if __name__ == "__main__":
    start_time = time.time()

    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop_p(SEMENTE)

    end_time = time.time()

    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")


    