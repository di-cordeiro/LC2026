# TP1.1 Gerador de Horário Escolar

Gerador de horário semanal de turmas em Marimo, modelado como CSP com dados lidos de CSV.

- Notebook principal: [horario_escolar.py](horario_escolar.py)
- Dados: `dados/` (iniciais) e `dados_v2/` (alterados, para o cenário incremental)

## Executar
``` bash
cd TP1/Ex1_horario
marimo edit horario_escolar.py    # para trabalhar
marimo run horario_escolar.py     # para ver como aplicação
```

## Requisitos


| Req | O que exige | Feito | Testado |
|---|---|:---:|:---:|
| R1 | Turma sem duas aulas em simultâneo | x | x |
| R2 | Carga semanal exata por disciplina e turma | x | x |
| R3 | No máximo uma aula da disciplina por dia e turma (bloco duplo conta como uma) | x | x |
| R4 | Duplo período: 2 tempos consecutivos, no mesmo dia | x | x |
| R5 | Professor sem duas aulas em simultâneo | x | x |
| R6 | Professor só dá aulas quando está disponível | x | x |
| R7 | Sala do tipo certo e sem exceder a quantidade por tipo | x | x |
| R8 | Dados sempre lidos dos CSV, nada escrito no código | x | x |
| R9 | `H1` a partir de `H0`: mais rápido do que do zero e com poucas aulas alteradas | x | x |
| O1 | Minimizar buracos dos professores (ótimo não obrigatório) | x | x |


## Plano de Trabalho 

**1. Dados**
- [x] Ler os 4 CSV e validar o formato
- [ ] Escolher a pasta (`dados/` ou `dados_v2/`) sem mexer no código

**2. Modelo base (R1-R7)**
- [x] Variáveis e restrições no CP-SAT
- [x] Blocos duplos e salas especiais
- [x] Primeiro horário válido `H0`

**3. Validador independente**
- [x] Função que confirma R1-R8 sobre um horário já gerado
- [x] Um caso de teste por restrição
- [x] Teste com um conjunto de dados diferente do fornecido

**4. Objetivo (O1)**
- [x] Definir o que é um buraco e a função objetivo
- [x] Limite de tempo do solver

**5. Construção incremental (R9)**
- [x] `H1` a partir de `H0` com `dados_v2/`
- [x] Comparar `H1` do zero vs incremental: tempo e nº de aulas alteradas
- [x] Tratar outras alterações: disponibilidade, sala avariada, turma nova, professor substituído

**6. Apresentação e entrega**
- [ ] Horário numa grelha semanal por turma
- [ ] Notebook a correr de ponta a ponta sem erros
- [ ] Partes geradas por LLM marcadas nos comentários
- [ ] Link da conversa com o LLM no relatório
- [ ] PDF exportado
- [ ] Repositório público e e-mail enviado até às 23:59 de 6 de outubro

**Bónus (opcional)**
- [ ] Preferências dos professores na função objetivo
- [ ] Escala: mais turmas e professores, e limites encontrados

## Decisões a justificar na discussão oral

- Técnica de modelação e biblioteca: _
- Leitura e representação dos dados: _
- Definição de buraco e função objetivo: _
- Abordagem incremental (o que se fixa, o que se reotimiza): _
- Como medi tempo e aulas alteradas: _

## Estado atual
