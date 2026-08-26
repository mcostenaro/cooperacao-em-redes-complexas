# O que a dinâmica faz

Análise do mecanismo por trás dos resultados. O [README](README.md) descreve o
modelo e o [PROTOCOLO](PROTOCOLO.md) inventaria os experimentos; aqui está a
leitura física: **por que** os números saem como saem.

As medições deste documento vêm dos CSVs em `resultados/`, gerados com a
semente-base padrão. Onde há medida feita fora dos experimentos (correlação
entre vizinhos, decomposição por componente), está dito no texto — são
realizações únicas e carregam ruído.

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

Daí a conclusão central do trabalho — *o parâmetro de controle é o grau médio,
não a topologia* — ganhar mecanismo: **a topologia só consegue entrar pela
correlação local do par sorteado, e é o grau médio que a governa.** Uma regra que
olha apenas os rótulos de dois nós adjacentes não tem como enxergar comprimento
de caminho, clusterização ou estrutura de comunidades.

A evidência direta são três topologias sem nada em comum, no mesmo grau médio:

| ⟨k⟩ | ER | SBM α=0,5 | WS p=1 | espalhamento | erro típico |
|---|---|---|---|---|---|
| 2 | 0,797 | 0,811 | 1,000 | 0,203 | 0,0022 |
| 4 | 0,626 | 0,626 | 0,617 | 0,009 | 0,0011 |
| 8 | 0,546 | 0,547 | 0,541 | 0,006 | 0,0008 |
| 14 | 0,522 | 0,522 | 0,522 | 0,000 | 0,0007 |
| 20 | 0,515 | 0,513 | 0,515 | 0,002 | 0,0007 |

De ⟨k⟩ = 8 em diante as três concordam na terceira casa. O grau médio explica
~30% de variação; a topologia, menos de 1%.

## 5. O extremo: quando o estado absorvente vence

Em ⟨k⟩ = 2 o espalhamento explode, porque o Watts-Strogatz **trava em ρ = 1**.
Medido: o anel k = 2 chega a cooperação total em ~26 varreduras e fica.

O mecanismo é coalescência. Com grau 2 a rede é localmente unidimensional; a
homogeneização de par cria domínios, os domínios coalescem, e como D,D → C,C o
domínio de C é o único absorvente. Em 1D esse processo completa.

E é sobre **grau**, não sobre o anel: com religação total (p = 1) o k = 2
continua dando 1,0, porque um grafo 2-regular aleatório ainda é uma união de
ciclos — continua unidimensional.

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

| ⟨k⟩ | p₀ = 0,1 | p₀ = 0,9 | diferença | erro típico |
|---|---|---|---|---|
| 2 | 0,827 | 0,815 | **+0,012** | 0,0024 |
| 4 | 0,617 | 0,617 | +0,000 | 0,0011 |
| 10 | 0,538 | 0,538 | +0,000 | 0,0007 |
| 20 | 0,519 | 0,517 | +0,002 | 0,0007 |

De ⟨k⟩ = 4 em diante a diferença é do tamanho da barra de erro: a memória de p₀ é
apagada por completo. Em ⟨k⟩ = 2 sobra um resíduo de +0,012, cinco vezes a barra
— e o mecanismo prevê exatamente isso: em grau baixo há nós fracamente acoplados
(folhas, que interagem sempre com o mesmo vizinho) e componentes absorvidas, e é
aí que a condição inicial consegue sobreviver.

### E2 — protótipo com score
Não mede fenômeno nenhum. Os dois ramos do `if` de comparação de score são
logicamente idênticos, então roda a mesma dinâmica de E1. Vale como registro da
tentativa de usar matriz de payoff — e como ponto de partida para a reescrita
evolutiva, já que a estrutura de acumular payoff já está lá.

### E3 — ER, varre ⟨k⟩
A curva de decaimento da correlação, medida na rede sem estrutura nenhuma. É a
referência contra a qual o desvio das outras topologias é medido — e acima de
⟨k⟩ = 6 não há desvio apreciável.

### E4 — WS, varre k com p de religação fixo
Onde o estado absorvente aparece limpo: k = 2 dá 1,0; k = 4 dá ~0,98 (quase
absorve); de k = 6 em diante entra no regime de campo médio. Mapeia a transição
entre "coalescência 1D vence" e "mistura vence".

### E5 — WS, varre p com k fixo
Testa a transição small-world. A previsão do mecanismo é que **p não faça quase
nada**, porque religar não muda o grau — e é o que se observa, inclusive k = 2
permanecendo em 1,0 para todo p. Resultado negativo informativo: comprimento de
caminho e clusterização são invisíveis para essa regra.

### E6 — WS, transiente
Mede o tempo de relaxação. Há dois regimes qualitativamente distintos, e as
curvas não têm a mesma forma: em k = 2 é coalescência até a absorção (~26
varreduras), em k ≥ 6 é relaxação para ½.

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
O controle que fecha o argumento: reproduz a curva do ER dentro de 0,006 acima de
⟨k⟩ = 8, com barras de ~0,0008.

### E10 — SBM, histograma de 200 realizações
Mede a dispersão real entre realizações independentes — a única coisa que uma
barra de erro sobre série temporal não alcança. Depois da troca para blocagem,
serve também de validação externa dela: a largura do histograma e a barra por
blocagem devem ser da mesma ordem.

### E11 — BA contra ER, mesmo ⟨k⟩
Testa heterogeneidade de grau. E aqui aparece o único efeito de topologia
estatisticamente real do conjunto:

| ⟨k⟩ | BA | ER | BA − ER | erro típico |
|---|---|---|---|---|
| 2 | 0,829 | 0,797 | **+0,032** | 0,0027 |
| 4 | 0,617 | 0,628 | −0,011 | 0,0010 |
| 10 | 0,540 | 0,532 | +0,008 | 0,0008 |
| 20 | 0,518 | 0,514 | +0,004 | 0,0008 |

Acima de ⟨k⟩ = 8 o BA fica sistematicamente ~0,004 a 0,008 acima do ER — pequeno,
mas de 5 a 10 vezes a barra de erro, e com sinal consistente em cinco pontos
seguidos. Coerente com o mecanismo: BA tem cauda de nós de grau baixo (folhas)
que se mantêm correlacionadas com seu único vizinho, e é a correlação média da
população que fixa ρ. Ou seja, **o que importa não é só o grau médio, é a
distribuição de graus** — mas o efeito é de ~1%, contra ~30% do grau médio.

Este é o tipo de conclusão que só se pode afirmar com barra de erro honesta e com
semente registrada: são 4 σ, não ruído, e qualquer um pode regerar o número.

---

## 7. O que isso implica

1. **A conclusão do TCC se sustenta e ganha mecanismo.** "O grau médio é o
   parâmetro de controle" deixa de ser observação empírica e passa a ter uma
   causa: o grau médio é a taxa de descorrelação, e a regra só enxerga
   correlação de vizinhança.
2. **O resultado "topologia não importa" é uma propriedade da regra, não da
   física da cooperação.** Reciprocidade de rede — o mecanismo pelo qual a
   topologia importa nessa literatura — exige payoff somado sobre toda a
   vizinhança e imitação baseada nele. Nenhum dos dois existe aqui, então a
   ausência do efeito era esperada.
3. **Há um efeito de topologia de ~1%**, na distribuição de graus (E11), visível
   agora que as barras de erro são honestas.
4. **O caminho natural** é dar à dinâmica os ingredientes que faltam — payoff
   somado sobre a vizinhança e atualização por imitação — mantendo as mesmas
   quatro famílias de rede, para comparação direta. Ver
   [Próximos passos](README.md#próximos-passos).

## Como refazer as medidas deste documento

As tabelas das seções 4, 6 saem direto dos CSVs de `resultados/`. As das seções
3 e 5 (correlação entre vizinhos, decomposição por componente) não têm script
próprio no repositório — foram medidas com `comum.evoluir` seguido de inspeção
do estado final de `G`, que fica com o `value` de cada nó ao fim da simulação.
