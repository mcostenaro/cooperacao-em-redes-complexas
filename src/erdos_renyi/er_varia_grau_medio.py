import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (diretorios, estatisticas, evoluir, geradores, salvar_csv,
                   salvar_figura, semente_base, semente_de_ponto)

SAIDA_CSV, SAIDA_FIG = diretorios('erdos_renyi')

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'er_varia_grau_medio'



#função de atribuição



#função principal
def dilema_prisioneiro(k, semente):

    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #parametros do grafo, grau medio <k> = p*N
    n = 1000
    p = k/n

    #distribuição da quantidade de cooperadores iniciais
    p_i = 0.5
    
    #grafo aleatorio
    G = nx.erdos_renyi_graph(n, p, seed=gerador_numpy)

    #dinamica compartilhada: o laco vive em comum.evoluir
    t_list, frac_coop = evoluir(G, p_i, gerador_numpy, gerador_random, n)

    #media e desvio, ja descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)


    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(t_list, frac_coop, color='blue')
    plt.title('Evolução Temporal - Erdos-renyi')
    plt.xlabel('Tempo (varreduras)')
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


    salvar_figura(plt, SAIDA_FIG / f'er_p_{p}.png')

    return media_frac_coop, desvio_padrao_da_media

def loop(semente):

    medias = []
    desvios = []
    graus_medios = []

    for k in range(2, 21, 2):
        start_loop_time = time.time()

        media, desvio = dilema_prisioneiro(k, semente_de_ponto(semente, VARREDURA, k))
        medias.append(media)
        desvios.append(desvio)
        graus_medios.append(k)
        #print(medias, desvios, graus_medios)

        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"loop {round(k/2)} concluido em {loop_duration} segundos")
    
    salvar_csv(
        SAIDA_CSV / 'er_grau_medio.csv',
        ['Grau_Medio', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'],
        zip(graus_medios, medias, desvios),
        semente=semente,
    )


if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop(SEMENTE)
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

    