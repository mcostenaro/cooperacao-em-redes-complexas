# Dilema do Prisioneiro em Redes Complexas

Simulações de Monte Carlo de uma dinâmica de cooperação/deserção sobre quatro
modelos de rede — Barabási-Albert, Erdős-Rényi, Watts-Strogatz e Stochastic
Block Model — investigando como a topologia afeta a fração estacionária de
cooperadores.

Código do meu Trabalho de Conclusão de Curso (2024). Este repositório contém a
**versão apresentada**, reorganizada mas com a dinâmica original preservada.
As limitações do modelo estão documentadas em [Limitações conhecidas](#limitações-conhecidas).

O inventário dos experimentos — o que cada script varre, com que parâmetros, o
que grava e quanto custa — está em [PROTOCOLO.md](PROTOCOLO.md).

---

## Estrutura

```
src/
├── comum.py                        # parametros de amostragem e I/O compartilhados
├── barabasi_albert/
│   ├── ba_varia_grau_medio.py      # varre m = 1..10 (⟨k⟩ = 2m)
│   └── ba_prototipo_com_score.py   # protótipo com matriz de payoff (ver Limitações)
├── erdos_renyi/
│   └── er_varia_grau_medio.py      # varre ⟨k⟩ = 2..20
├── watts_strogatz/
│   ├── ws_varia_k.py               # p fixo, varre k
│   ├── ws_varia_p.py               # k fixo, varre p de religação
│   └── ws_transiente.py            # curva ρ(t), média de 30 realizações
├── sbm/
│   ├── sbm_varia_alpha_ensemble.py # varre α, 20 realizações
│   ├── sbm_varia_alpha_paralelo.py # idem, 25 realizações, multiprocessing
│   ├── sbm_varia_k.py              # α fixo, varre ⟨k⟩
│   └── sbm_histograma_alpha.py     # histograma de 200 realizações, α fixo
├── comparacoes/
│   ├── ba_vs_er.py                 # BA e ER no mesmo gráfico
│   └── gerar_graficos.py           # lê os CSVs e monta as figuras
└── nucleos.py                      # utilitário: imprime os.cpu_count()

resultados/
├── <modelo>/csv/                   # saídas numéricas (semeadas)
├── <modelo>/figuras/               # PNGs
├── <modelo>/legacy/                # tudo que foi gerado antes da semeadura
└── _orfaos/                        # dados sem script correspondente
```

**`legacy/` não é versionado.** Todo resultado gerado antes da semeadura foi
movido para `resultados/<modelo>/legacy/` e entrou no `.gitignore`, junto com
`_orfaos/`. Não existe semente que os regere, então não servem como dado
versionado — ficam na máquina para conferência histórica e nada mais. O que o
repositório versiona daqui em diante é só saída com coluna `Semente_Base`.

Em `watts_strogatz/legacy/` há um par de subpastas `media_30_simulacoes/` (em
`csv/` e em `figuras/`) com resultados promediados sobre 30 realizações, gerados
por uma versão anterior dos scripts de WS. A nomenclatura ali é a antiga
(`Dilema_WA_results_*`, `WA_transiente_p_*_k_*`) e não corresponde à saída atual.

Todo script resolve seus diretórios de saída via `comum.diretorios(modelo)`, que
parte da raiz do repositório, então pode ser executado de qualquer diretório.
Nenhum script abre janela do matplotlib: tudo é gravado em disco.

## Amostragem

Definida em `src/comum.py` e usada por todos os scripts de simulação:

| | valor |
|---|---|
| 1 varredura | N passos (cada nó sorteado uma vez em média) |
| passos por simulação | 10⁶ (= 1000 varreduras, N = 1000) |
| registro da série | a cada 100 passos = 0,1 varredura |
| registros por simulação | 10.000 |
| transiente descartado | 1.000 registros = 100 varreduras = 10% |
| amostras estacionárias | 9.000 |

A coluna de tempo dos CSVs novos (`Tempo_varreduras`) está em varreduras, não em
índice de registro.

**Por que isso importa.** Antes cada script tinha sua própria taxa de registro e
seu próprio corte: BA registrava a cada 100 passos e descartava 100 registros
(9.900 amostras), ER registrava a cada 1.000 e descartava 100 (900 amostras),
WS/SBM registravam a cada 1.000 e descartavam 1.000 (**100** amostras). Como o
desvio publicado é σ/√N, as barras de erro de BA e ER diferiam por
√(9900/900) = 3,3 — e o σ das duas séries era o mesmo (0,0207 vs 0,0203 em
⟨k⟩ = 6). A diferença era artefato da taxa de amostragem, não física, e aparecia
no gráfico de comparação como se BA fosse 3× mais preciso que ER.

> **Os CSVs em `resultados/<modelo>/legacy/` são anteriores a essa
> padronização.** As médias continuam válidas como ordem de grandeza, mas as
> barras de erro não são comparáveis entre modelos. Para publicar a comparação é
> preciso regerar.

## Reprodutibilidade

Toda a aleatoriedade sai de uma **semente-base** inteira, definida em
`src/comum.py` (`SEMENTE_PADRAO`) e sobrescrevível por linha de comando ou por
variável de ambiente:

```bash
python src/sbm/sbm_varia_k.py --semente 12345
```

| origem | precedência |
|---|---|
| `--semente N` na linha de comando | 1ª |
| variável de ambiente `TCC_SEMENTE` | 2ª |
| `comum.SEMENTE_PADRAO` | padrão |

Como funciona:

- **Nenhum script usa `random` ou `np.random` globais.** `comum.geradores(semente)`
  devolve um par `(np.random.Generator, random.Random)` que é passado como
  argumento até o laço da dinâmica. As duas correntes vêm de derivações
  distintas da mesma semente, então consumir uma não desloca a outra.
- **Cada ponto da varredura tem sua própria semente**, derivada com
  `comum.semente_de_ponto(base, rótulo, *parâmetros)`. Os rótulos entram no
  `spawn_key` da `SeedSequence`, então a semente depende de *qual* ponto é e não
  da ordem em que a varredura chegou nele: rodar a varredura inteira ou um ponto
  isolado dá exatamente a mesma sequência de números.
- **As realizações de um ensemble** saem de `comum.sementes_de_realizacoes()`
  (`SeedSequence.spawn`) e são passadas **como argumento da tarefa** do
  `multiprocessing`. No Windows o start method é `spawn`: o processo filho
  reimporta o módulo do zero e não herda gerador nenhum do pai — herdar a
  semente não funcionaria. Antes, os dois scripts paralelos chamavam
  `SeedSequence()` dentro do filho, sem entropia fixa.
- **Os geradores do networkx** (`barabasi_albert_graph`, `erdos_renyi_graph`,
  `watts_strogatz_graph`, `stochastic_block_model`) recebem o gerador numpy em
  `seed=`, então a topologia também é reproduzível.
- **A semente vai para a saída.** Todo CSV de simulação ganhou a coluna
  `Semente_Base`, e cada script imprime a semente que usou. Um CSV com
  `Semente_Base = 12345` é regerado rodando o mesmo script com
  `--semente 12345`.

Trocar a semente-base muda todos os números; é o único ponto do código onde isso
acontece.

Três variáveis de ambiente a mais existem para testar a reprodutibilidade em
segundos em vez de horas, sem tocar em `resultados/`: `TCC_VARREDURAS` e
`TCC_REGISTROS_TRANSIENTE` reduzem a amostragem, e `TCC_RESULTADOS` redireciona
a raiz das saídas.

## Como rodar

```bash
pip install -r requirements.txt
```

```bash
python src/erdos_renyi/er_varia_grau_medio.py
```

Para remontar as figuras de comparação a partir dos CSVs já existentes, sem
resimular nada (leva segundos):

```bash
python src/comparacoes/gerar_graficos.py
```

Um ponto de varredura leva ~2,7 s (10⁶ passos); regerar tudo leva ~35 min. Os
que usam `multiprocessing` chamam `comum.processos()`, que deixa dois núcleos
livres — `TCC_PROCESSOS=N` sobrescreve. Mudar esse número não muda resultado
nenhum: cada tarefa carrega sua própria semente.

## O modelo

**Agentes.** N = 1000 nós, cada um com um estado `value` ∈ {0 = coopera, 1 = delata},
sorteado inicialmente com probabilidade `p`.

**Dinâmica.** A cada passo sorteia-se um nó e um vizinho dele. O par é atualizado
segundo uma regra determinística:

| par | resultado |
|-----|-----------|
| C, C | ambos permanecem C |
| C, D | o cooperador vira D |
| D, C | o cooperador vira D |
| D, D | **ambos viram C** |

Uma unidade de tempo = N passos. Descarta-se o transiente e calcula-se a média e
o desvio padrão da média da fração de cooperadores no estado estacionário, com os
parâmetros da seção [Amostragem](#amostragem).

Essa regra é exatamente **Win-Stay, Lose-Shift** (Pavlov, Nowak & Sigmund 1993)
com nível de aspiração A na faixa P < A < R: quem recebeu um payoff acima da
aspiração repete a ação, quem recebeu abaixo troca. Equivalentemente, ambos os
nós assumem o valor `s_i XOR s_j`.

## Resultados

| Rede | Resultado |
|------|-----------|
| Erdős-Rényi | ρ cai de 0,78 (⟨k⟩=2) e satura em ~0,51 conforme ⟨k⟩ cresce |
| Barabási-Albert | mesma tendência decrescente com ⟨k⟩ = 2m |
| Watts-Strogatz, k=2 | ρ = 1,0 exato para todo p de religação (anel trava em cooperação) |
| SBM | ρ ≈ 0,628 constante para α de 0,1 a 0,9, com ⟨k⟩ fixo |

**Conclusão.** O parâmetro de controle é o **grau médio**, não a topologia. A
estrutura de comunidades (α no SBM, com ⟨k⟩ mantido constante) não afeta o
resultado.

Isso é consistente com o campo médio da regra: sorteando um par aleatório,
`E[Δρ] ∝ 2(1−ρ)(1−2ρ)`, cujo ponto fixo estável é **ρ\* = 1/2**, independente da
rede. Os desvios observados em relação a 1/2 são correções de conectividade
finita e de regularidade da rede. Os dados confirmam: ER com ⟨k⟩=20 dá 0,514, e
condições iniciais p₀ = 0,1 e p₀ = 0,9 convergem ambas para ≈ 0,54.

## Limitações conhecidas

Documentadas aqui porque determinam o alcance das conclusões acima:

1. **A matriz de payoff não é usada.** A classificação ganhou/perdeu está
   embutida na estrutura dos `if`, não calculada a partir dos payoffs. Alterar
   os valores em `calc_score` não muda nenhum resultado. Não há varredura do
   parâmetro de tentação (b, ou T/R), que é o eixo x padrão da literatura.

2. **O nível de aspiração é implícito.** WSLS exige um limiar A separando
   ganho de perda. O código fixa P < A < R sem declarar. Com S < A < P, o estado
   todo-D vira absorvente e a cooperação desaparece em qualquer rede — ou seja,
   o resultado principal depende de uma escolha não declarada.

3. **Não há dinâmica evolutiva.** Todo agente é um autômato WSLS fixo: ninguém
   imita, ninguém se reproduz, nenhuma estratégia compete com outra. "Fração de
   cooperadores" mede a fase de um autômato, não o sucesso evolutivo da cooperação.

4. **Reciprocidade de rede está ausente por construção.** O mecanismo pelo qual
   a topologia importa nessa literatura exige payoff somado sobre toda a
   vizinhança e imitação baseada nele. Aqui a atualização olha apenas os rótulos
   de um par sorteado, então grau e clusterização entram só pelo sorteio.

5. **WSLS sem memória por parceiro.** No DP iterado, Pavlov reage à última
   rodada contra *aquele* oponente. Aqui cada nó tem uma ação global única e é
   pareado com um vizinho diferente a cada passo.

6. **Os resultados em `legacy/` são anteriores à semeadura.** Foram gerados
   quando todo gerador de grafo recebia `seed=None`, então não trazem coluna
   `Semente_Base` e não podem ser regerados exatamente — por isso saíram do
   versionamento. Vale para os números antigos, não para o código: ver
   [Reprodutibilidade](#reprodutibilidade).

### Pontos menores

- `ba_prototipo_com_score.py`: os dois ramos do `if` de comparação de score são
  logicamente idênticos, então a pontuação acumulada não influencia nada. O
  script roda a mesma dinâmica dos demais.
- `resultados/_orfaos/Dilema_LFR_results.csv` (local, não versionado) tem
  valores entre 2,9 e 5,3, fora
  do intervalo [0,1] de uma fração. Nenhum script atual gera LFR — provável erro
  de normalização em código perdido.
- Os CSVs históricos `Dilema_SBM_results_k_*.csv` vieram de `sbm_varia_alpha.py`
  ou de `sbm_varia_alpha_ensemble.py`, que gravavam no mesmo arquivo e se
  sobrescreviam. Não há registro de qual. Hoje os três varrimentos de α escrevem
  `sbm_alpha_k_{k}_{n}sim.csv`, com n = 1, 20 ou 25.
- Nos CSVs em `legacy/` a coluna de tempo é índice de registro, não varredura.
  Os cabeçalhos deles não foram renomeados justamente para não mascarar isso.
- A nomenclatura de `legacy/` é a antiga (`WA_`, `Dilema_`), diferente da atual —
  ver a [convenção de nomes](PROTOCOLO.md#7-convenção-de-nomes-e-o-que-já-foi-resolvido).

### Já corrigido

- Amostragem e corte de transiente unificados em `src/comum.py` (ver
  [Amostragem](#amostragem)).
- Nada era reprodutível: `seed=None` em todo gerador de grafo, `random`/
  `np.random` globais em 9 dos 11 scripts, e `SeedSequence()` sem entropia fixa
  nos dois paralelos. Agora há semente-base explícita, derivação determinística
  por ponto da varredura e propagação para os processos filhos — ver
  [Reprodutibilidade](#reprodutibilidade). Verificado rodando cada script duas
  vezes com a mesma semente e comparando os CSVs byte a byte.
- `gerar_graficos.py` gravava tudo com `plt.show()` e não produzia arquivo
  nenhum; as figuras vinham de print de tela. Agora salva PNG em
  `resultados/comparacoes/figuras/`.
- `comparar_graficos_p0` e `comparar_WA_transiente` levantavam `ValueError`:
  liam CSVs de série de 2 colunas com um leitor endurecido para 3. Agora usam
  `comum.ler_serie`.
- `ba_prototipo_com_score.py` e `sbm_histograma_alpha.py` não gravavam nada em
  disco. Agora salvam CSV e figura.
- `ws_varia_k.py` e `ws_varia_p.py` gravavam figuras com o mesmo nome e se
  sobrescreviam; agora vão para `figuras/varia_k/` e `figuras/varia_p/`.
- `sbm_varia_alpha.py` salvava toda iteração em `SBM_verificacao.png`,
  sobrescrevendo; agora o nome inclui o alpha.
- `ws_varia_p.py` tinha o título "Erdos-renyi" nos gráficos de Watts-Strogatz.
- Nomes de saída inconsistentes entre quem grava e quem lê: `gerar_graficos.py`
  procurava quatro CSVs que nenhum script produzia e pulava duas figuras em
  silêncio. Os nomes foram unificados em `<modelo>_<eixo>_<parâmetro>.csv` (ver
  [PROTOCOLO](PROTOCOLO.md#7-convenção-de-nomes-e-o-que-já-foi-resolvido)), o que
  só ficou barato depois que os dados antigos saíram do versionamento.
- `p₀` estava fixo no corpo de `ba_varia_grau_medio.py`: a figura que contrapõe
  p₀ = 0,1 a 0,9 exigia editar o script e rodar de novo, e a série de transiente
  gravava sempre no mesmo nome, então só o último `m` sobrevivia. Agora p₀ é uma
  varredura (`P0_INICIAIS`) e o nome do arquivo carrega `m` e `p₀`.
- A comparação entre todos os modelos misturava BA com p₀ = 0,9 e os demais com
  0,5. A curva de BA passou a vir de `ba_vs_er.py`, que roda a 0,5.
- Barras de erro subestimadas: o desvio era `σ/√N` sobre uma série temporal
  correlacionada, tratando como independentes amostras separadas por 100 passos
  num grafo de 1000 nós. Medido em ER, o erro real é 3 a 5 vezes maior. Agora é
  estimado por blocagem (`comum.erro_por_blocagem`), validada contra AR(1). As
  médias não mudam — só a barra de erro, e só nos experimentos de uma
  realização; os de ensemble já usavam realizações independentes.
- A dinâmica estava copiada em 11 scripts, então mudar a regra exigia replicar
  11 vezes sem nada garantindo que ficassem iguais. Agora vive em
  `comum.evoluir()`; a única cópia restante é a de `ba_prototipo_com_score.py`,
  que tem regra própria. O laço também reconstruía `list(G.nodes())` a cada um
  dos 10⁶ passos — fixar as listas uma vez deu os mesmos resultados (58 CSVs
  byte a byte) 3,6x mais rápido.
- Três políticas de paralelização diferentes (`Pool()`, `Pool(processes=8)`,
  `min(8, cpu_count() - 2)`), uma por script. Agora todas usam
  `comum.processos()`.
- `sbm_varia_alpha.py` varria α com uma realização por ponto, medindo o mesmo
  que `sbm_varia_alpha_ensemble.py` mede com 20. Aposentado.
- Encoding: nenhum `open()` declarava `encoding=`, então em Windows os CSVs
  saíam em cp1252 e 18 arquivos do SBM tinham "fração" corrompido no cabeçalho
  (bytes U+FFFD gravados no arquivo). Cabeçalhos agora são ASCII sem acento nem
  cedilha, e todo I/O é UTF-8 explícito. Os 18 arquivos foram reparados — só o
  cabeçalho; nenhum número foi tocado.

## Correspondência com os nomes originais

| Original | Atual |
|----------|-------|
| `Dilema_barabasi.py` | `src/barabasi_albert/ba_varia_grau_medio.py` |
| `Dilema_prisioneiro.py` | `src/barabasi_albert/ba_prototipo_com_score.py` |
| `Dilema_Erdos.py` | `src/erdos_renyi/er_varia_grau_medio.py` |
| `Dilema_WS_k_varia.py` | `src/watts_strogatz/ws_varia_k.py` |
| `Dilema_WS_p_varia.py` | `src/watts_strogatz/ws_varia_p.py` |
| `DIlema_WS_P_transicao.py` | `src/watts_strogatz/ws_transiente.py` |
| `Dilema_SBM_alpha_varia.py` | `src/sbm/sbm_varia_alpha.py` |
| `Dilema_SBM_alpha_varias_sim.py` | `src/sbm/sbm_varia_alpha_ensemble.py` |
| `Dilema_SBM_k_varia.py` | `src/sbm/sbm_varia_k.py` |
| `teste_paral.py` | `src/sbm/sbm_varia_alpha_paralelo.py` |
| `SBM_teste_alpha.py` | `src/sbm/sbm_histograma_alpha.py` |
| `Dilema_varios_modelos.py` | `src/comparacoes/ba_vs_er.py` |
| `graficos_dilema.py` | `src/comparacoes/gerar_graficos.py` |
| `nucleos.py` | `src/nucleos.py` |
| — | `src/comum.py` (novo) |

## Próximos passos

Regerar os resultados com semente registrada, repovoando
`resultados/<modelo>/csv/`. O que existe hoje está em `legacy/` e vem de antes da
padronização da amostragem e da semeadura (limitação 7).

Reescrita da dinâmica para teoria de jogos evolutiva padrão, mantendo os mesmos
modelos de rede para comparação direta:

- cada nó joga com **todos** os vizinhos e acumula payoff Π;
- atualização por imitação com regra de Fermi:
  `P(i copia j) = 1 / (1 + exp[(Π_i − Π_j)/K])`;
- varredura do parâmetro de tentação como eixo x;
- decisão explícita entre payoff acumulado e payoff médio por vizinho — a
  escolha altera fortemente os resultados em redes livres de escala;
- barras de erro sobre um ensemble de realizações independentes, não sobre
  uma série temporal correlacionada.

Alternativa: manter WSLS e tornar o nível de aspiração A um parâmetro explícito,
varrendo-o para mapear os regimes (absorvente em D / coexistência / oscilatório).

## Referências

- Nowak, M. & Sigmund, K. (1993). *A strategy of win-stay, lose-shift that
  outperforms tit-for-tat in the Prisoner's Dilemma game*. Nature 364, 56–58.
- Nowak, M. & May, R. (1992). *Evolutionary games and spatial chaos*. Nature 359, 826–829.
- Szabó, G. & Fáth, G. (2007). *Evolutionary games on graphs*. Physics Reports 446, 97–216.
