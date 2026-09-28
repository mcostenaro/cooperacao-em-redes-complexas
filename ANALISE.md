# O que a dinâmica faz

Análise do mecanismo por trás dos resultados. O [README](README.md) descreve o
modelo e o [PROTOCOLO](PROTOCOLO.md) inventaria os experimentos; aqui está a
leitura física: **por que** os números saem como saem.

As medições deste documento vêm dos CSVs em `resultados/`, gerados com a
semente-base padrão. Onde há medida feita fora dos experimentos (correlação
entre vizinhos, decomposição por componente, simulações longas, tempos de
absorção), está dito no texto — são realizações únicas ou poucas sementes e
carregam ruído.

**Sobre as barras de erro.** Nos experimentos de uma realização, a barra mede a
flutuação temporal de *uma* rede sorteada, não a variação de uma rede para
outra. De ⟨k⟩ = 8 em diante as duas coincidem (~0,001); em grau baixo a
variação entre redes é maior — ~0,015 em ⟨k⟩ = 2, ~0,005 em 4, ~0,002 em 6,
medida pelos ensembles do SBM (E8, E10). Diferenças entre redes distintas em
⟨k⟩ ≤ 6 são julgadas contra esse espalhamento, não contra a barra.

---

## 0. Antes de tudo: não há dinâmica evolutiva aqui

Vale abrir com isso porque o vocabulário do trabalho — "fração de cooperadores",
"dilema do prisioneiro" — sugere teoria de jogos evolutiva, e o que o código faz
é outra coisa.

Numa dinâmica evolutiva, agentes acumulam payoff jogando com a vizinhança e
**imitam** quem se saiu melhor: a estratégia se propaga por seleção. Aqui não há
seleção, nem imitação, nem reprodução. Todo nó é um autômato fixo, e a matriz de
payoff nunca é consultada — `calc_score` existe em `ba_prototipo_com_score.py`
mas seus dois ramos são logicamente idênticos.

O que se mede é a **fase estacionária de um autômato celular estocástico**. Isso
não invalida resultado nenhum, mas muda o que ele significa: "fração de
cooperadores" aqui é o estado de equilíbrio de uma regra de atualização, não o
sucesso evolutivo de uma estratégia. Ver
[Limitações conhecidas](README.md#limitações-conhecidas).

## 1. A regra tem um caso, não três

Escrita como está no código, a regra parece ter três ramos. Ela tem um:

> os dois nós sorteados passam a valer `s_i XOR s_j`

| par | XOR | resultado |
|---|---|---|
| C, C | 0 | ambos C |
| C, D | 1 | ambos D |
| D, D | 0 | ambos C |

Em **todos** os casos o par termina com os dois nós no mesmo estado. A regra é
uma **homogeneização de par**, com um viés: par discordante vira D, par de D
vira C. Duas consequências saem daí, e elas explicam o resto do documento.

## 2. Consequência I — o ponto fixo de campo médio é ½

Se o par sorteado fosse estatisticamente independente, cada nó sendo C com
probabilidade ρ, o balanço por passo seria:

| par | probabilidade | Δ (nº de cooperadores) |
|---|---|---|
| C,C | ρ² | 0 |
| C,D ou D,C | 2ρ(1−ρ) | −1 |
| D,D | (1−ρ)² | +2 |

**E[Δ] = −2ρ(1−ρ) + 2(1−ρ)² = 2(1−ρ)(1−2ρ)**

Zera em dois pontos:

- **ρ = ½**, estável — acima dele o drift é negativo, abaixo é positivo;
- **ρ = 1**, **absorvente** — se todos cooperam, todo par é C,C e nada mais muda.

O drift perto de ρ = 1 aponta para baixo, então o estado absorvente não é
atingido por deriva. Só por coalescência local, que é o assunto da seção 5.

**Mas ele é sempre alcançável.** Qualquer nó D com pelo menos um vizinho vira C
em no máximo duas atualizações da mesma aresta — D,D → C,C direto, ou C,D →
D,D → C,C — sem mexer em nenhum outro nó. Aplicando isso nó a nó, todos-C se
alcança a partir de qualquer estado. Numa rede finita, então, a cadeia de
Markov termina em todos-C com probabilidade 1 (fora os nós isolados, que
nunca mudam).

O platô perto de ½ que os experimentos medem é portanto **quase-estacionário**:
um estado de vida longa, não o estado final. Quanto tempo ele dura depende da
rede. Em redes de grau baixo e sem hubs a absorção cabe na simulação (seção 5).
Nos casos testados com 5000 varreduras em vez de 1000 — ER e BA com ⟨k⟩ = 4,
WS k = 4 com p = 0,2 e 1, anel com k = 6 — não há sinal de deriva. É o platô, e
não a absorção, que o trabalho mede.

## 3. Consequência II — a regra destrói a própria premissa

O campo médio supõe vizinhos descorrelacionados. Mas a regra **iguala pares**:
ela fabrica correlação entre vizinhos a cada passo. Correlação positiva
superrepresenta os pares D,D, que são justamente os que produzem +2. O balanço
se equilibra então num ρ **acima** de ½.

Medido em ER, amostrando o par exatamente como a dinâmica o sorteia (nó
uniforme, depois vizinho uniforme):

| ⟨k⟩ | ρ | correlação entre vizinhos | balanço (q_CD+q_DC) / 2q_DD |
|---|---|---|---|
| 2 | 0,829 | 0,40 | 1,14 |
| 4 | 0,630 | 0,20 | 0,99 |
| 6 | 0,571 | 0,08 | 1,10 |
| 20 | 0,499 | 0,01 | 0,97 |
| 40 | 0,507 | −0,00 | 1,03 |

*(realização única, 300 varreduras — os valores intermediários têm ruído
apreciável; a tendência é o que importa)*

A última coluna é o teste de estacionariedade: a condição de equilíbrio é
exatamente `q_CD + q_DC = 2·q_DD`, ou seja, essa razão valer 1. Vale, em todos os
graus. A coluna do meio é a explicação: **ρ − ½ acompanha a correlação entre
vizinhos, e as duas vão a zero juntas.**

## 4. O que ⟨k⟩ controla de fato

Não é "quanta cooperação a rede sustenta". É **com que rapidez a correlação
criada pela regra é destruída**.

Um nó de grau 2 interage sempre com os mesmos dois parceiros: o que a regra
correlaciona permanece correlacionado. Um nó de grau 40 é pareado com um vizinho
diferente a cada encontro, e a memória do último se dilui. Grau alto reconstrói a
hipótese de campo médio, e o sistema entrega ρ = ½.

Daí a conclusão central do trabalho — *o parâmetro de controle é o grau médio* —
ganhar mecanismo: **a topologia só consegue entrar pela correlação local do par
sorteado, e em redes aleatórias é o grau médio que a governa.** Uma regra que
olha apenas os rótulos de dois nós adjacentes não enxerga comprimento de caminho
nem estrutura de comunidades. Estrutura *local* ela enxerga, sim, quando essa
estrutura segura a correlação — ver o anel regular, abaixo.

A evidência direta são três topologias aleatórias sem nada em comum, no mesmo
grau médio:

| ⟨k⟩ | ER | SBM α=0,5 | WS p=1 | espalhamento | erro típico |
|---|---|---|---|---|---|
| 2 | 0,797 | 0,811 | 1,000 | 0,203 | 0,0022 |
| 4 | 0,626 | 0,626 | 0,617 | 0,009 | 0,0011 |
| 8 | 0,546 | 0,547 | 0,541 | 0,006 | 0,0008 |
| 14 | 0,522 | 0,522 | 0,522 | 0,000 | 0,0007 |
| 20 | 0,515 | 0,513 | 0,515 | 0,002 | 0,0007 |

De ⟨k⟩ = 8 em diante as três concordam na terceira casa. Em ⟨k⟩ = 4 o
espalhamento de 0,009 está dentro da variação entre redes nesse grau (~0,005 por
rede — ver a nota no topo). O grau médio move ρ em ~0,3; entre redes
aleatórias, a topologia move menos de 0,01 a partir de ⟨k⟩ = 4. Em ⟨k⟩ = 2 o
WS religado se separa das outras — seção 5.

**A exceção: a rede regular.** O anel do Watts-Strogatz (p = 0) contra o mesmo
anel totalmente religado (p = 1), mesmo k:

| k | anel (p = 0) | religado (p = 1) | diferença |
|---|---|---|---|
| 4 | 1,0 no longo prazo (absorve) | 0,617 | — |
| 6 | 0,591 | 0,562 | +0,029 |
| 10 | 0,536 | 0,531 | +0,005 |
| 20 | 0,515 | 0,515 | 0,000 |

*(k = 4, p = 0: o CSV tem 0,903 porque a absorção acontece entre ~900 e ~1300
varreduras, na borda das 1000 simuladas — seção 5.)*

Com k = 6 a diferença é ~30 vezes a barra e ~10 vezes a variação entre redes
nesse grau. A leitura coerente com a seção 3: no anel, os vizinhos de um nó são
vizinhos entre si, então a correlação que a regra cria num par se espalha para
parceiros compartilhados e demora mais a se diluir. A religação destrói isso.
O efeito some quando o grau cresce, como a correlação da seção 3.
O grau médio continua sendo a variável dominante, mas **não a única**: em grau
baixo, a regularidade da rede conta.

## 5. O extremo: quando o estado absorvente vence

Em ⟨k⟩ = 2 o espalhamento explode, porque o Watts-Strogatz **trava em ρ = 1**.
Como a seção 2 mostrou, todos-C é sempre alcançável; aqui ele é alcançado
depressa. Tempos de absorção medidos (três sementes cada, 5000 varreduras):

| rede | absorve em (varreduras) |
|---|---|
| anel, k = 2 | 19, 24, 24 |
| WS k = 2 religado (p = 1) | 35, 35, 58 |
| anel, k = 4 | 923, 1189, 1317 |

O mecanismo é coalescência. No anel k = 2 a rede é unidimensional; a
homogeneização de par cria domínios, os domínios coalescem, e como D,D → C,C o
domínio de C é o único absorvente. Em 1D esse processo completa. No anel k = 4
ele também completa, só que ~50 vezes mais devagar — e por isso o ponto k = 4,
p = 0 de E4 saiu no meio da absorção.

O WS k = 2 religado **não** é 2-regular. No gerador do networkx cada nó religa a
própria aresta e continua com ela, então o grafo tem N arestas para N nós: cada
componente tem **exatamente um ciclo**, com árvores penduradas, e os graus vão de
1 a 6 ou 7. Continua absorvendo. Mas "poucos ciclos" não basta como explicação:
o BA com m = 1 é uma árvore (nenhum ciclo) e fica em 0,83 sem absorver. O que o
separa do WS religado, pelo que se mediu, são os hubs — grau máximo 57 contra 6.
Um hub é pareado com muitos vizinhos diferentes, e isso dilui a correlação como
grau alto dilui (seção 4). É a explicação consistente com o resto do documento,
mas não foi testada à parte.

No ER com ⟨k⟩ = 2 o mesmo efeito aparece parcialmente. Decompondo o estado final
por tipo de componente:

| | nós | ρ |
|---|---|---|
| isolados (grau 0) | 115 | 0,461 — congelados na condição inicial |
| componentes pequenas | 47 | **1,000** — todas absorvidas |
| componente gigante | 838 | 0,802 — correlação alta, mas não absorve |

Uma componente pequena sempre termina cooperando. Um par isolado, por exemplo:
C,D → D,D → C,C → fim. *(realização única, 200 varreduras)*

Note que a fragmentação **não** é a explicação principal nem em ⟨k⟩ = 2: a
componente gigante sozinha já está em 0,80. O efeito dominante é a correlação da
seção 3; a absorção das componentes pequenas é um acréscimo.

---

## 6. Experimento por experimento

Numeração do [PROTOCOLO](PROTOCOLO.md#4-mapa-dos-experimentos).

### E1 — BA, varre ⟨k⟩ com p₀ ∈ {0,1; 0,9}
Testa se o atrator apaga a condição inicial. O drift 2(1−ρ)(1−2ρ) empurra para ½
vindo de qualquer lado, então as duas curvas deveriam colapsar. Colapsam:

| ⟨k⟩ | p₀ = 0,1 | p₀ = 0,9 | diferença | barra | variação entre redes |
|---|---|---|---|---|---|
| 2 | 0,827 | 0,815 | +0,012 | 0,0024 | ~0,015 |
| 4 | 0,617 | 0,617 | +0,000 | 0,0011 | ~0,005 |
| 10 | 0,538 | 0,538 | +0,000 | 0,0007 | ~0,001 |
| 20 | 0,519 | 0,517 | +0,002 | 0,0007 | ~0,001 |

Cada p₀ roda sobre uma rede sorteada diferente, então a diferença entre as duas
colunas se julga contra a variação entre redes, não contra a barra. Assim
julgada, ela é compatível com zero em todos os graus: em ⟨k⟩ = 2 o +0,012 é
maior que a barra, mas menor que o espalhamento de uma rede para outra nesse
grau. **A memória de p₀ é apagada** dentro do que o experimento consegue
resolver. Para afirmar um resíduo em grau baixo seria preciso rodar os dois p₀
sobre as mesmas redes, ou um ensemble.

### E2 — protótipo com score
Não mede fenômeno nenhum. Os dois ramos do `if` de comparação de score são
logicamente idênticos, então roda a mesma dinâmica de E1. Vale como registro da
tentativa de usar matriz de payoff — e como ponto de partida para a reescrita
evolutiva, já que a estrutura de acumular payoff já está lá.

### E3 — ER, varre ⟨k⟩
A curva de decaimento da correlação, medida na rede sem estrutura nenhuma. É a
referência contra a qual o desvio das outras topologias é medido — e, entre as
redes aleatórias, de ⟨k⟩ = 4 em diante o desvio fica abaixo de 0,01.

### E4 — WS, varre k com p de religação fixo
Onde o estado absorvente aparece limpo: k = 2 dá 1,0 para todo p. Em k = 4 o
resultado depende de p: o anel (p = 0) absorve no longo prazo — o CSV tem 0,903
porque a absorção acontece entre ~900 e ~1300 varreduras —, com p = 0,02 a
série ainda sobe no fim da janela (0,717 no CSV, ~0,735 em 5000 varreduras), e
com p ≥ 0,2 o platô é estável entre 0,62 e 0,64. De k = 6 em diante não há
absorção, mas o anel fica acima do religado até k ≈ 10 (seção 4). Mapeia a
transição entre "coalescência vence" e "mistura vence", e ela depende tanto de
k quanto de p.

### E5 — WS, varre p com k fixo
Testa a transição small-world. O resultado depende do grau:

| k | p = 0 | p = 0,1 | p = 1 |
|---|---|---|---|
| 2 | 1,000 | 1,000 | 1,000 |
| 6 | 0,592 | 0,570 | 0,560 |
| 10 | 0,536 | 0,535 | 0,531 |

Em k = 2 tudo absorve, qualquer p. Em k = 6 a religação **importa**: ρ cai
0,032, e a maior parte da queda acontece já em p = 0,1 — é a destruição da
estrutura local do anel (seção 4). Em k = 10 o efeito é de 0,005, pequeno mas
~6 vezes a barra. O comprimento de caminho, que despenca já com p pequeno, não
aparece como variável própria; a estrutura local do anel aparece, e some
quando o grau cresce.

### E6 — WS, transiente
Mede o tempo de relaxação. Há dois regimes qualitativamente distintos, e as
curvas não têm a mesma forma: em k = 2 é coalescência até a absorção (~20 a
25 varreduras no anel), em k ≥ 6 é relaxação rápida para o platô. A figura de
comparação mostra k = 10, onde as quatro curvas de p se sobrepõem.

### E7 e E8 — SBM, varre α
O experimento mais bem desenhado do conjunto. α muda a estrutura de comunidades
**mantendo ⟨k⟩ fixo**:

```
p_intra = 4⟨k⟩ / (N(1 + 3α))        p_inter = α · p_intra
```

Isso isola exatamente a variável que os outros experimentos não isolam. A
previsão do mecanismo é curva plana em α, porque comunidade é estrutura
mesoscópica e a regra só enxerga o vizinho imediato. É o que se observa. E8
repete para dez graus médios — é a evidência principal de que ⟨k⟩ manda e α não.

### E9 — SBM, varre ⟨k⟩ com α = 0,5
O controle que fecha o argumento: reproduz a curva do ER dentro de 0,002 de
⟨k⟩ = 8 em diante, com barras de ~0,0007.

### E10 — SBM, histograma de 200 realizações
Mede a dispersão real entre realizações independentes — a única coisa que uma
barra de erro sobre série temporal não alcança. E mostra que, em ⟨k⟩ = 4, ela é
grande: as 200 médias se espalham com σ = 0,0051, contra 0,0011 da barra por
blocagem de uma realização. A blocagem não está errada — mede a flutuação
temporal de uma rede, e isso ela acerta. A diferença é a variação de uma rede
sorteada para outra, que uma única série não tem como ver. É daqui (e de E8) que
sai a nota sobre barras de erro no topo deste documento.

### E11 — BA contra ER, mesmo ⟨k⟩
Testa heterogeneidade de grau. Aqui aparece, entre redes aleatórias, o efeito
de topologia estatisticamente sustentado do conjunto:

| ⟨k⟩ | BA | ER | BA − ER | incerteza da diferença |
|---|---|---|---|---|
| 2 | 0,829 | 0,797 | +0,032 | ~0,02 |
| 4 | 0,617 | 0,628 | −0,011 | ~0,007 |
| 8 | 0,551 | 0,545 | +0,006 | ~0,002 |
| 10 | 0,540 | 0,532 | +0,008 | ~0,0014 |
| 20 | 0,518 | 0,514 | +0,004 | ~0,001 |

*(incerteza da diferença: √2 × a variação entre redes naquele grau — ver a nota
no topo. É maior que a barra de cada ponto em ⟨k⟩ ≤ 6.)*

Em ⟨k⟩ = 2 e 4 as diferenças, de sinais opostos, estão dentro de ~1,5 vez a
incerteza: não sustentam conclusão. De ⟨k⟩ = 8 em diante o BA fica acima do ER
em **todos os sete pontos**, por +0,0025 a +0,008 — cada um de 2 a 6 vezes a
incerteza, e o sinal constante torna o conjunto muito improvável como ruído.
Coerente com o mecanismo: BA tem cauda de nós de grau baixo (folhas) que se
mantêm correlacionadas com seu único vizinho, e é a correlação média da
população que fixa ρ. Ou seja, **o que importa não é só o grau médio, é a
distribuição de graus** — mas o efeito é de ~0,005, contra ~0,3 do grau médio.

Este é o tipo de conclusão que só se pode afirmar com barra de erro honesta e com
semente registrada: qualquer um pode regerar o número. O passo seguinte para
fechá-la é um ensemble de BA e ER, em vez de uma rede de cada.

---

## 7. O que isso implica

1. **A conclusão do TCC se sustenta, com escopo, e ganha mecanismo.** "O grau
   médio é o parâmetro de controle" vale entre redes aleatórias e deixa de ser
   observação empírica: o grau médio é a taxa de descorrelação, e a regra só
   enxerga correlação de vizinhança.
2. **A topologia importa pouco, e só onde segura correlação local.** O anel
   regular com k ≤ 6 fica acima das redes aleatórias, e com k ≤ 4 é absorvido;
   comunidades (α) e comprimento de caminho não aparecem. Que o efeito seja
   pequeno é propriedade da regra, não da física da cooperação: reciprocidade
   de rede — o mecanismo pelo qual a topologia importa nessa literatura — exige
   payoff somado sobre toda a vizinhança e imitação baseada nele. Nenhum dos
   dois existe aqui.
3. **Há um efeito da distribuição de graus de ~0,005** (BA > ER, E11), visível
   de ⟨k⟩ = 8 em diante agora que as barras de erro são honestas.
4. **O que se mede é um platô quase-estacionário.** Todos-C é absorvente e
   sempre alcançável (seção 2). Para os resultados principais isso não muda
   nada, porque a absorção leva muito mais que a simulação; mas em redes
   regulares de grau baixo ela acontece dentro da janela, e o ponto k = 4,
   p = 0 do WS saiu no meio dela.
5. **O caminho natural** é dar à dinâmica os ingredientes que faltam — payoff
   somado sobre a vizinhança e atualização por imitação — mantendo as mesmas
   quatro famílias de rede, para comparação direta. Ver
   [Próximos passos](README.md#próximos-passos).

## Como refazer as medidas deste documento

As tabelas das seções 4 e 6 saem direto dos CSVs de `resultados/`; a variação
entre redes sai dos ensembles de E8 (erro × √25) e de E10. As medidas das seções
2, 3 e 5 (correlação entre vizinhos, decomposição por componente, simulações de
5000 varreduras, tempos de absorção, graus e ciclos dos grafos) não têm script
próprio no repositório — foram feitas com `comum.evoluir` (com
`comum.VARREDURAS` aumentado quando preciso) e inspeção do grafo e do estado
final de `G`, que fica com o `value` de cada nó ao fim da simulação.
