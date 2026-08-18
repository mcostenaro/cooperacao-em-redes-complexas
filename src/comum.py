"""Parametros de amostragem e utilitarios comuns aos scripts de simulacao.

Todos os scripts usam estas constantes para que medias e barras de erro sejam
comparaveis entre modelos.

Antes desta padronizacao cada script tinha sua propria taxa de registro e seu
proprio corte de transiente: BA registrava a cada 100 passos e descartava 100
registros (9900 amostras), ER registrava a cada 1000 e descartava 100 (900
amostras), e WS/SBM registravam a cada 1000 e descartavam 1000 (100 amostras).
Como o desvio padrao da media e sigma/sqrt(N), as barras de erro publicadas
diferiam por um fator sqrt(9900/900) = 3,3 entre BA e ER sem que o sigma da
serie fosse diferente - era artefato da taxa de amostragem, nao fisica.

Convencao adotada:
    - 1 varredura = N passos de Monte Carlo (cada no sorteado uma vez em media)
    - 1000 varreduras simuladas = 10^6 passos com N = 1000
    - 1 registro a cada 100 passos = 0,1 varredura -> 10.000 registros
    - descarte de 1000 registros (100 varreduras, 10%) como transiente
    - restam 9.000 amostras estacionarias em todos os scripts

Cabecalhos de CSV nao usam acento nem cedilha, e todo arquivo e escrito em
UTF-8 explicito. Os CSVs antigos do SBM foram gravados sem encoding declarado
e acabaram com bytes U+FFFD no lugar de "cao" em "fracao".

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

Variaveis de ambiente reconhecidas (as tres ultimas existem para o teste de
reprodutibilidade rodar em segundos em vez de horas, sem tocar em
`resultados/`):

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


def total_de_passos(n=N_PADRAO):
    """Numero de passos de Monte Carlo de uma simulacao."""
    return VARREDURAS * n


def deve_registrar(i):
    """True quando o passo i deve virar um registro da serie temporal."""
    return i % PASSOS_POR_REGISTRO == 0 and i != 0


def tempo(i, n=N_PADRAO):
    """Instante do passo i em varreduras, a unidade de tempo do modelo."""
    return i / n


def estatisticas(frac_coop):
    """Media e desvio padrao da media da serie, descartado o transiente.

    O desvio e sigma/sqrt(N) sobre uma serie temporal correlacionada, entao
    subestima a incerteza real. Serve para comparar pontos medidos do mesmo
    jeito, nao como barra de erro estatistica rigorosa - para isso e preciso
    um ensemble de realizacoes independentes.
    """
    estacionario = frac_coop[REGISTROS_TRANSIENTE:]
    n_amostras = len(estacionario)
    media = float(np.mean(estacionario))
    desvio_da_media = float(np.std(estacionario) / np.sqrt(n_amostras))
    return media, desvio_da_media


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

    Os CSVs de transiente (fracao_de_cooperadores*.csv, WA_transiente_*.csv)
    tem duas colunas, nao tres. Usar ler_csv neles levanta IndexError.
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
