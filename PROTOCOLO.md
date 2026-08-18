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

Resposta obtida: o parâmetro de controle é o grau médio, não a topologia. Ver
[Resultados](README.md#resultados).

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

O desvio gravado é σ/√N sobre a série temporal (subestima a incerteza real —
limitação 6 do README), **exceto** nos três experimentos com ensemble (E8, E9,
E11), onde é σ/√N sobre realizações independentes. E6 não grava desvio nenhum:
promedia 30 realizações e grava só a curva média.

## 4. Mapa dos experimentos

| # | script | rede | eixo varrido | fixo | pontos | realiz./ponto | custo |
|---|--------|------|--------------|------|-------:|--------------:|------:|
| E1 | `ba_varia_grau_medio.py` | BA | m = 1..10 (⟨k⟩ = 2m), para p₀ ∈ {0,1; 0,9} | — | 20 | 1 | ~6 min |
| E2 | `ba_prototipo_com_score.py` | BA | — (ponto único) | m = 3, p₀ = 0,5 | 1 | 1 | ~20 s |
| E3 | `er_varia_grau_medio.py` | ER | ⟨k⟩ = 2..20 | p₀ = 0,5 | 10 | 1 | ~3 min |
| E4 | `ws_varia_k.py` | WS | k = 2..20, para 5 valores de p | p₀ = 0,5 | 50 | 1 | ~14 min |
| E5 | `ws_varia_p.py` | WS | p = 0..1, para k ∈ {2,6,10} | p₀ = 0,5 | 33 | 1 | ~9 min |
| E6 | `ws_transiente.py` | WS | ρ(t), 4 valores de p × k ∈ {2,6,10} | p₀ = 0,5 | 12 | **30** | ~9 min |
| E7 | `sbm_varia_alpha.py` | SBM | α = 0,1..0,9 | ⟨k⟩ = 4 | 9 | 1 | ~3 min |
| E8 | `sbm_varia_alpha_ensemble.py` | SBM | α = 0,1..0,9 | ⟨k⟩ = 4 | 9 | **20** | ~51 min |
| E9 | `sbm_varia_alpha_paralelo.py` | SBM | α = 0,1..0,9, para ⟨k⟩ = 2..20 | — | 90 | **25** | ~80 min |
| E10 | `sbm_varia_k.py` | SBM | ⟨k⟩ = 2..20 | α = 0,5 | 10 | 1 | ~3 min |
| E11 | `sbm_histograma_alpha.py` | SBM | — (distribuição) | α = 0,5, ⟨k⟩ = 4 | 1 | **200** | ~7 min |
| E12 | `ba_vs_er.py` | BA + ER | ⟨k⟩ = 2..20 | p₀ = 0,5 | 10 | 1 (×2 redes) | ~6 min |

Custos são de relógio na configuração cheia, medidos a ~17 s por simulação de
10⁶ passos (12 núcleos). E6, E9 e E11 usam `multiprocessing`.

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
> entre todos os modelos **não** vem daqui: vem de E12, que roda BA a p₀ = 0,5
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

Resultado notável: em k = 2 a fração fica exatamente 1,0 para todo p — o anel
trava em cooperação total.

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
`multiprocessing.Pool()` sem argumento: usa todos os núcleos.

Saída: `ws_transiente_k_{k}_p_{p}.csv` (`Tempo_varreduras, Media_Frac_Coop,
Semente_Base`) e uma figura por k com as quatro curvas de p sobrepostas.

### E7 — SBM, varre α com ⟨k⟩ = 4
`src/sbm/sbm_varia_alpha.py`

Quatro blocos de 250 nós. α é a razão entre a probabilidade de ligação **entre**
blocos e **dentro** do bloco: α → 0 são comunidades isoladas, α = 1 é um ER
homogêneo. A parametrização mantém o grau médio constante enquanto α varia:

```
p_intra = 4⟨k⟩ / (N(1 + 3α))        p_inter = α · p_intra
```

Isso é o coração do experimento de SBM: **isolar o efeito da estrutura de
comunidades do efeito do grau médio**. α = 0,1..0,9, uma realização por ponto.

Saída: `sbm_alpha_k_4_1sim.csv` e uma figura de série temporal por α.

### E8 — SBM, mesmo varrimento com ensemble de 20
`src/sbm/sbm_varia_alpha_ensemble.py`

Idêntico a E7, mas 20 realizações independentes por α; a barra de erro passa a
ser σ/√20 **sobre realizações**, não sobre a série. É a versão estatisticamente
defensável de E7. Sequencial (não usa `multiprocessing`), por isso é o segundo
mais caro.

Saída: `sbm_alpha_k_4_20sim.csv` e figura com barras de erro.

### E9 — SBM, α × ⟨k⟩ com ensemble de 25, paralelo
`src/sbm/sbm_varia_alpha_paralelo.py`

O experimento mais caro: E8 repetido para cada ⟨k⟩ = 2, 4, ..., 20. São
10 × 9 × 25 = 2.250 simulações, em `Pool(processes=8)`. Produz a família de
curvas α × ρ, uma por grau médio — a evidência principal de que α não importa e
⟨k⟩ importa.

Saída: `sbm_alpha_k_{k}_25sim.csv` por grau médio (`Alpha, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`) e figura por k. O nome segue o mesmo
padrão de E7 (`_1sim`) e E8 (`_20sim`), então os três varrimentos de α convivem
sem colidir.

### E10 — SBM, varre grau médio com α = 0,5
`src/sbm/sbm_varia_k.py`

O corte ortogonal a E7: α fixo em 0,5, ⟨k⟩ = 2..20, uma realização por ponto. É
a curva de SBM que entra na comparação entre todos os modelos.

Saída: `sbm_grau_medio_alpha_0.5.csv` (`Grau_Medio, Media_Frac_Coop,
Desvio_Padrao_da_Media, Semente_Base`) e figura.

### E11 — SBM, histograma de realizações
`src/sbm/sbm_histograma_alpha.py`

Não varre nada: fixa α = 0,5 e ⟨k⟩ = 4 e roda **200 realizações independentes**
para mostrar a distribuição da média estacionária entre realizações. Responde
"qual é a dispersão real entre realizações", que é justamente o que a barra de
erro σ/√N sobre série não mede.

Saída: `sbm_histograma_alpha_0.5_k_4.csv` (`Realizacao, Media_Frac_Coop,
Semente_Base` — as 200 realizações cruas, para refazer o histograma sem
resimular) e o histograma.

### E12 — BA contra ER no mesmo eixo
`src/comparacoes/ba_vs_er.py`

Roda as duas redes no mesmo laço de ⟨k⟩ = 2..20 (BA com m = ⟨k⟩/2), ambas com
p₀ = 0,5, para a comparação sair sem viés de condição inicial. Note que **E1 usa
p₀ = 0,9 e este usa 0,5** — os dois números de BA não são intercambiáveis.

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

**Nenhum experimento foi regerado ainda com semente.** Tudo que existe em
`resultados/<modelo>/legacy/` veio de antes da padronização da amostragem e da
semeadura: as médias servem como ordem de grandeza, as barras de erro não são
comparáveis entre modelos, e nenhum número pode ser reproduzido. Esses arquivos
estão fora do versionamento (ver [README](README.md#estrutura)).

`resultados/<modelo>/csv/` está vazio à espera da regeração.

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
| E7, E8, E9 | `sbm_alpha_k_{k}_{n}sim.csv` (n = 1, 20, 25) |
| E10 | `sbm_grau_medio_alpha_{alpha}.csv` |
| E11 | `sbm_histograma_alpha_{alpha}_k_{k}.csv` |
| E12 | `ba_vs_er.csv` |

**Renomear foi possível porque os dados antigos saíram do versionamento.** Os
nomes legados existiam para não quebrar a correspondência com CSVs já gerados;
uma vez que esses foram para `legacy/` e tudo será regerado, a compatibilidade
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
   0,5. A curva de BA passou a vir de E12, que roda a p₀ = 0,5.
5. **`SBM_50s_*.csv` dizia 50 realizações e eram 25.** Agora o nome carrega o
   número que o código usa.

### Ainda em aberto

- **E7 e E8 medem a mesma coisa** com 1 e 20 realizações. E7 se sustenta pelas
  figuras de série temporal por α, mas o CSV dele é dominado pelo de E8. Decidir
  se E7 vira só gerador de figuras ou se sai.
- **A dinâmica está copiada em 11 arquivos** (ver [seção 9](#9-onde-mexer-para-estender)).
- **Barras de erro sobre série temporal correlacionada** nos experimentos de uma
  realização só (limitação 6 do README). E8, E9 e E11 não têm esse problema.

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
python src/sbm/sbm_varia_alpha.py --semente 12345
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

Custo total ~3 h de relógio em sequência (3.143 simulações); ~1 h 30 se os sequenciais forem
disparados em paralelo com E9. Os três com `multiprocessing` (E6, E9, E11) não
devem rodar simultaneamente entre si — brigam pelos mesmos núcleos.

Para testar a cadeia inteira em minutos antes de gastar as 3 horas, com saída
redirecionada para não tocar em `resultados/`:

```bash
TCC_VARREDURAS=5 TCC_REGISTROS_TRANSIENTE=5 TCC_RESULTADOS=/tmp/teste python src/erdos_renyi/er_varia_grau_medio.py
```

## 9. Onde mexer para estender

| quero... | mexer em |
|---|---|
| mudar amostragem, transiente, N | `src/comum.py` |
| mudar a semente-base | `src/comum.py`, `SEMENTE_PADRAO` |
| mudar a regra da dinâmica | o bloco `if p1_v == 0:` de **cada** script (está copiado 11 vezes) |
| acrescentar um ponto à varredura | o `for` dentro de `loop()` do script |
| acrescentar uma figura de comparação | `src/comparacoes/gerar_graficos.py`, lista `tarefas` |

A dinâmica estar copiada em 11 arquivos é a dívida técnica mais visível: qualquer
mudança de regra precisa ser replicada, e nada garante que fiquem iguais. Se o
próximo passo for a reescrita para teoria de jogos evolutiva
([README](README.md#próximos-passos)), o natural é extrair a dinâmica para
`comum.py` antes.
