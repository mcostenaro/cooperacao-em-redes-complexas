# Dilema do Prisioneiro em Redes Complexas

Simulações de Monte Carlo de uma dinâmica de cooperação e deserção sobre quatro
modelos de rede: Barabási-Albert, Erdős-Rényi, Watts-Strogatz e Stochastic Block
Model. A pergunta é como a estrutura da rede afeta a fração de cooperadores no
estado estacionário.

Código do meu Trabalho de Conclusão de Curso (2024). A dinâmica é a mesma da
versão apresentada. Em 2026 reorganizei o código, tornei as simulações
reprodutíveis e refiz as barras de erro; os resultados em `resultados/` foram
todos regerados depois disso.

## O modelo

N = 1000 nós, cada um cooperando (C) ou delatando (D), com estado inicial
sorteado com probabilidade p₀ de cooperar. A cada passo sorteia-se um nó e um
vizinho dele, e o par é atualizado:

| par | resultado |
|-----|-----------|
| C, C | continuam C |
| C, D | o cooperador vira D |
| D, D | os dois viram C |

É a regra Win-Stay, Lose-Shift (Pavlov) com o nível de aspiração entre P e R. Na
prática, os dois nós passam a valer `s_i XOR s_j`.

Cada simulação tem 10⁶ passos (1000 varreduras), com a fração de cooperadores
registrada a cada 100 passos. Os primeiros 10% são descartados como transiente.

## Estrutura

```
src/
├── comum.py              # dinâmica, amostragem, sementes, estatística e I/O
├── barabasi_albert/      # varre o grau médio (m = 1..10) e p₀ ∈ {0,1; 0,9}
├── erdos_renyi/          # varre o grau médio (2..20)
├── watts_strogatz/       # varre k, a religação p e o transiente ρ(t)
├── sbm/                  # varre α (força das comunidades) e o grau médio
└── comparacoes/          # BA contra ER, e montagem das figuras finais
resultados/<modelo>/      # csv/ e figuras/ de cada modelo
```

São 11 experimentos, com 256 configurações de parâmetros e 3.134 simulações no
total. Os ensembles usam 20, 25, 30 e 200 realizações independentes; o maior é
o SBM variando α e o grau médio (90 configurações × 25 realizações).

## Como rodar

```bash
pip install -r requirements.txt
python src/erdos_renyi/er_varia_grau_medio.py
python src/comparacoes/gerar_graficos.py   # remonta as figuras a partir dos CSVs
```

Uma simulação leva ~3 s; regerar tudo leva ~35 min numa máquina de 12 núcleos.
Os scripts com `multiprocessing` usam os núcleos disponíveis menos dois
(`TCC_PROCESSOS=N` muda isso sem alterar resultado).

## Reprodutibilidade

Toda a aleatoriedade, inclusive a construção dos grafos, sai de uma semente-base.
Cada ponto de varredura e cada realização têm uma semente derivada dela, e todo
CSV guarda a semente-base na coluna `Semente_Base`. Os resultados versionados
usam 20242025:

```bash
python src/sbm/sbm_varia_k.py --semente 20242025
```

Rodar de novo com a mesma semente produz os mesmos arquivos, byte a byte.
`TCC_RESULTADOS=<pasta>` grava as saídas em outro lugar, útil para comparar com o
que está versionado.

## Barras de erro

Nos experimentos de uma realização, o erro da média vem de blocagem, e não de
σ/√N. Os registros de uma mesma série são muito correlacionados (entre um e
outro mudam no máximo 200 dos 1000 nós), e σ/√N subestimava o erro de 3 a 5
vezes. Nos ensembles o erro é σ/√N sobre as realizações, que são independentes.

## Resultados

- **O grau médio controla o resultado.** Em Erdős-Rényi, ρ cai de 0,797 com
  ⟨k⟩ = 2 para 0,515 ± 0,0007 com ⟨k⟩ = 20. De ⟨k⟩ = 4 em diante, ER, BA, SBM e
  Watts-Strogatz totalmente religado concordam dentro de ~0,01 no mesmo grau
  médio.
- **Comunidades não afetam.** No SBM com grau médio fixo, ρ é plano em α de 0,1 a
  0,9, para todos os graus médios de 2 a 20.
- **A condição inicial é esquecida.** p₀ = 0,1 e p₀ = 0,9 convergem para o mesmo
  valor (≈ 0,52 em BA com ⟨k⟩ = 20) em poucas varreduras.
- **A distribuição de graus tem um efeito pequeno.** De ⟨k⟩ = 8 em diante, BA
  fica 0,003 a 0,008 acima de ER em todos os pontos.
- **Redes regulares de grau baixo são exceção.** Em Watts-Strogatz com k = 2 a
  dinâmica termina com todos cooperando, para qualquer religação. Com k = 6, o
  anel sem religação fica em 0,592 contra 0,560 do totalmente religado.

O campo médio da regra explica o valor em torno de ½: sorteando pares
independentes, `E[Δρ] ∝ 2(1−ρ)(1−2ρ)`, com ponto fixo estável em ρ = ½. A regra
cria correlação entre vizinhos, e essa correlação eleva ρ acima de ½; quanto
maior o grau, mais rápido ela se dilui, e por isso o grau médio é o que manda.

Todos cooperando é um estado absorvente e alcançável de qualquer configuração,
então o platô medido é quase-estacionário. Para ⟨k⟩ ≥ 6 a absorção leva muito
mais que a simulação; em anéis de grau baixo, ela acontece dentro dela.

## Limitações

1. **A matriz de payoff não é usada.** Ganhar ou perder está embutido na regra, e
   não há varredura do parâmetro de tentação, que é o eixo usual na literatura.
2. **O nível de aspiração é implícito.** Com ele entre S e P, o estado todo-D vira
   absorvente e a cooperação desaparece em qualquer rede.
3. **Não há dinâmica evolutiva.** Ninguém imita nem compete; a fração de
   cooperadores mede a fase de um autômato, não o sucesso de uma estratégia. Por
   isso a reciprocidade de rede, que faz a topologia importar nessa literatura,
   está ausente.
4. **Dois pontos de Watts-Strogatz não convergiram.** Com k = 4 e p = 0 o anel é
   absorvido entre ~900 e ~1300 varreduras, então o 0,903 gravado é uma média
   sobre a absorção em andamento. Com p = 0,02 a série ainda sobe no fim
   (0,717 no CSV, ~0,735 com 5000 varreduras).
5. **Uma realização não mede a variação entre redes.** Em grau baixo, redes
   sorteadas com os mesmos parâmetros diferem mais do que a barra de erro de uma
   delas: ~0,005 em ⟨k⟩ = 4, contra ~0,001 da barra. De ⟨k⟩ = 8 em diante as duas
   coincidem.
6. `ba_prototipo_com_score.py` acumula pontuação, mas os dois ramos da comparação
   são idênticos, então roda a mesma dinâmica dos demais.

## Próximos passos

Reescrever a dinâmica como jogo evolutivo, mantendo as mesmas redes: cada nó
joga com todos os vizinhos, acumula payoff e imita um vizinho com a regra de
Fermi, `P(i copia j) = 1 / (1 + exp[(Π_i − Π_j)/K])`, varrendo o parâmetro de
tentação e com ensembles de realizações desde o início.

## Nomes originais dos scripts

| Original | Atual |
|----------|-------|
| `Dilema_barabasi.py` | `src/barabasi_albert/ba_varia_grau_medio.py` |
| `Dilema_prisioneiro.py` | `src/barabasi_albert/ba_prototipo_com_score.py` |
| `Dilema_Erdos.py` | `src/erdos_renyi/er_varia_grau_medio.py` |
| `Dilema_WS_k_varia.py` | `src/watts_strogatz/ws_varia_k.py` |
| `Dilema_WS_p_varia.py` | `src/watts_strogatz/ws_varia_p.py` |
| `DIlema_WS_P_transicao.py` | `src/watts_strogatz/ws_transiente.py` |
| `Dilema_SBM_alpha_varias_sim.py` | `src/sbm/sbm_varia_alpha_ensemble.py` |
| `Dilema_SBM_k_varia.py` | `src/sbm/sbm_varia_k.py` |
| `teste_paral.py` | `src/sbm/sbm_varia_alpha_paralelo.py` |
| `SBM_teste_alpha.py` | `src/sbm/sbm_histograma_alpha.py` |
| `Dilema_varios_modelos.py` | `src/comparacoes/ba_vs_er.py` |
| `graficos_dilema.py` | `src/comparacoes/gerar_graficos.py` |

## Referências

- Nowak, M. & Sigmund, K. (1993). *A strategy of win-stay, lose-shift that
  outperforms tit-for-tat in the Prisoner's Dilemma game*. Nature 364, 56–58.
- Nowak, M. & May, R. (1992). *Evolutionary games and spatial chaos*. Nature 359, 826–829.
- Szabó, G. & Fáth, G. (2007). *Evolutionary games on graphs*. Physics Reports 446, 97–216.
