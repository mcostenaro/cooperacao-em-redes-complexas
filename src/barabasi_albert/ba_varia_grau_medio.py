import networkx as nx
import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import (diretorios, estatisticas, evoluir, geradores, salvar_csv,
                   salvar_figura, semente_base, semente_de_ponto,
                   semente_registro)

SAIDA_CSV, SAIDA_FIG = diretorios('barabasi_albert')

# Rotulo desta varredura nas sementes derivadas.
VARREDURA = 'ba_varia_grau_medio'

# Condicoes iniciais varridas. A figura comparacao_fracao_de_cooperadores.png
# contrapoe p0 = 0,1 a p0 = 0,9. Acrescentar um valor aqui basta para varrer
# mais um.
P0_INICIAIS = [0.1, 0.9]



#função principal
def dilema_prisioneiro(n, m, p, semente):

    #geradores explicitos: nada de random/np.random globais
    gerador_numpy, gerador_random = geradores(semente)

    #p = fracao de cooperadores iniciais; grau medio <k> = 2*m

    #grafo aleatorio
    G = nx.barabasi_albert_graph(n, m, seed=gerador_numpy, initial_graph=None)

    #dinamica compartilhada: o laco vive em comum.evoluir
    t_list, frac_coop = evoluir(G, p, gerador_numpy, gerador_random, n)

    #media e desvio, ja descartado o transiente padronizado
    media_frac_coop, desvio_padrao_da_media = estatisticas(frac_coop)

    #lista de cooperadores transientes: 200 registros = 20 varreduras
    coop_trans = frac_coop[:200]
    t_list_trans = t_list[:200]

    salvar_csv(
        SAIDA_CSV / f'ba_serie_m_{m}_p0_{p}.csv',
        ['Tempo_varreduras', 'Fracao_Cooperadores'],
        zip(t_list_trans, coop_trans),
        semente=semente_registro(semente),
    )

    # Criar o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(t_list_trans, coop_trans, color='blue')
    plt.title('Evolução temporal - Barabási-Albert', fontsize=26)  # Aumentar o título
    plt.xlabel('Tempo (varreduras)', fontsize=20)  # Aumentar o rótulo do eixo X
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
    salvar_figura(plt, SAIDA_FIG / f'ba_m_{m}_p0_{p}.png')

    return media_frac_coop, desvio_padrao_da_media

def loop(p, semente):

    medias = []
    desvios = []
    graus_medios = []

    for m in range(1, 11):
        start_loop_time = time.time()

        media, desvio = dilema_prisioneiro(
            1000, m, p, semente_de_ponto(semente, VARREDURA, p, m))
        medias.append(media)
        desvios.append(desvio)
        graus_medios.append(2*m)
    
        end_loop_time = time.time()  # Fim do loop
        loop_duration = round(end_loop_time - start_loop_time, 2)
        print(f"p0 = {p}, loop {round(m)} concluido em {loop_duration} segundos")

    salvar_csv(
        SAIDA_CSV / f'ba_grau_medio_p0_{p}.csv',
        ['Grau_Medio', 'Media_Frac_Coop', 'Desvio_Padrao_da_Media'],
        zip(graus_medios, medias, desvios),
        semente=semente,
    )


def loop_p0(semente):
    for p in P0_INICIAIS:
        loop(p, semente)


if __name__ == "__main__":
    start_time = time.time()
    SEMENTE = semente_base()
    print(f"semente-base = {SEMENTE}")
    loop_p0(SEMENTE)
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