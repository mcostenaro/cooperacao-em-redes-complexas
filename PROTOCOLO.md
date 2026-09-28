# Protocolo experimental

Mapa dos experimentos deste repositório: o que cada script simula, com que
parâmetros, o que grava e quanto custa. Escrito para que se entenda o escopo do
TCC sem precisar reler os 11 scripts.

Complementa o [README](README.md), que cobre o modelo, a amostragem e a
semeadura. Aqui é o **inventário dos experimentos**.

---

## 1. A pergunta

Como a **topologia da rede** afeta a fração estacionária de cooperadores numa
dinâmica de dilema do prisioneiro? Quatro famílias de rede, todas com N = 1000
nós, varridas pelo mesmo eixo sempre que possível — o **grau médio ⟨k⟩** — mais
um eixo próprio de cada família (religação no Watts-Strogatz, força de comunidade
no SBM).

Resposta obtida: entre redes aleatórias, o parâmetro de controle é o grau médio;
a topologia só pesa em grau baixo, quando a rede é regular (o anel do
Watts-Strogatz). Ver [Resultados](README.md#resultados).

## 2. A dinâmica (idêntica em todos os experimentos)

Cada nó carrega `value ∈ {0 = coopera, 1 = delata}`, sorteado no início com
probabilidade `p₀`. A cada passo sorteia-se um nó e um vizinho dele, e o par é
atualizado de forma determinística:

| par | resultado |
|-----|-----------|
| C, C | ambos permanecem C |
| C, D | o cooperador vira D |
| D, C | o cooperador vira D |
| D, D | **ambos viram C** |

É Win-Stay Lose-Shift (Pavlov) com nível de aspiração implícito entre P e R.
Equivalente a ambos os nós assumirem `s_i XOR s_j`. As limitações dessa escolha
estão em [Limitações conhecidas](README.md#limitações-conhecidas) — em especial:
a matriz de payoff não é usada, e não há dinâmica evolutiva.

**Uma diferença entre scripts:** os que rodam sobre redes que podem ter nós
isolados (ER, SBM) testam `G.degree[nó] >= 1` antes de sortear o vizinho, e o
passo é perdido se o nó for isolado. BA e WS não testam, porque suas construções
garantem grau ≥ 1. Ou seja, em ER com ⟨k⟩ = 2 uma fração dos passos não faz nada
— o tempo efetivo é menor que o nominal.

## 3. Parâmetros globais

De `src/comum.py`, valem para todo experimento:

| | valor |
|---|---|
| N | 1000 nós |
| passos por simulação | 10⁶ (1000 varreduras) |
| registro da série | a cada 100 passos (0,1 varredura) |
| registros | 10.000 |
| transiente descartado | 1.000 registros (10%) |
| amostras estacionárias | 9.000 |
| semente-base padrão | `SEMENTE_PADRAO`, sobrescrevível por `--semente N` |

**A coluna de erro.** Há duas fontes, conforme o experimento:

- **Ensemble** (E7, E8): σ/√N sobre as realizações independentes. É o caso
  fácil — as amostras são independentes de fato. E10 também é ensemble, mas
  grava as realizações cruas em vez de uma barra de erro.
- **Uma realização** (E1, E3, E4, E5, E9, E11): erro do valor médio da série
  temporal, estimado por **blocagem** (`comum.erro_por_blocagem`). Não se pode
  usar σ/√N aqui: entre dois registros passam 100 passos, que tocam no máximo
  200 dos 1000 nós, então a medida seguinte é quase a mesma medida. Contar 9.000
  amostras onde há uma centena de independentes subestima o erro — medido em ER,
  por um fator de 3 a 5:

  | | ⟨k⟩ = 6 | ⟨k⟩ = 20 |
  |---|---|---|
  | σ/√N (ingênuo) | 0,000219 | 0,000207 |
  | blocagem (patamar) | 0,00120 | 0,00072 |
  | razão | 5,5x | 3,5x |

- **E6** não grava erro: promedia 30 realizações e grava só a curva média.

A blocagem sobe os níveis (blocos de 1, 2, 4, ... registros) até o erro estimado
parar de crescer, e usa esse patamar. Testada contra AR(1), que tem fórmula
fechada, acerta dentro de ~6% para correlação de 0 a 0,98 — inclusive no caso
independente, onde devolve σ/√N e não infla a barra à toa.

**O que a barra de uma realização não cobre.** A blocagem mede a flutuação
temporal da rede que foi sorteada. Outra rede com os mesmos parâmetros dá outra
média, e em grau baixo essa variação é maior que a barra: pelos ensembles do SBM
(E8, E10), ~0,015 em ⟨k⟩ = 2, ~0,005 em 4, ~0,002 em 6, e ~0,001 (igual à barra)
de ⟨k⟩ = 8 em diante. Comparar redes diferentes em ⟨k⟩ ≤ 6 exige usar esse
espalhamento, não a barra. Ver [ANALISE](ANALISE.md).

## 4. Mapa dos experimentos

| # | script | rede | eixo varrido | fixo | pontos | realiz./ponto | custo |
|---|--------|------|--------------|------|-------:|--------------:|------:|
| E1 | `ba_varia_grau_medio.py` | BA | m = 1..10 (⟨k⟩ = 2m), para p₀ ∈ {0,1; 0,9} | — | 20 | 1 | ~1 min |
| E2 | `ba_prototipo_com_score.py` | BA | — (ponto único) | m = 3, p₀ = 0,5 | 1 | 1 | ~3 s |
| E3 | `er_varia_grau_medio.py` | ER | ⟨k⟩ = 2..20 | p₀ = 0,5 | 10 | 1 | ~30 s |
| E4 | `ws_varia_k.py` | WS | k = 2..20, para 5 valores de p | p₀ = 0,5 | 50 | 1 | ~2 min |
| E5 | `ws_varia_p.py` | WS | p = 0..1, para k ∈ {2,6,10} | p₀ = 0,5 | 33 | 1 | ~2 min |
| E6 | `ws_transiente.py` | WS | ρ(t), 4 valores de p × k ∈ {2,6,10} | p₀ = 0,5 | 12 | **30** | ~2 min |
| E7 | `sbm_varia_alpha_ensemble.py` | SBM | α = 0,1..0,9 | ⟨k⟩ = 4 | 9 | **20** | ~8 min |
| E8 | `sbm_varia_alpha_paralelo.py` | SBM | α = 0,1..0,9, para ⟨k⟩ = 2..20 | — | 90 | **25** | ~15 min |
| E9 | `sbm_varia_k.py` | SBM | ⟨k⟩ = 2..20 | α = 0,5 | 10 | 1 | ~30 s |
| E10 | `sbm_histograma_alpha.py` | SBM | — (distribuição) | α = 0,5, ⟨k⟩ = 4 | 1 | **200** | ~1 min |
| E11 | `ba_vs_er.py` | BA + ER | ⟨k⟩ = 2..20 | p₀ = 0,5 | 10 | 1 (×2 redes) | ~1 min |

Custos são de relógio na configuração cheia, a **2,7 s por simulação** de 10⁶
passos, medido nesta máquina (12 núcleos). E6, E8 e E10 usam `multiprocessing`
com `comum.processos()` — por padrão, núcleos − 2.

> Antes da extração da dinâmica a mesma simulação levava 9,6 s e a coleção
> inteira passava de 3 h. Ver [por que evoluir é rápida](#por-que-evoluir-é-rápida).

Fora da tabela: `comparacoes/gerar_graficos.py` não simula nada — lê os CSVs e
monta as figuras de comparação (segundos). `nucleos.py` só imprime
`os.cpu_count()`.

---

## 5. Os experimentos, um a um

### E1 — Barabási-Albert, varre grau médio
`src/barabasi_albert/ba_varia_grau_medio.py`

Rede livre de escala por ligação preferencial: `barabasi_albert_graph(1000, m)`,
com m = 1..10, então ⟨k⟩ = 2m = 2..20. Varre também a **condição inicial**,
p₀ ∈ {0,1; 0,9} (constante `P0_INICIAIS`) — é o experimento que mostra que os
dois extremos convergem para o mesmo patamar. Todos os outros experimentos usam
p₀ = 0,5 fixo.

Saída, uma coleção por p₀:
- `ba_grau_medio_p0_{p0}.csv` — `Grau_Medio, Media_Frac_Coop, Desvio_Padrao_da_Media, Semente_Base`
- `ba_serie_m_{m}_p0_{p0}.csv` — série do transiente (200 registros = 20 varreduras), uma por m
- `figuras/ba_m_{m}_p0_{p0}.png`

A figura `comparacao_fracao_de_cooperadores.png` usa as séries de **m = 10**
(⟨k⟩ = 20) nos dois p₀.

> Como este experimento roda com p₀ ≠ 0,5, a curva de BA que entra na comparação
> entre todos os modelos **não** vem daqui: vem de E11, que roda BA a p₀ = 0,5
> como os demais modelos.

### E2 — Protótipo com score
`src/barabasi_albert/ba_prototipo_com_score.py`

Ponto único (m = 3, p₀ = 0,5) que acumula pontuação por `calc_score` e decide a
atualização comparando os scores dos dois jogadores. **Os dois ramos do `if` de
comparação são logicamente idênticos**, então o score não influencia nada: roda a
mesma dinâmica de E1. Mantido como registro da tentativa de usar matriz de
payoff, não como experimento com resultado próprio.

Saída: `ba_prototipo_score_m3.csv` (série completa, 10.000 registros) e figura.

### E3 — Erdős-Rényi, varre grau médio
`src/erdos_renyi/er_varia_grau_medio.py`

`erdos_renyi_graph(1000, k/1000)` para ⟨k⟩ = 2, 4, ..., 20. É o experimento de
referência: grafo aleatório sem estrutura, contra o qual as outras topologias são
comparadas.

Saída: `er_grau_medio.csv` (`Grau_Medio, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`) e uma figura da série por ponto.

### E4 — Watts-Strogatz, varre k com p de religação fixo
`src/watts_strogatz/ws_varia_k.py`

`watts_strogatz_graph(1000, k, p)` com k = 2, 4, ..., 20 para cada
p ∈ {0; 0,02; 0,2; 0,6; 1}. p = 0 é o anel regular puro, p = 1 é religação total.

Saída: um CSV por p, `ws_varia_k_p_{p}.csv` (`k, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`); figuras em `figuras/varia_k/`.

Resultado notável: em k = 2 a fração fica exatamente 1,0 para todo p — a
dinâmica é absorvida em cooperação total em poucas dezenas de varreduras.

> **Dois pontos de k = 4 não estão estacionários.** Com p = 0 o anel também é
> absorvido em 1,0, mas entre ~900 e ~1300 varreduras, na borda das 1000
> simuladas: o 0,903 do CSV é uma média sobre a absorção em andamento. Com
> p = 0,02 a série ainda sobe no fim da janela (0,717 no CSV, ~0,735 com 5000
> varreduras). Ver [limitação 7](README.md#limitações-conhecidas).

### E5 — Watts-Strogatz, varre p de religação com k fixo
`src/watts_strogatz/ws_varia_p.py`

O transposto de E4: p = 0; 0,1; ...; 1,0 (11 valores) para cada k ∈ {2, 6, 10}.
É o eixo que testa se a transição small-world afeta a cooperação.

Saída: um CSV por k, `ws_varia_p_k_{k}.csv` (`p, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`); figuras em `figuras/varia_p/`.

Alimenta a figura `comparacao_WS_k.png`.

### E6 — Watts-Strogatz, dinâmica do transiente
`src/watts_strogatz/ws_transiente.py`

Único experimento que estuda **ρ(t)** em vez do estacionário. Guarda os primeiros
2.000 registros (200 varreduras) e promedia **30 realizações independentes** por
ponto, para a curva sair lisa. Não descarta transiente — o transiente é o objeto.

k ∈ {2, 6, 10} × p ∈ {0; 0,02; 0,2; 1} = 12 curvas, 360 simulações.
Paralelo, com `comum.processos()` (núcleos − 2).

Saída: `ws_transiente_k_{k}_p_{p}.csv` (`Tempo_varreduras, Media_Frac_Coop,
Semente_Base`) e uma figura por k com as quatro curvas de p sobrepostas.

### E7 — SBM, varre α com ⟨k⟩ = 4
`src/sbm/sbm_varia_alpha_ensemble.py`

Quatro blocos de 250 nós. α é a razão entre a probabilidade de ligação **entre**
blocos e **dentro** do bloco: α → 0 são comunidades isoladas, α = 1 é um ER
homogêneo. A parametrização mantém o grau médio constante enquanto α varia:

```
p_intra = 4⟨k⟩ / (N(1 + 3α))        p_inter = α · p_intra
```

Isso é o coração do experimento de SBM: **isolar o efeito da estrutura de
comunidades do efeito do grau médio**. α = 0,1..0,9, com **20 realizações
independentes** por ponto — a barra de erro é σ/√20 sobre realizações, não sobre
a série temporal. Sequencial (não usa `multiprocessing`), por isso é caro.

> Havia um `sbm_varia_alpha.py` que fazia esta mesma varredura com **uma**
> realização por ponto. Foi aposentado: o CSV dele era dominado por este, e as
> figuras de série temporal por α que ele produzia eram plots de verificação.
> Está no histórico do git se precisar.

Saída: `sbm_alpha_k_4_20sim.csv` e figura com barras de erro.

### E8 — SBM, α × ⟨k⟩ com ensemble de 25, paralelo
`src/sbm/sbm_varia_alpha_paralelo.py`

O experimento mais caro: E7 repetido para cada ⟨k⟩ = 2, 4, ..., 20. São
10 × 9 × 25 = 2.250 simulações, em paralelo com `comum.processos()`. Produz a família de
curvas α × ρ, uma por grau médio — a evidência principal de que α não importa e
⟨k⟩ importa.

Saída: `sbm_alpha_k_{k}_25sim.csv` por grau médio (`Alpha, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`) e figura por k. O nome segue o mesmo
padrão de E7 (`_20sim`), então as duas varreduras de α convivem sem colidir —
inclusive em ⟨k⟩ = 4, que as duas cobrem.

### E9 — SBM, varre grau médio com α = 0,5
`src/sbm/sbm_varia_k.py`

O corte ortogonal a E7: α fixo em 0,5, ⟨k⟩ = 2..20, uma realização por ponto. É
a curva de SBM que entra na comparação entre todos os modelos.

Saída: `sbm_grau_medio_alpha_0.5.csv` (`Grau_Medio, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`) e figura.

### E10 — SBM, histograma de realizações
`src/sbm/sbm_histograma_alpha.py`

Não varre nada: fixa α = 0,5 e ⟨k⟩ = 4 e roda **200 realizações independentes**
para mostrar a distribuição da média estacionária entre realizações. Responde
"qual é a dispersão real entre realizações", que é justamente o que a barra de
erro sobre a série de uma realização não mede. Resposta: σ = 0,0051, contra
0,0011 da barra por blocagem nesse grau.

Saída: `sbm_histograma_alpha_0.5_k_4.csv` (`Realizacao, Media_Frac_Coop,
Semente_Base` — as 200 realizações cruas, para refazer o histograma sem
resimular) e o histograma.

### E11 — BA contra ER no mesmo eixo
`src/comparacoes/ba_vs_er.py`

Roda as duas redes no mesmo laço de ⟨k⟩ = 2..20 (BA com m = ⟨k⟩/2), ambas com
p₀ = 0,5, para a comparação sair sem viés de condição inicial. Note que **E1 usa
p₀ ∈ {0,1; 0,9} e este usa 0,5** — os números de BA dos dois não são
intercambiáveis.

Saída: `ba_vs_er.csv` com as duas redes lado a lado (`Grau_Medio,
BA_Media_Frac_Coop, BA_Desvio_Padrao_da_Media, ER_Media_Frac_Coop,
ER_Desvio_Padrao_da_Media, Semente_Base`) e `comparacao_modelos.png`.

Como as três primeiras colunas são exatamente `Grau_Medio, Media, Desvio` de BA,
este CSV também alimenta a curva de BA da figura `comparacao_todos_modelos.png`
— é a única fonte de BA a p₀ = 0,5, que é o valor usado por ER, WS e SBM.

### Montagem das figuras de comparação
`src/comparacoes/gerar_graficos.py`

Não simula: lê `resultados/<modelo>/csv/` e monta as figuras finais em
`resultados/comparacoes/figuras/`. Pula com aviso a figura cujo CSV de entrada
não existir. Roda em segundos, então é seguro chamar a qualquer momento.

Figuras: `comparacao_WS_k.png`, `comparacao_todos_modelos.png`,
`comparacao_WS_transiente.png`, `comparacao_fracao_de_cooperadores.png`,
`erdos_renyi_grau_medio.png`, `sbm_alpha_por_grau_medio.png`.

---

## 6. Estado atual dos dados

**Todos os experimentos foram regerados com semente** (`Semente_Base =
20242025`, em 26/08/2026). `resultados/<modelo>/csv/` tem 58 CSVs, todos com a
coluna `Semente_Base`, e as figuras de comparação foram remontadas a partir
deles. Os números citados no [README](README.md#resultados) saem desses
arquivos.

O que existe em `resultados/<modelo>/legacy/` veio de antes da padronização da
amostragem e da semeadura: as médias servem como ordem de grandeza, as barras
de erro não são comparáveis entre modelos, e nenhum número pode ser
reproduzido. Esses arquivos estão fora do versionamento (ver
[README](README.md#estrutura)).

## 7. Convenção de nomes e o que já foi resolvido

Os nomes de saída seguem hoje um padrão único: `<modelo>_<eixo>[_<parâmetro>].csv`,
tudo minúsculo, sem `Dilema_` nem `WA_`. Cada nome diz qual experimento o gerou e
com que parâmetro:

| experimento | CSV |
|---|---|
| E1 | `ba_grau_medio_p0_{p0}.csv`, `ba_serie_m_{m}_p0_{p0}.csv` |
| E2 | `ba_prototipo_score_m{m}.csv` |
| E3 | `er_grau_medio.csv` |
| E4 | `ws_varia_k_p_{p}.csv` |
| E5 | `ws_varia_p_k_{k}.csv` |
| E6 | `ws_transiente_k_{k}_p_{p}.csv` |
| E7, E8 | `sbm_alpha_k_{k}_{n}sim.csv` (n = 20, 25) |
| E9 | `sbm_grau_medio_alpha_{alpha}.csv` |
| E10 | `sbm_histograma_alpha_{alpha}_k_{k}.csv` |
| E11 | `ba_vs_er.csv` |

**Renomear foi possível porque os dados antigos saíram do versionamento.** Os
nomes legados existiam para não quebrar a correspondência com CSVs já gerados;
uma vez que esses foram para `legacy/` e tudo foi regerado, a compatibilidade
deixou de custar algo. Os arquivos em `legacy/` mantêm a nomenclatura antiga —
não confunda as duas.

Resolvido junto com a renomeação:

1. **`gerar_graficos.py` procurava quatro nomes que nenhum script produzia**
   (`Dilema_Barabasi_results`, `Dilema_SBM_results_alpha_05`, `WA_p_02`,
   `fracao_de_cooperadores01/09`), e por isso pulava em silêncio as figuras
   "todos os modelos" e "BA p₀ = 0,1 vs 0,9". Produtor e consumidor agora usam
   os mesmos nomes.
2. **A série de transiente de E1 se sobrescrevia:** o nome não incluía `m`, e as
   10 iterações gravavam no mesmo arquivo. Agora é `ba_serie_m_{m}_p0_{p0}.csv`.
3. **p₀ estava fixo em 0,9 no corpo da função de E1.** A figura que contrapõe
   p₀ = 0,1 e 0,9 dependia de alguém editar o arquivo e rodar de novo, sem
   registro de qual valor gerou qual CSV — os legados
   `Dilema_Barabasi_p03/p09.csv` são resquício disso. Virou a varredura
   `P0_INICIAIS`.
4. **BA entrava na comparação geral com p₀ = 0,9** enquanto ER, WS e SBM usavam
   0,5. A curva de BA passou a vir de E11, que roda a p₀ = 0,5.
5. **`SBM_50s_*.csv` dizia 50 realizações e eram 25.** Agora o nome carrega o
   número que o código usa.

6. **A dinâmica estava copiada em 11 arquivos.** Mudar a regra exigia replicar
   11 vezes, sem nada garantindo que ficassem iguais. Agora o laço vive em
   `comum.evoluir()` e existe em um lugar só — a exceção é
   `ba_prototipo_com_score.py` (E2), que tem regra própria e por isso mantém o
   laço dele.
7. **`sbm_varia_alpha.py` varria α com uma realização por ponto**, medindo o
   mesmo que E7 mede com 20. Aposentado.
8. **Três políticas de paralelização diferentes:** `Pool()` com todos os núcleos
   em E6, `Pool(processes=8)` fixo em E8, e `min(8, cpu_count() - 2)` em E10.
   As três agora chamam `comum.processos()`.

### Ainda em aberto

- **Dois pontos do WS com k = 4 (p = 0 e p = 0,02) não convergiram** nas 1000
  varreduras. Corrigir exige mais varreduras nesses pontos, ou um critério de
  parada por absorção — muda o protocolo, então ficou fora da regeração.
- **Os experimentos de uma realização** (E1, E3, E4, E5, E9, E11) não medem a
  variação entre redes, que domina em ⟨k⟩ ≤ 6. Trocá-los por ensembles fecharia
  as comparações em grau baixo (e a de BA contra ER, E11).
- **Escopo de reescrita do modelo**, não correção: matriz de payoff não usada,
  ausência de dinâmica evolutiva, e ausência de varredura do parâmetro de
  tentação — ver [Limitações conhecidas](README.md#limitações-conhecidas).

## 8. Como regerar tudo

Ordem sugerida — os baratos primeiro, para falhar cedo se algo estiver errado:

```bash
python src/erdos_renyi/er_varia_grau_medio.py --semente 12345
```

```bash
python src/barabasi_albert/ba_varia_grau_medio.py --semente 12345
```

```bash
python src/barabasi_albert/ba_prototipo_com_score.py --semente 12345
```

```bash
python src/sbm/sbm_varia_k.py --semente 12345
```

```bash
python src/comparacoes/ba_vs_er.py --semente 12345
```

```bash
python src/watts_strogatz/ws_transiente.py --semente 12345
```

```bash
python src/watts_strogatz/ws_varia_p.py --semente 12345
```

```bash
python src/watts_strogatz/ws_varia_k.py --semente 12345
```

```bash
python src/sbm/sbm_histograma_alpha.py --semente 12345
```

```bash
python src/sbm/sbm_varia_alpha_ensemble.py --semente 12345
```

```bash
python src/sbm/sbm_varia_alpha_paralelo.py --semente 12345
```

```bash
python src/comparacoes/gerar_graficos.py
```

**A mesma semente em todos** mantém a coleção coerente: os rótulos de varredura
já garantem que scripts diferentes não repitam a mesma corrente aleatória.

Custo total **~35 min** de relógio em sequência (3.134 simulações). Os três com
`multiprocessing` (E6, E8, E10) não devem rodar simultaneamente entre si —
brigam pelos mesmos núcleos.

Para testar a cadeia inteira antes, com saída redirecionada para não tocar em
`resultados/`:

```bash
TCC_VARREDURAS=5 TCC_REGISTROS_TRANSIENTE=5 TCC_RESULTADOS=/tmp/teste python src/erdos_renyi/er_varia_grau_medio.py
```

## 9. Onde mexer para estender

| quero... | mexer em |
|---|---|
| mudar a regra da dinâmica | `comum.evoluir()` — um lugar só |
| mudar amostragem, transiente, N | `src/comum.py` |
| mudar a semente-base | `src/comum.py`, `SEMENTE_PADRAO` |
| mudar quantos processos o `multiprocessing` usa | `comum.processos()` ou `TCC_PROCESSOS` |
| acrescentar um ponto à varredura | o `for` dentro de `loop()` do script |
| acrescentar uma figura de comparação | `src/comparacoes/gerar_graficos.py`, lista `tarefas` |

### A anatomia de um script de simulação

Depois da extração, todos seguem a mesma forma:

```python
def dilema_prisioneiro(<parametros do ponto>, semente):
    gerador_numpy, gerador_random = geradores(semente)   # correntes explicitas
    G = nx.<modelo>(..., seed=gerador_numpy)             # topologia semeada
    t_list, frac_coop = evoluir(G, p_i, gerador_numpy, gerador_random, n)
    return estatisticas(frac_coop)                       # media e erro

def loop(semente):
    for <ponto> in <varredura>:
        dilema_prisioneiro(<ponto>, semente_de_ponto(semente, VARREDURA, <ponto>))
    salvar_csv(..., semente=semente)
```

O que muda de um script para outro é a linha do grafo, a varredura e o que se
grava. A dinâmica é a mesma função em todos.

A única exceção é `ba_prototipo_com_score.py` (E2), que mantém laço próprio
porque a regra dele é outra — acumula score e decide comparando os dois
jogadores. Ele usa `comum.sortear_no`/`sortear_vizinho` para não duplicar o
sorteio.

### Por que `evoluir` é rápida

O laço original chamava `list(G.nodes())` e `list(G.neighbors(no))` a cada passo:
listas de mil elementos reconstruídas 10⁶ vezes por simulação. Como o grafo não
muda durante a dinâmica, `evoluir` as fixa uma vez (`listas_de_adjacencia`). São
exatamente as mesmas listas, na mesma ordem, então `choice` sorteia o mesmo
elemento e consome a mesma quantidade do gerador: **o resultado é idêntico** —
verificado com 58 CSVs byte a byte — e a simulação fica ~3,6x mais rápida
(2,7 s contra 9,6 s por 10⁶ passos).
