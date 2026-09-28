import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (diretorios, estatisticas, evoluir, geradores, salvar_csv,
                   salvar_figura, semente_base, semente_de_ponto)

SAIDA_CSV, SAIDA_FIG = diretorios('watts_strogatz')
# Subpasta propria: ws_varia_p.py gera as mesmas combinacoes (k, p) e as
# figuras teriam o mesmo nome.
SAIDA_FIG = SAIDA_FIG / 'varia_k'

# Rotulo desta varredura nas sementes derivadas. Distinto do de ws_varia_p.py:
# as duas passam pelas mesmas combinacoes (k, p) e nao devem repetir a mesma
# realizacao.
VARREDURA = 'ws_varia_k'



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
    
    #grafo aleatorio
    G = nx.watts_strogatz_graph(n, k, p, seed=gerador_numpy)

    #dinamica compartilhada: o laco vive em comum.evoluir
    t_list, frac_coop = evoluir(G, p_i, gerador_numpy, gerador_random, n)

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


    salvar_figura(plt, SAIDA_FIG / f'ws_k_{k}_p_{round(p, 2)}.png')

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
        SAIDA_CSV / f'ws_varia_k_p_{p}.csv',
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


    