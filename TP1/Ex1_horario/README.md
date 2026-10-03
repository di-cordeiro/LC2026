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
| R1 | Turma sem duas aulas em simultâneo | ☐ | ☐ |
| R2 | Carga semanal exata por disciplina e turma | ☐ | ☐ |
| R3 | No máximo uma aula da disciplina por dia e turma (bloco duplo conta como uma) | ☐ | ☐ |
| R4 | Duplo período: 2 tempos consecutivos, no mesmo dia | ☐ | ☐ |
| R5 | Professor sem duas aulas em simultâneo | ☐ | ☐ |
| R6 | Professor só dá aulas quando está disponível | ☐ | ☐ |
| R7 | Sala do tipo certo e sem exceder a quantidade por tipo | ☐ | ☐ |
| R8 | Dados sempre lidos dos CSV, nada escrito no código | ☐ | ☐ |
| R9 | `H1` a partir de `H0`: mais rápido do que do zero e com poucas aulas alteradas | ☐ | ☐ |
| O1 | Minimizar buracos dos professores (ótimo não obrigatório) | ☐ | ☐ |


## Plano de Trabalho 

**1. Dados**
- [x] Ler os 4 CSV e validar o formato
- [ ] Escolher a pasta (`dados/` ou `dados_v2/`) sem mexer no código

**2. Modelo base (R1-R7)**
- [x] Variáveis e restrições no CP-SAT
- [x] Blocos duplos e salas especiais
- [x] Primeiro horário válido `H0`

**3. Validador independente**
- [ ] Função que confirma R1-R8 sobre um horário já gerado
- [ ] Um caso de teste por restrição
- [ ] Teste com um conjunto de dados diferente do fornecido

**4. Objetivo (O1)**
- [ ] Definir o que é um buraco e a função objetivo
- [ ] Limite de tempo do solver

**5. Construção incremental (R9)**
- [ ] `H1` a partir de `H0` com `dados_v2/`
- [ ] Comparar `H1` do zero vs incremental: tempo e nº de aulas alteradas
- [ ] Tratar outras alterações: disponibilidade, sala avariada, turma nova, professor substituído

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
