import csv
import matplotlib.pyplot as plt
import time
import numpy as np
from pathlib import Path

# Diretorios resolvidos a partir da raiz do repositorio.
RAIZ = Path(__file__).resolve().parents[2]
RESULTADOS = RAIZ / 'resultados'
SAIDA_FIG = RESULTADOS / 'comparacoes' / 'figuras'
SAIDA_FIG.mkdir(parents=True, exist_ok=True)


def csv_de(modelo, nome):
    """Caminho de um CSV de resultado: csv_de('watts_strogatz', 'WA_k_2.csv')."""
    return RESULTADOS / modelo / 'csv' / nome

# Função para ler os dados do arquivo CSV
def read_csv(file_path):
    parametro1 = []
    parametro2 = []
    Desvio_padrao_media = []
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header
        for row in csvreader:
            parametro1.append(float(row[0])) 
            parametro2.append(float(row[1])) #modificar para int ou float dependendo do modelo
            Desvio_padrao_media.append(float(row[2]))

    return parametro1, parametro2, Desvio_padrao_media

#grafico equilibrio inciial
def comparar_graficos_p0(arquivo1, arquivo2, label1=r'$p_0 = 0.1$', label2=r'$p_0 = 0.9$'):
    '''
    Compara dois conjuntos de dados de fração de cooperadores e plota no mesmo gráfico.

    Parâmetros:
    - arquivo1: Caminho para o primeiro arquivo CSV.
    - arquivo2: Caminho para o segundo arquivo CSV.
    - label1: Rótulo para o primeiro conjunto de dados.
    - label2: Rótulo para o segundo conjunto de dados.
    '''
    # Lendo os dados dos arquivos CSV usando a função read_csv existente
    t_list1, frac_coop1 = read_csv(arquivo1)
    t_list2, frac_coop2 = read_csv(arquivo2)

    # Verificar se os tamanhos das listas são iguais (opcional)
    min_length = min(len(t_list1), len(t_list2))
    if len(t_list1) != len(t_list2):
        print("Aviso: Os dois arquivos têm números diferentes de registros. Usando o mínimo comum para plotagem.")
        t_list1 = t_list1[:min_length]
        frac_coop1 = frac_coop1[:min_length]
        t_list2 = t_list2[:min_length]
        frac_coop2 = frac_coop2[:min_length]

    # Criar o gráfico
    plt.figure(figsize=(12, 8))
    plt.plot(t_list1, frac_coop1, label=label1, linewidth=2, linestyle='-', color='blue')
    plt.plot(t_list2, frac_coop2, label=label2, linewidth=2, linestyle='-', color='red')

    plt.title('Evolução temporal - Barabási-Albert', fontsize=25)
    plt.xlabel('Tempo', fontsize=22)
    plt.ylabel('Fração de Cooperadores', fontsize=22)
    plt.ylim(0, 1)  # Limite do eixo Y entre 0 e 1
    plt.xlim(0, 200)  # Limite do eixo Y entre 0 e 1
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=16, loc='best')

    # Ajustar o tamanho dos números dos ticks dos eixos
    plt.tick_params(axis='both', which='major', labelsize=20)

    # Salvar o gráfico
    plt.savefig(SAIDA_FIG / 'comparacao_fracao_de_cooperadores.png', dpi=300)
    plt.close()
    print("Gráfico salvo como 'comparacao_fracao_de_cooperadores.png'.")


#Gráfico de dois modelos
'''def comparar_graficos(arquivo1, arquivo2):
    
    a entrade deve ser uma string
    
    # Lendo os dados dos arquivos CSV
    t_listBA, BA_frac_coop = read_csv(arquivo1)
    t_listER, ER_frac_coop = read_csv(arquivo2)

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
    plt.savefig(f'comp_frac_inicial.png')
    plt.close()'''

#gráfico de apenas um modelo
def grafico(arquivo):
    '''
    a entrade deve ser uma string
    '''
    # Lendo os dados dos arquivos CSV
    grau_medio, Media_frac_coop, desvios = read_csv(arquivo)
    
    # Plotando os dados
    plt.xticks(grau_medio)
    plt.errorbar(grau_medio, Media_frac_coop, yerr=desvios, capsize=7, fmt='o', markersize=5)
    plt.xlabel('Grau Médio', fontsize = 15)
    plt.ylabel('Média da fração de colaboradores', fontsize = 15)
    plt.xlim(0, None)  # Definindo o limite do eixo X começando em 0
    plt.ylim(0, 1)  # Definindo o limite do eixo Y entre 0 e 1    
    # Ajustar o tamanho dos números dos ticks dos eixos
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.grid(True)
    plt.title('Média da fração de cooperadores x grau médio', fontsize=12)
    plt.show()

def comparar_graficos_WS(arquivo1, arquivo2, arquivo3):
    '''
    a entrade deve ser uma string
    '''
    # Lendo os dados dos arquivos CSV
    k1, Media_frac_coop1, desvios1 = read_csv(arquivo1)
    k2, Media_frac_coop2, desvios2 = read_csv(arquivo2)
    k3, Media_frac_coop3, desvios3 = read_csv(arquivo3)


    
    # Plotando os dados
    plt.xticks(k1)
    plt.errorbar(k1, Media_frac_coop1, yerr=desvios1, label=r'$k = 2$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k2, Media_frac_coop2, yerr=desvios2, label=r'$k = 6$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k3, Media_frac_coop3, yerr=desvios3, label=r'$k = 10$', capsize=5, fmt='o', markersize=5)
    plt.xlabel(r'probabilidade de realocação ($p_r$)', fontsize=15)
    plt.ylabel('Média da fração de colaboradores', fontsize=15)
    plt.ylim(0, 1.1)  # Definindo o limite do eixo Y entre 0 e 1  
    plt.tick_params(axis='both', which='major', labelsize=15) 
    plt.legend()
    plt.grid(True)
    plt.title('Médias da fração de colaboradores x probabilidade de realocação', fontsize=12)
    plt.show()

def comparar_todos_graficos(arquivo1, arquivo2, arquivo3, arquivo4, arquivo5, arquivo6):
    # Lendo os dados dos arquivos CSV
    BA_grau_medio, BA_Media_frac_coop, BA_desvios = read_csv(arquivo1)
    ER_grau_medio, ER_Media_frac_coop, ER_desvios = read_csv(arquivo2)

    k1, Media_frac_coop1, desvios1 = read_csv(arquivo3)
    k2, Media_frac_coop2, desvios2 = read_csv(arquivo4)
    k3, Media_frac_coop3, desvios3 = read_csv(arquivo5)

    k_sbm, media_sbm, desvio_sbm = read_csv(arquivo6)

    # Plotando os dados
    plt.xticks(k1)
    plt.errorbar(BA_grau_medio, BA_Media_frac_coop, yerr=BA_desvios, label='BA', capsize=5, fmt='o', markersize=5)
    plt.errorbar(ER_grau_medio, ER_Media_frac_coop, yerr=ER_desvios, label='ER', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k1, Media_frac_coop1, yerr=desvios1, label=r'$WS_{p_r = 0}$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k2, Media_frac_coop2, yerr=desvios2, label=r'$WS_{p_r = 0.02}$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k3, Media_frac_coop3, yerr=desvios3, label=r'$WS_{p_r = 1}$', capsize=5, fmt='o', markersize=5)
    plt.errorbar(k_sbm, media_sbm, yerr=desvio_sbm, label=r'$SBM_{\alpha = 0.5}$', capsize=5, fmt='o', markersize=5)
    plt.xlabel('Grau médio', fontsize=15)
    plt.ylabel('Média da fração de colaboradores', fontsize=15)
    plt.ylim(0, 1.1)  # Definindo o limite do eixo Y entre 0 e 1  
    plt.tick_params(axis='both', which='major', labelsize=15) 
    plt.grid(True)
    plt.legend()
    plt.title('Comparação entre todos os modelos', fontsize=15)
    plt.show()

def comparar_WA_transiente(aq1, aq2, aq3, aq4):
    tempo1, media1 = read_csv(aq1)
    tempo2, media2 = read_csv(aq2)
    tempo3, media3 = read_csv(aq3)
    tempo4, media4 = read_csv(aq4)


    # Plotando os dados
    #plt.xticks(np.arange(0, max(tempo1) + 2, 4)) 
    plt.plot(tempo1, media1, label='p = 0', markersize=2)
    plt.plot(tempo2, media2, label='p = 0.02', markersize=2)
    plt.plot(tempo3, media3, label='p = 0,2', markersize=2)
    plt.plot(tempo4, media4, label='p = 1', markersize=2)

    plt.xlabel('Tempo', fontsize=15)
    plt.ylabel('Média da fração de colaboradores', fontsize=15)
    plt.grid(True)
    plt.xlim(0, 1000)   
    plt.ylim(0.5, 1.1)  # Definindo o limite do eixo Y entre 0 e 1  
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.legend(loc='upper right')
    plt.title('Dinâmica do tempo transiente', fontsize=15)
    plt.show()


def plot_from_csv(file_paths, labels=None, param1_type=float):
    """
    Lê um ou mais arquivos CSV e cria um gráfico usando os rótulos apropriados.
    
    :param file_paths: Lista de caminhos dos arquivos CSV.
    :param labels: Lista de rótulos personalizados para a legenda.
    :param param1_type: Tipo a ser usado para o primeiro parâmetro (float ou int).
    """
    plt.figure(figsize=(7, 5))
    
    # Se não forem fornecidos rótulos personalizados, usa os nomes dos arquivos como rótulos
    if labels is None:
        labels = file_paths
    
    # Iterar sobre cada caminho de arquivo fornecido e rótulo correspondente
    for file_path, label in zip(file_paths, labels):
        # Chamar a função read_csv e obter os dados para cada arquivo
        parametro1, parametro2, desvio_padrao = read_csv(file_path)
        
        # Plotar os dados de cada arquivo
        plt.errorbar(parametro1, parametro2, yerr=desvio_padrao, fmt='o', capsize=5, label=label, markersize=5)
    
    # Definir rótulos e título diretamente no código
    plt.xlabel(r'Alpha', fontsize=12)
    plt.ylabel(r'Média da fração de cooperadores', fontsize=12)
    plt.title(r'Média da fração de cooperadores x alpha', fontsize=15)
    plt.xlim(0, None)  # Definindo o limite do eixo X começando em 0
    plt.ylim(0, 1)  # Definindo o limite do eixo Y entre 0 e 1
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.grid(True)
    plt.legend()  # Adicionar legenda personalizada
    plt.show()


if __name__ == "__main__":
    start_time = time.time()

    ws = lambda nome: csv_de('watts_strogatz', nome)
    ba = lambda nome: csv_de('barabasi_albert', nome)
    er = lambda nome: csv_de('erdos_renyi', nome)
    sbm = lambda nome: csv_de('sbm', nome)

    #comparar_WA_transiente(ws("WA_transiente_k_10_p_0.csv"), ws("WA_transiente_k_10_p_0.02.csv"), ws("WA_transiente_k_10_p_0.2.csv"), ws("WA_transiente_k_10_p_1.csv"))
    #comparar_todos_graficos(ba('Dilema_Barabasi_results.csv'), er('Dilema_erdos_results.csv'), ws('WA_p_0.csv'), ws('WA_p_02.csv'), ws('WA_p_1.csv'), sbm('Dilema_SBM_results_alpha_05.csv'))
    comparar_graficos_WS(ws('WA_k_2.csv'), ws('WA_k_6.csv'), ws('WA_k_10.csv')) #ao usar mudar o row entre float e int
    #comparar_graficos_p0(ba('fracao_de_cooperadores01.csv'), ba('fracao_de_cooperadores09.csv'), label1=r'$p_0 = 0.1$', label2=r'$p_0 = 0.9$')
    #grafico(er('Dilema_erdos_results.csv'))
    #labels = [r'$\langle k \rangle = 2$', r'$\langle k \rangle = 4$', r'$\langle k \rangle = 6$', r'$\langle k \rangle = 8$', r'$\langle k \rangle = 10$']
    #lista = [sbm(f'SBM_50s_{k}.csv') for k in (2, 4, 6, 8, 10)]
    #plot_from_csv(lista, labels, float)
    end_time = time.time()
    print(f"Tempo de execução: {round(end_time - start_time, 2)} segundos")


    #LEMBRAR DE ATUALIZAR CADA UMA DAS FUNÇÕES ADICIONANDO O COMANDO plt.plot(..., color = 'cor'), a funcao comparar_graficos ja ta feito
