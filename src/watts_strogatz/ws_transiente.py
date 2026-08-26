import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import multiprocessing as mp

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (PASSOS_POR_REGISTRO, diretorios, evoluir, geradores,
                   processos,
                   salvar_csv, salvar_figura, semente_base, semente_de_ponto,
                   sementes_de_realizacoes, tempo)

SAIDA_CSV, SAIDA_FIG = diretorios('watts_strogatz')
SAIDA_FIG = SAIDA_FIG / 'transiente'

# Registros mantidos da serie: 2000 registros = 200 varreduras.
REGISTROS_TRANSIENTE_PLOT = 2000

# Realizacoes promediadas em cada curva.
REALIZACOES = 30

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'ws_transiente'




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

    return t_list[:REGISTROS_TRANSIENTE_PLOT], frac_coop[:REGISTROS_TRANSIENTE_PLOT]

#funcao para fazer varias simulações do tempo transiente do modelo WA
def multiplas_simulacoes(k, p, semente):
    # Uma semente por realizacao, derivada do ponto (k, p) e passada como
    # argumento da tarefa. No Windows o start method e spawn: o filho reimporta
    # o modulo e nao herda gerador nenhum do pai.
    sementes = sementes_de_realizacoes(semente_de_ponto(semente, VARREDURA, k, p),
                                       REALIZACOES)
    with mp.Pool(processes=processos()) as pool:
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


    