"""Monta as figuras de comparacao a partir dos CSVs ja gerados.

Nao roda simulacao: le resultados/<modelo>/csv/ e grava PNGs em
resultados/comparacoes/figuras/.
"""

import matplotlib.pyplot as plt
import time
import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from comum import RESULTADOS, diretorios, ler_csv, ler_serie, salvar_figura

_, SAIDA_FIG = diretorios('comparacoes')


def csv_de(modelo, nome):
    """Caminho de um CSV: csv_de('watts_strogatz', 'ws_varia_p_k_2.csv')."""
    return RESULTADOS / modelo / 'csv' / nome


# grafico equilibrio inicial
def comparar_graficos_p0(arquivo1, arquivo2, label1=r'$p_0 = 0.1$', label2=r'$p_0 = 0.9$'):
    '''
    Compara duas series temporais da fracao de cooperadores no mesmo grafico.

    Os arquivos sao CSVs de serie (duas colunas: tempo, fracao). Sao as series
    de BA para o mesmo m e dois p0 diferentes - o experimento de condicao
    inicial.
    '''
    t_list1, frac_coop1 = ler_serie(arquivo1)
    t_list2, frac_coop2 = ler_serie(arquivo2)

    # Verificar se os tamanhos das listas são iguais
    min_length = min(len(t_list1), len(t_list2))
    if len(t_list1) != len(t_list2):
        print("Aviso: Os dois arquivos têm números diferentes de registros. Usando o mínimo comum para plotagem.")
        t_list1 = t_list1[:min_length]
        frac_coop1 = frac_coop1[:min_length]
        t_list2 = t_list2[:min_length]
        frac_coop2 = frac_coop2[:min_length]

    plt.figure(figsize=(12, 8))
    plt.plot(t_list1, frac_coop1, label=label1, linewidth=2, linestyle='-', color='blue')
    plt.plot(t_list2, frac_coop2, label=label2, linewidth=2, linestyle='-', color='red')

    plt.title('Evolução temporal - Barabási-Albert', fontsize=25)
    plt.xlabel('Tempo (varreduras)', fontsize=22)
    plt.ylabel('Fração de Cooperadores', fontsize=22)
    plt.ylim(0, 1)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=16, loc='best')
    plt.tick_params(axis='both', which='major', labelsize=20)

    salvar_figura(plt, SAIDA_FIG / 'comparacao_fracao_de_cooperadores.png', dpi=300)


# grafico de apenas um modelo
def grafico(arquivo, nome_saida, titulo='Média da fração de cooperadores x grau médio'):
    grau_medio, media_frac_coop, desvios = ler_csv(arquivo)

    plt.figure(figsize=(8, 5))
    plt.xticks(grau_medio)
    plt.errorbar(grau_medio, media_frac_coop, yerr=desvios, capsize=7, fmt='o', markersize=5)
    plt.xlabel('Grau Médio', fontsize=15)
    plt.ylabel('Média da fração de cooperadores', fontsize=15)
    plt.xlim(0, None)
    plt.ylim(0, 1)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.grid(True)
    plt.title(titulo, fontsize=12)

    salvar_figura(plt, SAIDA_FIG / nome_saida)


def comparar_graficos_WS(arquivo1, arquivo2, arquivo3):
    '''Tres valores de k, fracao de cooperadores em funcao da religacao p.'''
    k1, media1, desvios1 = ler_csv(arquivo1)
    k2, media2, desvios2 = ler_csv(arquivo2)
    k3, media3, desvios3 = ler_csv(arquivo3)

    plt.figure(figsize=(8, 5))
    plt.xticks(k1)
    plt.errorbar(k1, media1, yerr=desvios1, label=r'$k = 2$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k2, media2, yerr=desvios2, label=r'$k = 6$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k3, media3, yerr=desvios3, label=r'$k = 10$', capsize=5, fmt='o', markersize=5)
    plt.xlabel(r'probabilidade de religação ($p_r$)', fontsize=15)
    plt.ylabel('Média da fração de cooperadores', fontsize=15)
    plt.ylim(0, 1.1)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.legend()
    plt.grid(True)
    plt.title('Fração de cooperadores x probabilidade de religação', fontsize=12)

    salvar_figura(plt, SAIDA_FIG / 'comparacao_WS_k.png')


def comparar_todos_graficos(arquivo1, arquivo2, arquivo3, arquivo4, arquivo5, arquivo6):
    # arquivo1 e o CSV de ba_vs_er.py, cujas tres primeiras colunas sao
    # Grau_Medio, BA_Media_Frac_Coop, BA_Desvio - exatamente o que ler_csv
    # devolve. E de la que vem a curva de BA porque aquele experimento roda com
    # p0 = 0,5, igual a ER, WS e SBM. A varredura de ba_varia_grau_medio usa
    # p0 = 0,1 e 0,9, entao poria uma condicao inicial diferente no mesmo
    # grafico.
    BA_grau_medio, BA_media, BA_desvios = ler_csv(arquivo1)
    ER_grau_medio, ER_media, ER_desvios = ler_csv(arquivo2)

    k1, media1, desvios1 = ler_csv(arquivo3)
    k2, media2, desvios2 = ler_csv(arquivo4)
    k3, media3, desvios3 = ler_csv(arquivo5)

    k_sbm, media_sbm, desvio_sbm = ler_csv(arquivo6)

    plt.figure(figsize=(9, 6))
    plt.xticks(k1)
    plt.errorbar(BA_grau_medio, BA_media, yerr=BA_desvios, label='BA', capsize=5, fmt='o', markersize=5)
    plt.errorbar(ER_grau_medio, ER_media, yerr=ER_desvios, label='ER', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k1, media1, yerr=desvios1, label=r'$WS_{p_r = 0}$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k2, media2, yerr=desvios2, label=r'$WS_{p_r = 0.02}$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k3, media3, yerr=desvios3, label=r'$WS_{p_r = 1}$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k_sbm, media_sbm, yerr=desvio_sbm, label=r'$SBM_{\alpha = 0.5}$', capsize=5, fmt='o', markersize=5)
    plt.xlabel('Grau médio', fontsize=15)
    plt.ylabel('Média da fração de cooperadores', fontsize=15)
    plt.ylim(0, 1.1)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.grid(True)
    plt.legend()
    plt.title('Comparação entre todos os modelos', fontsize=15)

    salvar_figura(plt, SAIDA_FIG / 'comparacao_todos_modelos.png')


def comparar_ws_transiente(aq1, aq2, aq3, aq4, nome_saida='comparacao_WS_transiente.png'):
    '''Quatro series de transiente do WS, uma por valor de religacao p.'''
    tempo1, media1 = ler_serie(aq1)
    tempo2, media2 = ler_serie(aq2)
    tempo3, media3 = ler_serie(aq3)
    tempo4, media4 = ler_serie(aq4)

    plt.figure(figsize=(9, 6))
    plt.plot(tempo1, media1, label='p = 0', markersize=2)
    plt.plot(tempo2, media2, label='p = 0.02', markersize=2)
    plt.plot(tempo3, media3, label='p = 0,2', markersize=2)
    plt.plot(tempo4, media4, label='p = 1', markersize=2)

    plt.xlabel('Tempo (varreduras)', fontsize=15)
    plt.ylabel('Média da fração de cooperadores', fontsize=15)
    plt.grid(True)
    plt.ylim(0.5, 1.1)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.legend(loc='upper right')
    plt.title('Dinâmica do tempo transiente', fontsize=15)

    salvar_figura(plt, SAIDA_FIG / nome_saida)


def plot_from_csv(file_paths, labels=None, nome_saida='sbm_alpha.png'):
    """Sobrepoe varios CSVs de tres colunas num unico grafico de alpha."""
    plt.figure(figsize=(7, 5))

    if labels is None:
        labels = [Path(p).stem for p in file_paths]

    for file_path, label in zip(file_paths, labels):
        parametro1, parametro2, desvio_padrao = ler_csv(file_path)
        plt.errorbar(parametro1, parametro2, yerr=desvio_padrao, fmt='o', capsize=5, label=label, markersize=5)

    plt.xlabel(r'Alpha', fontsize=12)
    plt.ylabel(r'Média da fração de cooperadores', fontsize=12)
    plt.title(r'Média da fração de cooperadores x alpha', fontsize=15)
    plt.xlim(0, None)
    plt.ylim(0, 1)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.grid(True)
    plt.legend()

    salvar_figura(plt, SAIDA_FIG / nome_saida)


def gerar_tudo():
    """Gera todas as figuras cujos CSVs de entrada existirem."""
    ws = lambda nome: csv_de('watts_strogatz', nome)
    ba = lambda nome: csv_de('barabasi_albert', nome)
    er = lambda nome: csv_de('erdos_renyi', nome)
    sbm = lambda nome: csv_de('sbm', nome)
    comp = lambda nome: csv_de('comparacoes', nome)

    tarefas = [
        ('WS: k fixo, varia p', comparar_graficos_WS,
         [ws('ws_varia_p_k_2.csv'), ws('ws_varia_p_k_6.csv'), ws('ws_varia_p_k_10.csv')]),
        ('todos os modelos', comparar_todos_graficos,
         [comp('ba_vs_er.csv'), er('er_grau_medio.csv'),
          ws('ws_varia_k_p_0.csv'), ws('ws_varia_k_p_0.02.csv'), ws('ws_varia_k_p_1.csv'),
          sbm('sbm_grau_medio_alpha_0.5.csv')]),
        ('transiente WS k=10', comparar_ws_transiente,
         [ws('ws_transiente_k_10_p_0.csv'), ws('ws_transiente_k_10_p_0.02.csv'),
          ws('ws_transiente_k_10_p_0.2.csv'), ws('ws_transiente_k_10_p_1.csv')]),
        ('BA: p0 = 0.1 vs 0.9', comparar_graficos_p0,
         [ba('ba_serie_m_10_p0_0.1.csv'), ba('ba_serie_m_10_p0_0.9.csv')]),
        ('ER: varia grau medio', grafico,
         [er('er_grau_medio.csv'), 'erdos_renyi_grau_medio.png']),
    ]

    for nome, funcao, args in tarefas:
        faltando = [a for a in args if isinstance(a, Path) and not a.exists()]
        if faltando:
            print(f"[pulado] {nome}: CSV ausente -> {faltando[0].name}")
            continue
        try:
            funcao(*args)
        except Exception as erro:
            print(f"[falhou] {nome}: {type(erro).__name__}: {erro}")

    # SBM: uma curva por grau medio, so os arquivos que existirem.
    lista = [sbm(f'sbm_alpha_k_{k}_25sim.csv') for k in (2, 4, 6, 8, 10)]
    rotulos = [rf'$\langle k \rangle = {k}$' for k in (2, 4, 6, 8, 10)]
    presentes = [(c, r) for c, r in zip(lista, rotulos) if c.exists()]
    if presentes:
        plot_from_csv([c for c, _ in presentes], [r for _, r in presentes],
                      nome_saida='sbm_alpha_por_grau_medio.png')
    else:
        print("[pulado] SBM alpha: nenhum sbm_alpha_k_*_25sim.csv encontrado")


if __name__ == "__main__":
    start_time = time.time()
    gerar_tudo()
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")
