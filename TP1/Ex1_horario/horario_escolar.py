import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Horário escolar
    Uma escola tem um conjunto de turmas ($T$), de disciplinas ($D$), de professores ($P$), com a respetiva disponibilidade, e de tipos de sala ($S$), normais e especiais, em número limitado. O horário semanal tem 5 dias, cada um com 5 tempos. Pretende-se gerar automaticamente o horário semanal de cada turma.
    Cada disciplina $d$ tem um professor $p(d)$, uma carga semanal $c(d)$, um indicador de duplo período e um tipo de sala $s(d)$. Cada tipo de sala $s$ tem $Q_s$ salas disponíveis em simultâneo, e cada professor tem alguns tempos indisponíveis. Todos estes valores são lidos dos ficheiros CSV.

    ### Regras
    - Uma turma não pode ter duas aulas em simultâneo.
    - Cada disciplina cumpre exatamente a carga semanal exigida para cada turma.
    - No máximo, só pode haver uma aula da mesma disciplina por dia e por turma. As disciplinas de duplo período têm de ser dadas em blocos de dois tempos consecutivos, no mesmo dia, e cada bloco conta como uma só aula.
    - Um professor não pode dar duas aulas em simultâneo, mesmo que sejam a turmas ou disciplinas diferentes.
    - Um professor só pode dar aulas nos tempos em que está disponível.
    - Cada aula ocupa uma sala. Disciplinas com `sala_especial` só podem usar salas desse tipo; as restantes usam salas `normal`. Em nenhum tempo o número de aulas a decorrer num tipo de sala pode exceder a `quantidade` desse tipo definida em `salas.csv`.

    ### Objetivo
    O número total de "buracos" no horário de cada professor deve ser minimizado. Um buraco é um tempo livre, no meio do dia, entre a primeira e a última aula desse professor nesse dia.

    ### Construção incremental
    Quando os recursos mudam ligeiramente, o horário deve ser reajustado sem recomeçar do zero e alterando o menor número possível de aulas.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Análise do problema

    Este é um problema de alocação. Pretende-se alocar aulas (disciplinas de cada turma) aos tempos da semana, respeitando a disponibilidade dos professores e as salas existentes.

    Existem $T$ turmas, que podemos identificar por um índice $t \in [0..T\!-\!1]$, e $D$ disciplinas, identificadas por $d \in [0..D\!-\!1]$. Cada tempo da semana é identificado por um par $(i,h) \in [0..4]\times[0..4]$, em que $i$ é o dia e $h$ o tempo desse dia.

    Vamos usar uma família $x_{t,d,i,h}$ de variáveis binárias, com a seguinte semântica

    $$x_{t,d,i,h} == 1  \quad \mbox{se e só se} \quad \mbox{a turma $t$ tiver a disciplina $d$ no dia $i$, ao tempo $h$.}$$

    Estas $T\times D\times 5\times 5$ variáveis são convenientemente representadas numa matriz $X$ instanciável com valores $\{0,1\}^{T\times D\times 5\times 5}$, a que se costuma chamar *matriz de alocação*.

    O professor e o tipo de sala de cada disciplina são dados do problema, e não variáveis de decisão. Por isso não fazem parte do índice de $x$ e só aparecem nas restrições, através de $p(d)$ e $s(d)$.

    Destaca-se ainda o seguinte:

    **Limitações** (que impõem limites máximos à alocação)


    1. Uma turma não tem duas aulas em simultâneo.
    2. Em cada dia, uma turma tem no máximo uma aula de cada disciplina sem duplo período, e no máximo um bloco de dois tempos de cada disciplina com duplo período.
    3. Em cada tempo, um professor tem no máximo uma aula, somando todas as suas disciplinas e turmas.
    5. Um professor não dá aulas nos tempos em que está indisponível.
    6. Em cada tempo, o número de aulas num tipo de sala $s$ não excede $Q_s$.

    **Obrigações** (que impõem limites mínimos à alocação)

    6. Cada turma tem exatamente $c(d)$ tempos semanais de cada disciplina $d$.
    7. As disciplinas de duplo período só podem ser dadas em blocos de dois tempos consecutivos, no mesmo dia.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Implementação
    Começamos por importar o CP-SAT do OR-TOOLS e criar o modelo 'modelo'.

    Depois obtemos os conjuntos $T$ (turmas) e $D$ (disciplinas) a partir dos dados lidos dos ficheiros CSV, e definimos a estrutura da semana: 5 dias com 5 tempos cada.

    Em seguida, declaramos a matriz de alocação $X$ como um dicionário de variáveis booleanas $x_{t,d,i,h}$.
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    import pandas as pd
    from pathlib import Path

    def ler_dados(pasta):
        pasta = Path(pasta)
        return {
            "disciplinas": pd.read_csv(pasta / "disciplinas.csv"),
            "disponibilidade": pd.read_csv(pasta / "disponibilidade_excecoes.csv"),
            "salas": pd.read_csv(pasta / "salas.csv"),
            "turmas": pd.read_csv(pasta / "turmas.csv")
        }

    dados = ler_dados("dados")
    mo.vstack([dados["disciplinas"], dados["disponibilidade"], dados["salas"], dados["turmas"]])
    return (dados,)


@app.cell
def _(dados):
    from ortools.sat.python import cp_model

    turmas = dados["turmas"]["turma"].tolist()
    disciplinas = dados["disciplinas"]["disciplina"].tolist()
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    tempos = range(1, 6)

    modelo = cp_model.CpModel()

    x = {
        (t, d, i, h): modelo.NewBoolVar(f"x_{t}_{d}_{i}_{h}")
           for t in turmas for d in disciplinas for i in dias for h in tempos
        }
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Passamos agora à modelação das restrições.

    A restrição:
    1. Uma turma não tem duas aulas em simultâneo

    pode expressar-se da seguinte forma:

    $$\forall_{t< T} \cdot \forall_{i< I} \cdot \forall_{h< H} \cdot \quad \sum_{d< D} x_{t,d,i,h} \leq 1$$
    """)
    return


if __name__ == "__main__":
    app.run()
