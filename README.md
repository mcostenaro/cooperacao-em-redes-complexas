# Dilema do Prisioneiro em Redes Complexas

Simulações de Monte Carlo de uma dinâmica de cooperação/deserção sobre quatro
modelos de rede — Barabási-Albert, Erdős-Rényi, Watts-Strogatz e Stochastic
Block Model — investigando como a topologia afeta a fração estacionária de
cooperadores.

Código do meu Trabalho de Conclusão de Curso (2024). Este repositório contém a
**versão apresentada**, reorganizada mas com a dinâmica original preservada.
As limitações do modelo estão documentadas em [Limitações conhecidas](#limitações-conhecidas).

---

## Estrutura

```
src/
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
│   ├── sbm_varia_alpha.py          # varre α (1 realização por ponto)
│   ├── sbm_varia_alpha_ensemble.py # idem, 20 realizações
│   ├── sbm_varia_alpha_paralelo.py # idem, 25 realizações, multiprocessing
│   ├── sbm_varia_k.py              # α fixo, varre ⟨k⟩
│   └── sbm_histograma_alpha.py     # histograma de 200 realizações, α fixo
├── comparacoes/
│   ├── ba_vs_er.py                 # BA e ER no mesmo gráfico
│   └── gerar_graficos.py           # lê os CSVs e monta as figuras
└── nucleos.py                      # utilitário: imprime os.cpu_count()

resultados/
├── <modelo>/csv/                   # saídas numéricas
├── <modelo>/figuras/               # PNGs
└── _orfaos/                        # dados sem script correspondente
```

Em `watts_strogatz/` há um par de subpastas `media_30_simulacoes/` (em `csv/` e
em `figuras/`) com resultados promediados sobre 30 realizações, gerados por uma
versão anterior dos scripts de WS. A nomenclatura ali é a antiga
(`Dilema_WA_results_*`, `WA_transiente_p_*_k_*`) e não corresponde à saída atual.

Cada script resolve seus diretórios de saída a partir da raiz do repositório
(`Path(__file__).resolve().parents[2]`), então pode ser executado de qualquer
diretório.

## Como rodar

```bash
pip install -r requirements.txt
```

```bash
python src/erdos_renyi/er_varia_grau_medio.py
```

Os scripts de simulação levam de minutos a horas (10⁶ passos por ponto da
varredura). Os que usam `multiprocessing` assumem ~8 núcleos; ajuste
`processes=` conforme sua máquina (`python src/nucleos.py` mostra quantos você tem).

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
o desvio padrão da média da fração de cooperadores no estado estacionário.

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

6. **Barras de erro subestimadas.** O desvio padrão da média é calculado como
   `σ/√N` sobre uma série temporal correlacionada, tratando amostras dependentes
   como independentes.

### Pontos menores

- `ba_prototipo_com_score.py`: os dois ramos do `if` de comparação de score são
  logicamente idênticos, então a pontuação acumulada não influencia nada. O
  script roda a mesma dinâmica dos demais.
- `gerar_graficos.py`: `comparar_graficos_p0` e `comparar_WA_transiente`
  desempacotam 2 valores de `read_csv`, que retorna 3 — levantam `ValueError`.
  Ficaram desatualizadas quando a coluna de desvio foi adicionada.
- A unidade de tempo não é uniforme: `ba_varia_grau_medio.py` registra a cada
  100 passos (0,1 varredura) enquanto os demais registram a cada 1000 (1 varredura).
  O tamanho do transiente descartado também varia entre scripts.
- `resultados/_orfaos/Dilema_LFR_results.csv` tem valores entre 2,9 e 5,3, fora
  do intervalo [0,1] de uma fração. Nenhum script atual gera LFR — provável erro
  de normalização em código perdido.
- `sbm_varia_alpha.py` e `sbm_varia_alpha_ensemble.py` gravavam no mesmo arquivo
  e se sobrescreviam. Agora escrevem `sbm_alpha_k_{k}_1sim.csv` e
  `sbm_alpha_k_{k}_20sim.csv`. Os CSVs históricos `Dilema_SBM_results_k_*.csv`
  vieram de um dos dois, sem registro de qual.
- Prefixo `WA_` nos arquivos de Watts-Strogatz é typo herdado de `WS_`,
  preservado para não quebrar a correspondência com os dados já gerados.

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

## Próximos passos

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
