"""Parametros de amostragem e utilitarios comuns aos scripts de simulacao.

Todos os scripts usam estas constantes para que medias e barras de erro sejam
comparaveis entre modelos.

Convencao:
    - 1 varredura = N passos de Monte Carlo (cada no sorteado uma vez em media)
    - 1000 varreduras simuladas = 10^6 passos com N = 1000
    - 1 registro a cada 100 passos = 0,1 varredura -> 10.000 registros
    - descarte de 1000 registros (100 varreduras, 10%) como transiente
    - restam 9.000 amostras estacionarias em todos os scripts

Cabecalhos de CSV nao usam acento nem cedilha, e todo arquivo e escrito em
UTF-8 explicito.

Reprodutibilidade
-----------------
Toda a aleatoriedade dos scripts sai de uma unica semente-base inteira, obtida
por `semente_base()`: `--semente N` na linha de comando, senao a variavel de
ambiente TCC_SEMENTE, senao SEMENTE_PADRAO. Nenhum script usa os modulos
`random` ou `np.random` globais - `geradores()` devolve um par de geradores
explicitos que sao passados como argumento.

Cada ponto da varredura pega sua semente com `semente_de_ponto(base, *rotulos)`,
que deriva de uma SeedSequence com spawn_key vinda dos rotulos, nao da ordem de
execucao: rodar a varredura inteira ou um ponto isolado da exatamente a mesma
sequencia de numeros. As realizacoes de um ensemble saem de
`sementes_de_realizacoes()`, que usa SeedSequence.spawn, e sao passadas como
argumento da tarefa do multiprocessing - no Windows o start method e spawn, o
processo filho reimporta o modulo e nao herda estado nenhum do pai.

Variaveis de ambiente reconhecidas (as tres ultimas servem para testes
rapidos, sem tocar em `resultados/`):

    TCC_SEMENTE               semente-base
    TCC_VARREDURAS            sobrescreve VARREDURAS
    TCC_REGISTROS_TRANSIENTE  sobrescreve REGISTROS_TRANSIENTE
    TCC_RESULTADOS            raiz das saidas, no lugar de <repo>/resultados
"""

import csv
import os
import random
import sys
import zlib
from pathlib import Path

import numpy as np

# Raiz do repositorio, a partir de src/comum.py.
RAIZ = Path(__file__).resolve().parents[1]


def _inteiro_do_ambiente(nome, padrao):
    """Le um inteiro de uma variavel de ambiente, com padrao se ausente/vazia."""
    valor = os.environ.get(nome)
    if not valor:
        return padrao
    return int(valor)


# Raiz das saidas. Redirecionavel para nao sobrescrever resultados publicados.
RESULTADOS = Path(os.environ.get('TCC_RESULTADOS') or (RAIZ / 'resultados'))

# Numero de nos usado em todos os modelos.
N_PADRAO = 1000

# Varreduras simuladas. Total de passos = VARREDURAS * n.
VARREDURAS = _inteiro_do_ambiente('TCC_VARREDURAS', 1000)

# Um registro a cada 100 passos = 0,1 varredura com n = 1000.
PASSOS_POR_REGISTRO = 100

# Registros descartados como transiente: 1000 registros = 100 varreduras = 10%.
REGISTROS_TRANSIENTE = _inteiro_do_ambiente('TCC_REGISTROS_TRANSIENTE', 1000)

# Semente-base usada quando nada e informado. Trocar este numero muda todos os
# resultados; e o unico ponto do codigo onde isso acontece.
SEMENTE_PADRAO = 20242025

# Marcadores de spawn_key das duas correntes de um mesmo ponto. Sao valores
# altos de proposito: SeedSequence.spawn numera os filhos de 0 em diante, entao
# nunca colidem com uma semente de realizacao.
_MARCA_NUMPY = 0xA1F00001
_MARCA_RANDOM = 0xA1F00002


def semente_base(argv=None):
    """Semente-base inteira desta execucao.

    Precedencia: `--semente N` (ou `--semente=N`) na linha de comando, depois a
    variavel de ambiente TCC_SEMENTE, depois SEMENTE_PADRAO.
    """
    argumentos = sys.argv[1:] if argv is None else list(argv)
    for i, argumento in enumerate(argumentos):
        if argumento == '--semente':
            if i + 1 >= len(argumentos):
                raise SystemExit('--semente exige um valor inteiro')
            return int(argumentos[i + 1])
        if argumento.startswith('--semente='):
            return int(argumento.split('=', 1)[1])
    return _inteiro_do_ambiente('TCC_SEMENTE', SEMENTE_PADRAO)


def _texto_da_chave(valor):
    """Normaliza um rotulo de ponto para texto estavel entre execucoes.

    Floats passam por formatacao fixa porque np.arange(0.1, 1, 0.1) produz
    0.30000000000000004: sem isso o mesmo alpha escrito como 0.3 no CSV daria
    outra semente.
    """
    if isinstance(valor, (float, np.floating)):
        return f'{float(valor):.6f}'
    return str(valor)


def semente_de_ponto(base, *rotulos):
    """SeedSequence de um ponto da varredura, identificado por seus rotulos.

    Os rotulos entram no spawn_key, entao a semente depende de *qual* ponto e,
    nao da ordem em que a varredura o alcancou. Chamar
    `semente_de_ponto(base, 'ws_varia_k', 0.02, 6)` da o mesmo resultado
    rodando a varredura inteira ou so aquele ponto.
    """
    rotulo = '|'.join(_texto_da_chave(r) for r in rotulos)
    chave = zlib.crc32(rotulo.encode('utf-8'))
    return np.random.SeedSequence(entropy=int(base), spawn_key=(chave,))


def sementes_de_realizacoes(semente, quantidade):
    """Lista de sementes filhas de um ponto, uma por realizacao do ensemble.

    Usa SeedSequence.spawn, que numera os filhos a partir de 0 - chame uma vez
    por ponto, sobre a SeedSequence recem-criada por `semente_de_ponto`, senao
    a numeracao anda e as sementes mudam.

    Cada elemento e passado como argumento da tarefa do multiprocessing (e
    picklavel). Herdar a semente do processo pai nao funcionaria: no Windows o
    start method e spawn e o filho reimporta o modulo do zero.
    """
    return semente.spawn(quantidade)


def semente_registro(semente):
    """Semente-base por tras de uma semente derivada, para registrar na saida.

    `semente_de_ponto` e `sementes_de_realizacoes` preservam a entropia da base
    e mudam apenas o spawn_key, entao qualquer semente derivada sabe dizer de
    qual semente-base ela veio.
    """
    if isinstance(semente, np.random.SeedSequence):
        return int(semente.entropy)
    return int(semente)


def geradores(semente):
    """(gerador numpy, gerador random) independentes, derivados de uma semente.

    Aceita SeedSequence ou int. As duas correntes saem de derivacoes distintas
    da mesma semente, entao consumir uma nao desloca a outra. Estes geradores
    substituem os modulos `random` e `np.random` globais e sao tambem o que se
    passa em `seed=` dos geradores de grafo do networkx.
    """
    if not isinstance(semente, np.random.SeedSequence):
        semente = np.random.SeedSequence(int(semente))

    def derivar(marca):
        return np.random.SeedSequence(entropy=semente.entropy,
                                      spawn_key=semente.spawn_key + (marca,))

    gerador_numpy = np.random.default_rng(derivar(_MARCA_NUMPY))
    estado = derivar(_MARCA_RANDOM).generate_state(8, dtype=np.uint32)
    gerador_random = random.Random(int.from_bytes(estado.tobytes(), 'little'))
    return gerador_numpy, gerador_random


def processos():
    """Numero de processos dos scripts que usam multiprocessing.

    Deixa dois nucleos livres para a maquina continuar usavel; TCC_PROCESSOS
    sobrescreve.

    Trocar este numero nao muda resultado nenhum: cada tarefa carrega sua
    propria semente e pool.map preserva a ordem dos retornos.
    """
    pedido = _inteiro_do_ambiente('TCC_PROCESSOS', 0)
    if pedido > 0:
        return pedido
    return max(1, (os.cpu_count() or 1) - 2)


def sortear_no(G, gerador_random, nos=None):
    """Um no do grafo, uniformemente."""
    return gerador_random.choice(nos if nos is not None else list(G.nodes()))


def sortear_vizinho(G, no, gerador_random, vizinhos=None):
    """Um vizinho de `no`, uniformemente."""
    if vizinhos is not None:
        return gerador_random.choice(vizinhos[no])
    return gerador_random.choice(list(G.neighbors(no)))


def listas_de_adjacencia(G):
    """(lista de nos, dict de listas de vizinhos), fixadas uma unica vez.

    O grafo nao muda durante a dinamica, entao as listas sao montadas uma vez,
    fora do laco. Sao as mesmas que list(G.nodes()) e list(G.neighbors(no))
    devolvem, na mesma ordem, entao `choice` consome o gerador do mesmo jeito.
    """
    nos = list(G.nodes())
    return nos, {no: list(G.neighbors(no)) for no in nos}


def atribuir_estados(G, p0, gerador_numpy):
    """Sorteia o estado inicial de cada no e devolve quantos cooperam.

    `p0` e a fracao esperada de cooperadores. value = 0 coopera, 1 delata.
    """
    num_coop = 0
    for no in G.nodes():
        G.nodes[no]['value'] = 1 * (gerador_numpy.random() < 1 - p0)
        if G.nodes[no]['value'] == 0:
            num_coop += 1
    return num_coop


def evoluir(G, p0, gerador_numpy, gerador_random, n=None):
    """Roda a dinamica sobre G e devolve (tempos, fracao de cooperadores).

    A regra e Win-Stay Lose-Shift: sorteia-se um no e um vizinho dele, e o par
    passa a valer `s_i XOR s_j` - C com D vira D com D, D com D vira C com C, C
    com C fica. Nos isolados fazem o passo passar em branco; em BA e WS isso
    nunca acontece, porque a construcao garante grau >= 1.

    Devolve a serie inteira, sem descartar transiente: quem quer o estacionario
    passa o resultado por `estatisticas`, quem estuda o transiente (como
    ws_transiente.py) usa o comeco dela.
    """
    if n is None:
        n = G.number_of_nodes()

    nos, vizinhos = listas_de_adjacencia(G)
    num_coop = atribuir_estados(G, p0, gerador_numpy)

    tempos = [0.0]
    coop = [num_coop]

    for i in range(total_de_passos(n)):
        no = gerador_random.choice(nos)

        if vizinhos[no]:
            vizinho = gerador_random.choice(vizinhos[no])

            valor_no = G.nodes[no]['value']
            valor_vizinho = G.nodes[vizinho]['value']

            if valor_no == 0:
                # C com D: o cooperador deserta. C com C: nada muda.
                if valor_vizinho == 1:
                    G.nodes[no]['value'] = 1
                    num_coop -= 1
            elif valor_vizinho == 0:
                # D com C: o cooperador deserta.
                G.nodes[vizinho]['value'] = 1
                num_coop -= 1
            else:
                # D com D: ambos passam a cooperar.
                G.nodes[no]['value'] = 0
                G.nodes[vizinho]['value'] = 0
                num_coop += 2

        if deve_registrar(i):
            tempos.append(tempo(i, n))
            coop.append(num_coop)

    return tempos, [x / n for x in coop]


def total_de_passos(n=N_PADRAO):
    """Numero de passos de Monte Carlo de uma simulacao."""
    return VARREDURAS * n


def deve_registrar(i):
    """True quando o passo i deve virar um registro da serie temporal."""
    return i % PASSOS_POR_REGISTRO == 0 and i != 0


def tempo(i, n=N_PADRAO):
    """Instante do passo i em varreduras, a unidade de tempo do modelo."""
    return i / n


def erro_por_blocagem(serie, minimo_de_blocos=16):
    """Erro do valor medio de uma serie correlacionada, por blocagem.

    sigma/sqrt(N) supoe amostras independentes. As desta serie nao sao: entre
    dois registros passam 100 passos, que tocam no maximo 200 dos 1000 nos - a
    medida seguinte e quase a mesma medida. Usar sqrt(N) com N = 9000 conta
    9000 amostras onde ha uma centena de independentes, e o erro sai pequeno
    demais. Medido em ER, o fator e de 3 a 5.

    A blocagem (Flyvbjerg & Petersen 1989) nao supoe independencia: agrupa a
    serie em blocos consecutivos e usa as medias dos blocos. Enquanto o bloco e
    menor que o tempo de correlacao, o erro estimado cresce; quando passa, ele
    estabiliza - esse patamar e o erro verdadeiro. Aqui subimos os niveis
    (blocos de 1, 2, 4, ... elementos) ate o crescimento deixar de ser
    significativo diante da propria incerteza da estimativa.

    Testado contra AR(1), cujo erro tem formula fechada: acerta dentro de ~6%
    para correlacao de 0 a 0,98 - inclusive o caso independente, onde devolve
    sigma/sqrt(N) e nao infla a barra a toa.
    """
    x = np.asarray(serie, dtype=float)
    if len(x) < 2:
        return 0.0

    niveis = []
    tamanho = 1
    while len(x) // tamanho >= minimo_de_blocos:
        blocos_inteiros = len(x) // tamanho
        blocos = x[:blocos_inteiros * tamanho].reshape(blocos_inteiros, tamanho)
        medias = blocos.mean(axis=1)
        niveis.append((float(medias.std(ddof=1) / np.sqrt(blocos_inteiros)),
                       blocos_inteiros))
        tamanho *= 2

    if not niveis:
        return float(np.std(x) / np.sqrt(len(x)))

    erro = niveis[0][0]
    for (atual, _), (anterior, blocos_anterior) in zip(niveis[1:], niveis):
        incerteza = anterior / np.sqrt(2 * (blocos_anterior - 1))
        erro = atual
        if atual - anterior < incerteza:
            break
    return erro


def estatisticas(frac_coop):
    """Media e erro do valor medio da serie, descartado o transiente.

    O erro vem de `erro_por_blocagem`, nao de sigma/sqrt(N), porque a serie e
    correlacionada. Nos experimentos com ensemble o erro nao passa por aqui: la
    ele e calculado sobre as realizacoes, que sao independentes.
    """
    estacionario = frac_coop[REGISTROS_TRANSIENTE:]
    media = float(np.mean(estacionario))
    return media, erro_por_blocagem(estacionario)


def diretorios(modelo):
    """Devolve (saida_csv, saida_fig) de um modelo, criando os diretorios."""
    saida_csv = RESULTADOS / modelo / 'csv'
    saida_fig = RESULTADOS / modelo / 'figuras'
    saida_csv.mkdir(parents=True, exist_ok=True)
    saida_fig.mkdir(parents=True, exist_ok=True)
    return saida_csv, saida_fig


def salvar_csv(caminho, cabecalho, linhas, semente=None):
    """Grava um CSV em UTF-8 com cabecalho sem acento nem cedilha.

    Com `semente` informada acrescenta a coluna Semente_Base, repetida em todas
    as linhas: o arquivo passa a rastrear a execucao que o gerou. Os leitores
    (`ler_csv`, `ler_serie`) indexam pelas primeiras colunas e ignoram a extra.
    """
    if semente is not None:
        cabecalho = [*cabecalho, 'Semente_Base']
        linhas = ([*linha, semente] for linha in linhas)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, 'w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(cabecalho)
        escritor.writerows(linhas)
    print(f"CSV salvo em {caminho}")


def ler_csv(caminho):
    """Le um CSV de resultado e devolve as tres colunas como listas de float."""
    coluna1 = []
    coluna2 = []
    desvios = []
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        next(leitor)  # cabecalho
        for linha in leitor:
            coluna1.append(float(linha[0]))
            coluna2.append(float(linha[1]))
            desvios.append(float(linha[2]))
    return coluna1, coluna2, desvios


def ler_serie(caminho):
    """Le um CSV de serie temporal de duas colunas: (tempo, valores).

    Os CSVs de serie (ba_serie_*.csv, ws_transiente_*.csv) tem duas colunas,
    nao tres. Usar ler_csv neles levanta IndexError.
    """
    tempos = []
    valores = []
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        next(leitor)  # cabecalho
        for linha in leitor:
            tempos.append(float(linha[0]))
            valores.append(float(linha[1]))
    return tempos, valores


def salvar_figura(plt, caminho, dpi=150):
    """Salva a figura corrente em disco e fecha, sem abrir janela."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(caminho, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"Figura salva em {caminho}")
