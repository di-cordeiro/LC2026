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
    4. Um professor não dá aulas nos tempos em que está indisponível.
    5. Em cada tempo, o número de aulas num tipo de sala $s$ não excede a quantidade de salas $Q_s$.

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
    return dados, pd


@app.cell
def _(dados):
    from ortools.sat.python import cp_model

    T = dados["turmas"]["turma"].tolist()
    D = dados["disciplinas"]["disciplina"].tolist()
    I = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    H = range(1, 6)

    horario = cp_model.CpModel()

    x = {
        (t, d, i, h): horario.NewBoolVar(f"x_{t}_{d}_{i}_{h}")
           for t in T for d in D for i in I for h in H
        }
    return D, H, I, T, cp_model, horario, x


@app.cell
def _(dados, pd):
    # Dados auxiliares para restrições
    dupla = dict(zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["duplo_periodo"] == "sim"))
    professor = dict(zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["professor"]))
    P = sorted(set(professor.values()))
    indisponivel = set(zip(dados["disponibilidade"]["professor"], dados["disponibilidade"]["dia"], dados["disponibilidade"]["periodo"]))
    quantidade_salas = dict(zip(dados["salas"]["sala"], dados["salas"]["quantidade"]))
    sala_normal = dados["salas"].loc[dados["salas"]["tipo"] == "normal", "sala"].iloc[0]
    sala = {d: (sala_normal if pd.isna(esp) else esp)
           for d, esp in zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["sala_especial"])
           }
    carga = dict(zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["carga_semanal"]))
    return P, carga, dupla, indisponivel, professor, quantidade_salas, sala


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


@app.cell
def _(D, H, I, T, horario, x):
    def restricao_sem_aulas_simultaneo():
        for t in T:
            for i in I:
                for h in H:
                    horario.Add(sum(x[(t,d,i,h)] for d in D) <= 1)

    return (restricao_sem_aulas_simultaneo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2. Em cada dia, uma turma tem no máximo uma aula de cada disciplina sem duplo período, e no máximo um bloco de dois tempos de cada disciplina com duplo período. Divide-se em duas expressões, as com duplo período e as que não têm.

    As sem duplo período pode expressar-se da seguinte forma:

    $$\forall_{i<I} \cdot \forall_{t<T} \cdot \forall_{d<D,\;duplo(d)=\text{não}} \quad \sum_{h<H} x_{t,d,i,h} \leq 1$$

    As com duplo período pode expressar-se da seguinte forma:
    $$\forall_{i<I} \cdot \forall_{t<T} \cdot \forall_{d<D,\;duplo(d)=\text{sim}} \cdot \forall_{h,k<H,\;k>h+1} \quad x_{t,d,i,h}+x_{t,d,i,k}\leq1$$
    """)
    return


@app.cell
def _(D, H, I, T, dupla, horario, x):
    def restricao_sem_duplo_periodo():
        for i in I:
            for t in T:
                for d in D:
                    if not dupla[d]:
                        horario.Add(sum(x[(t, d, i, h)] for h in H) <= 1)

    return (restricao_sem_duplo_periodo,)


@app.cell
def _(D, H, I, T, dupla, horario, x):
    def restricao_com_duplo_periodo():
        for i in I:
            for t in T:
                for d in D:
                    if dupla[d]:
                        for h1 in H:
                            for h2 in H:
                                if h2 > h1 + 1:
                                    horario.Add(x[(t, d, i, h1)] + x[(t, d, i, h2)] <= 1)

    return (restricao_com_duplo_periodo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    3. Em cada tempo, um professor tem no máximo uma aula, somando todas as suas disciplinas e turmas

    pode expressar-se da seguinte forma:

    $$\forall_{p<P} \cdot \forall_{i<I} \cdot \forall_{h<H} \cdot \quad \sum_{t<T}\ \sum_{d<D,\;p(d)=p} x_{t,d,i,h} \leq 1$$
    """)
    return


@app.cell
def _(D, H, I, P, T, horario, professor, x):
    def restricao_professor_maximo_uma_aula_por_tempo():
        for p in P:
            for i in I:
                for h in H:
                    horario.Add(sum(x[(t,d,i,h)] for t in T for d in D if professor[d] == p) <= 1)

    return (restricao_professor_maximo_uma_aula_por_tempo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    4. Um professor não dá aulas nos tempos em que está indisponível

    pode expressar-se da seguinte forma:

    $$\forall_{t< T} \cdot \forall_{d< D} \cdot \forall_{i< I} \cdot \forall_{h< H,\;(p(d),i,h\in Ind)} \quad x_{t,d,i,h} = 0$$
    """)
    return


@app.cell
def _(D, H, I, T, horario, indisponivel, professor, x):
    def restricao_professor_indisponivel():
        for t in T:
            for d in D:
                for i in I:
                    for h in H:
                        if(professor[d],i,h) in indisponivel:
                            horario.Add(x[(t,d,i,h)] == 0)

    return (restricao_professor_indisponivel,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    5. Em cada tempo, o número de aulas num tipo de sala $s$ não excede a quantidade de salas $Q_s$

    pode expressar-se da seguinte forma:
    $$\forall_{s<S} \cdot \forall_{i<I} \cdot \forall_{h<H} \cdot \quad \sum_{t<T}\ \sum_{d<D,\;s(d)=s} x_{t,d,i,h} \leq Q_s$$
    """)
    return


@app.cell
def _(D, H, I, T, horario, quantidade_salas, sala, x):
    def restricao_salas():
        for s in quantidade_salas:
            for i in I:
                for h in H:
                    horario.Add(sum(x[(t,d,i,h)] for t in T for d in D if sala[d] == s) <= quantidade_salas[s])

    return (restricao_salas,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    6. Cada turma tem exatamente $c(d)$ tempos semanais de cada disciplina $d$

    pode expressar-se da seguinte forma:

    $$\forall_{t< T} \cdot \forall_{d<D} \cdot \quad \sum_{i<I}\ \sum_{h<H} x_{t,d,i,h} = c(d)$$
    """)
    return


@app.cell
def _(D, H, I, T, carga, horario, x):
    def restricao_carga_semanal():
        for t in T:
            for d in D: 
                horario.Add(sum(x[(t,d,i,h)] for i in I for h in H) == int(carga[d]))

    return (restricao_carga_semanal,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    7. As disciplinas de duplo período só podem ser dadas em blocos de dois tempos consecutivos, no mesmo dia

    pode expressar-se da seguinte forma:

    $$\forall_{t<T} \cdot \forall_{d<D,\;duplo(d)=\text{sim}} \cdot \forall_{i<I} \cdot \forall_{h<H} \cdot \quad x_{t,d,i,h} \leq x_{t,d,i,h-1} + x_{t,d,i,h+1}$$
    """)
    return


@app.cell
def _(D, H, I, T, dupla, horario, x):
    def restricao_blocos_consecutivos():
        for t in T:
            for d in D:
                if dupla[d]:
                    for i in I:
                        for h in H:
                            viz = [x[(t,d,i,k)] for k in (h-1, h+1) if k in H]
                            horario.Add(x[(t,d,i,h)] <= sum(viz))

    return (restricao_blocos_consecutivos,)


@app.cell
def _(
    horario,
    restricao_blocos_consecutivos,
    restricao_carga_semanal,
    restricao_com_duplo_periodo,
    restricao_professor_indisponivel,
    restricao_professor_maximo_uma_aula_por_tempo,
    restricao_salas,
    restricao_sem_aulas_simultaneo,
    restricao_sem_duplo_periodo,
):
    def contar(f):
        antes = len(horario.Proto().constraints)
        f()
        print(f.__name__, len(horario.Proto().constraints) - antes)

    contar(restricao_sem_aulas_simultaneo)
    contar(restricao_sem_duplo_periodo)
    contar(restricao_com_duplo_periodo)
    contar(restricao_professor_maximo_uma_aula_por_tempo)
    contar(restricao_professor_indisponivel)
    contar(restricao_salas)
    contar(restricao_carga_semanal)
    contar(restricao_blocos_consecutivos)
    return


@app.cell
def _(cp_model, horario):
    solver = cp_model.CpSolver()
    estado = solver.Solve(horario)
    print("Estado:", solver.StatusName(estado))
    print("Nº de restrições:", len(horario.Proto().constraints))
    return (solver,)


@app.cell
def _(D, H, I, T, solver, x):
    for t in T:
        print(t)
        for h in H:
            linha = []
            for i in I:
                aula = [d for d in D if solver.Value(x[(t, d, i, h)]) == 1]
                linha.append(aula[0] if aula else "-")
            print(f"{h}º tempo:", " | ".join(f"{a:<16}" for a in linha))
        print()
    return


if __name__ == "__main__":
    app.run()
