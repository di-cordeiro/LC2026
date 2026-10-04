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
    import time

    return mo, time


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
    pasta_dados = "dados" # posso por "dados", "dados_v2" ou "dados_teste"
    dados = ler_dados(pasta_dados)
    mo.vstack([dados["disciplinas"], dados["disponibilidade"], dados["salas"], dados["turmas"]])
    return Path, dados, ler_dados, pd


@app.cell
def _(pd):
    def lista_de_dados(dados):
        disc = dados["disciplinas"]
        sala_normal = dados["salas"].loc[dados["salas"]["tipo"] == "normal", "sala"].iloc[0]
        return {
            "T": dados["turmas"]["turma"].tolist(),
            "D": disc["disciplina"].tolist(),
            "I": ["Seg", "Ter", "Qua", "Qui", "Sex"],
            "H": range(1, 6),
            "professor": dict(zip(disc["disciplina"], disc["professor"])),
            "dupla": dict(zip(disc["disciplina"], disc["duplo_periodo"] == "sim")),
            "carga": dict(zip(disc["disciplina"], disc["carga_semanal"].astype(int))),
            "sala": {d: (sala_normal if pd.isna(e) else e)
                     for d, e in zip(disc["disciplina"], disc["sala_especial"])},
            "quantidade_salas": dict(zip(dados["salas"]["sala"], dados["salas"]["quantidade"])),
            "indisponivel": set(zip(dados["disponibilidade"]["professor"], dados["disponibilidade"]["dia"],dados["disponibilidade"]["periodo"])),
        }

    return (lista_de_dados,)


@app.cell
def _():
    from ortools.sat.python import cp_model

    horario = cp_model.CpModel()
    return (cp_model,)


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


@app.function
def restricao_sem_aulas_simultaneo(modelo,x,p):
    for t in p["T"]:
        for i in p["I"]:
            for h in p["H"]:
                modelo.Add(sum(x[(t,d,i,h)] for d in p["D"]) <= 1)


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


@app.function
def restricao_sem_duplo_periodo(modelo,x,p):
    for i in p["I"]:
        for t in p["T"]:
            for d in p["D"]:
                if not p["dupla"][d]:
                    modelo.Add(sum(x[(t, d, i, h)] for h in p["H"]) <= 1)


@app.function
def restricao_com_duplo_periodo(modelo,x,p):
    for i in p["I"]:
        for t in p["T"]:
            for d in p["D"]:
                if p["dupla"][d]:
                    for h1 in p["H"]:
                        for h2 in p["H"]:
                            if h2 > h1 + 1:
                                modelo.Add(x[(t, d, i, h1)] + x[(t, d, i, h2)] <= 1)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    3. Em cada tempo, um professor tem no máximo uma aula, somando todas as suas disciplinas e turmas

    pode expressar-se da seguinte forma:

    $$\forall_{p<P} \cdot \forall_{i<I} \cdot \forall_{h<H} \cdot \quad \sum_{t<T}\ \sum_{d<D,\;p(d)=p} x_{t,d,i,h} \leq 1$$
    """)
    return


@app.function
def restricao_professor_maximo_uma_aula_por_tempo(modelo,x,p):
    for prof in sorted(set(p["professor"].values())):
        for i in p["I"]:
            for h in p["H"]:
                modelo.Add(sum(x[(t,d,i,h)] for t in p["T"] for d in p["D"] if p["professor"][d] == prof) <= 1)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    4. Um professor não dá aulas nos tempos em que está indisponível

    pode expressar-se da seguinte forma:

    $$\forall_{t< T} \cdot \forall_{d< D} \cdot \forall_{i< I} \cdot \forall_{h< H,\;(p(d),i,h\in Ind)} \quad x_{t,d,i,h} = 0$$
    """)
    return


@app.function
def restricao_professor_indisponivel(modelo,x,p):
    for t in p["T"]:
        for d in p["D"]:
            for i in p["I"]:
                for h in p["H"]:
                    if(p["professor"][d],i,h) in p["indisponivel"]:
                        modelo.Add(x[(t,d,i,h)] == 0)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    5. Em cada tempo, o número de aulas num tipo de sala $s$ não excede a quantidade de salas $Q_s$

    pode expressar-se da seguinte forma:
    $$\forall_{s<S} \cdot \forall_{i<I} \cdot \forall_{h<H} \cdot \quad \sum_{t<T}\ \sum_{d<D,\;s(d)=s} x_{t,d,i,h} \leq Q_s$$
    """)
    return


@app.function
def restricao_salas(modelo,x,p):
    for s in p["quantidade_salas"]:
        for i in p["I"]:
            for h in p["H"]:
                modelo.Add(sum(x[(t,d,i,h)] for t in p["T"] for d in p["D"] if p["sala"][d] == s) <= p["quantidade_salas"][s])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    6. Cada turma tem exatamente $c(d)$ tempos semanais de cada disciplina $d$

    pode expressar-se da seguinte forma:

    $$\forall_{t< T} \cdot \forall_{d<D} \cdot \quad \sum_{i<I}\ \sum_{h<H} x_{t,d,i,h} = c(d)$$
    """)
    return


@app.function
def restricao_carga_semanal(modelo,x,p):
    for t in p["T"]:
        for d in p["D"]: 
            modelo.Add(sum(x[(t,d,i,h)] for i in p["I"] for h in p["H"]) == int(p["carga"][d]))


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    7. As disciplinas de duplo período só podem ser dadas em blocos de dois tempos consecutivos, no mesmo dia

    pode expressar-se da seguinte forma:

    $$\forall_{t<T} \cdot \forall_{d<D,\;duplo(d)=\text{sim}} \cdot \forall_{i<I} \cdot \forall_{h<H} \cdot \quad x_{t,d,i,h} \leq x_{t,d,i,h-1} + x_{t,d,i,h+1}$$
    """)
    return


@app.function
def restricao_blocos_consecutivos(modelo,x,p):
    for t in p["T"]:
        for d in p["D"]:
            if p["dupla"][d]:
                for i in p["I"]:
                    for h in p["H"]:
                        viz = [x[(t,d,i,k)] for k in (h-1, h+1) if k in p["H"]]
                        modelo.Add(x[(t,d,i,h)] <= sum(viz))


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Validação do Horário

    O solver devolve sempre um horário que cumpre o modelo que lhe demos, mas isso não garante que o modelo esteja bem escrito: uma restrição esquecida ou mal formulada passa despercebida. Por isso escrevemos um **validador independente**, `verificar`, que recebe os dados e um horário já gerado e confirma, regra a regra, que o horário cumpre o enunciado.

    O validador não usa o modelo CP-SAT nem as suas variáveis: relê os dados dos ficheiros CSV e recalcula tudo a partir do próprio horário. Devolve a lista de violações encontradas, e uma lista vazia significa que o horário é válido.

    #### Testes do validador

    Um validador que nunca falha não prova nada. Por isso, para cada requisito, partimos de um horário válido, introduzimos de propósito uma violação desse requisito e confirmamos que `verificar` a deteta. Confirmamos também que o horário gerado pelo solver não tem nenhuma violação.

    #### Dados diferentes

    Para mostrar que nada está escrito diretamente no código (R8), repetimos o fluxo completo com um conjunto de dados diferente, em `dados_teste/`, com uma turma e uma disciplina a mais e outra exceção de disponibilidade. Só muda o nome da pasta lida.
    """)
    return


@app.cell
def _verificar(pd):
    def verificar(dados, sol):
        erros = []
        T = dados["turmas"]["turma"].tolist()
        D = dados["disciplinas"]["disciplina"].tolist()
        I = ["Seg", "Ter", "Qua", "Qui", "Sex"]
        H = range(1, 6)
        carga = dict(zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["carga_semanal"]))
        dupla = {d: (v == "sim") for d, v in zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["duplo_periodo"])}
        professor = dict(zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["professor"]))
        P = sorted(set(professor.values()))
        indisponivel = set(zip(dados["disponibilidade"]["professor"], dados["disponibilidade"]["dia"], dados["disponibilidade"]["periodo"]))
        quantidade_salas = dict(zip(dados["salas"]["sala"], dados["salas"]["quantidade"]))
        sala_normal = dados["salas"].loc[dados["salas"]["tipo"] == "normal", "sala"].iloc[0]
        sala = {d: (sala_normal if pd.isna(esp) else esp)
                for d, esp in zip(dados["disciplinas"]["disciplina"], dados["disciplinas"]["sala_especial"])
               }

        # R1: turma sem duas aulas em simultâneo
        for t in T:
            for i in I:
                for h in H:
                    if sum(sol[(t, d, i, h)] for d in D) > 1:
                        erros.append(("R1", t, i, h))

        # R2: carga semanal exata
        for t in T:
            for d in D: 
                total = sum(sol[(t,d,i,h)] for i in I for h in H) 
                if total != int(carga[d]):
                    erros.append(("R2", t, d, total, int(carga[d])))

        # R3: disciplinas sem duplo período
        for i in I:
            for t in T:
                for d in D:
                    if not dupla[d]:
                        if (sum(sol[(t, d, i, h)] for h in H) > 1):
                            erros.append(("R3", i, t, d))

        # R4: disciplinas de duplo período
        for i in I:
            for t in T:
                for d in D:
                    if dupla[d]:
                        ocupados = [h for h in H if sol[(t, d, i, h)] == 1]
                        valido = len(ocupados) == 0 or (len(ocupados) == 2 and ocupados[1] == ocupados[0] + 1)
                        if not valido:
                            erros.append(("R4", i, t, d, ocupados))

        # R5: no máximo uma aula por tempo por professor
        for p in P:
            for i in I:
                for h in H:
                    if (sum(sol[(t,d,i,h)] for t in T for d in D if professor[d] == p) > 1):
                        erros.append(("R5", p, i, h))

        # R6: nenhuma aula do professor quando está indisponível
        for t in T:
            for d in D:
                for i in I:
                    for h in H:
                        if(professor[d],i,h) in indisponivel and (sol[(t,d,i,h)] == 1):
                            erros.append(("R6", t, d, i, h))

        # R7: o número de aulas num tipo de sala não excede a quantidade de salas
        for s in quantidade_salas:
            for i in I:
                for h in H:
                    if (sum(sol[(t,d,i,h)] for t in T for d in D if sala[d] == s) > quantidade_salas[s]):
                        erros.append(("R7", s, i, h))

        return erros


    return (verificar,)


@app.cell
def _(dados, sol, verificar):
    verificar(dados, sol)
    return


@app.cell
def _(dados, sol, verificar):
    def test_horario_valido():
        assert verificar(dados, sol) == []


    def test_R1():
        mal = dict(sol)
        mal[("7ºA", "Matemática", "Seg", 1)] = 1
        mal[("7ºA", "Português", "Seg", 1)] = 1
        assert any(e[0] == "R1" for e in verificar(dados, mal))

    def test_R2():
        mal = dict(sol)
        for i in ["Seg", "Ter", "Qua", "Qui", "Sex"]:
            for h in range(1, 6):
                mal[("7ºA", "Matemática", i, h)] = 0
        assert any(e[0] == "R2" for e in verificar(dados, mal))

    def test_R3():
        mal = dict(sol)
        mal[("7ºA", "Matemática", "Seg", 1)] = 1
        mal[("7ºA", "Matemática", "Seg", 2)] = 1
        assert any(e[0] == "R3" for e in verificar(dados, mal))

    def test_R4():
        mal = dict(sol)
        for h in range(1, 6):
            mal[("7ºA", "Educação Física", "Seg", h)] = 0
            mal[("7ºA", "Educação Física", "Seg", 4)] = 1 
        assert any(e[0] == "R4" for e in verificar(dados, mal))

    def test_R5():
        mal = dict(sol)
        mal[("7ºA", "Matemática", "Seg", 1)] = 1
        mal[("7ºB", "Matemática", "Seg", 1)] = 1
        assert any(e[0] == "R5" for e in verificar(dados, mal))

    def test_R6():
        mal = dict(sol)
        mal[("7ºA", "Educação Física", "Seg", 1)] = 1
        assert any(e[0] == "R6" for e in verificar(dados, mal))

    def test_R7():
        mal = dict(sol)
        mal[("7ºA", "Ciências", "Seg", 1)] = 1
        mal[("7ºB", "Ciências", "Seg", 1)] = 1
        assert any(e[0] == "R7" for e in verificar(dados, mal))


    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Objetivo: minimizar o buraco dos professores

    Um **buraco** é um tempo livre de um professor, no meio do dia, com pelo menos uma aula antes e uma aula depois. Os tempos livres no início ou no fim do dia não contam.

    Para os contar dentro do modelo, introduzimos três famílias de variáveis binárias, para cada professor $p$, dia $i$ e tempo $h$:

    - $a_{p,i,h}$ vale 1 se o professor $p$ tem aula no tempo $h$ no dia $i$;
    - $m_{p,i,h}$ vale 1 se o professor {p} tem uma aula num tempo anterior a {h}, nesse dia;
    - $n_{p,i,h}$ vale 1 se o professor {p} tem uma aula num tempo posterior a {h}, nesse dia.

    O valor de $a$ obtém-se somando as aulas de todas as disciplinas do professor, em todas as turmas:

    $$a_{p,i,h} = \sum_{t<T}\ \sum_{d<D,\;p(d)=p} x_{t,d,i,h}$$

    As variáveis $m$ e $n$ ficam limitadas inferiormente pelos tempos em causa:

    $$\forall_{k<h} \cdot m_{p,i,h} \geq a_{p,i,k} \qquad\qquad\forall_{k>h} \cdot n_{p,i,h} \geq a_{p,i,k}$$

    Basta o limite inferior: se houver aula antes, $m$ é forçada a 1, e o solver nunca ganha em pô-la a 1 sem necessidade, porque isso só pode aumentar os buracos.

    Introduzimos ainda uma variável binária $b_{p,i,h}$ por tempo, que indica um buraco. Há buraco quando existe aula antes, existe aula depois e não existe aula no próprio tempo:

    $$b_{p,i,h} \geq m_{p,i,h} + n_{p,i,h} - a_{p,i,h} - 1$$

    Quando as três condições se verificam, o lado direito vale 1 e $b$ é forçada a 1. Nos outros casos vale 0 ou menos, e $b$ pode ser 0. Em particular, um dia sem aulas do professor não conta buracos.

    O objetivo é minimizar o número total de buracos:

    $$\min \sum_{p<P}\ \sum_{i<I}\ \sum_{h<H} b_{p,i,h}$$

    Esta função objetivo não altera as restrições: apenas escolhe, entre os horários válidos, os que têm menos buracos. Por isso o horário continua a passar no validador.

    **Verificação independente.** Para confirmar o resultado sem usar o modelo, a função `contar_buracos` percorre o horário já gerado e, para cada professor e dia, calcula o intervalo entre a primeira e a última aula menos o número de aulas.
    """)
    return


@app.function
def menos_buracos(modelo,x,p, extra=0):
    buracos = []
    for prof in sorted(set(p["professor"].values())):
        for i in p["I"]:
            a = {}
            for h in p["H"]:
                a[h] = modelo.NewBoolVar(f"a_{prof}_{i}_{h}")
                modelo.Add(a[h] == sum(x[(t, d, i, h)] for t in p["T"] for d in p["D"] if p["professor"][d] == prof))
            for h in p["H"]:
                antes = modelo.NewBoolVar(f"antes_{prof}_{i}_{h}")
                depois = modelo.NewBoolVar(f"depois_{prof}_{i}_{h}")
                for k in p["H"]:
                    if k < h:
                        modelo.Add(antes >= a[k])
                    if k > h:
                        modelo.Add(depois >= a[k])
                b = modelo.NewBoolVar(f"b_{prof}_{i}_{h}")
                modelo.Add(b >= depois + antes - a[h] - 1)
                buracos.append(b)
    modelo.Minimize(sum(buracos) + extra)


@app.cell
def _(dados, lista_de_dados, sol):
    def contar_buracos(sol, p):
        total = 0
        for prof in set(p["professor"].values()):
            for i in p["I"]:
                ocupados = [h for h in p["H"] if sum(sol[(t, d, i, h)] for t in p["T"] for d in p["D"]
                                                      if p["professor"][d] == prof) > 0]
                if ocupados:
                    total += (max(ocupados) - min(ocupados) + 1) - len(ocupados)
        return total

    contar_buracos(sol, lista_de_dados(dados))
    return (contar_buracos,)


@app.cell
def _(cp_model, lista_de_dados):
    def construir_modelo(dados, com_objetivo = True):
        p = lista_de_dados(dados)
        modelo = cp_model.CpModel()
        x = {(t, d, i, h): modelo.NewBoolVar(f"x_{t}_{d}_{i}_{h}")
             for t in p["T"] for d in p["D"] for i in p["I"] for h in p["H"]}

        restricao_sem_aulas_simultaneo(modelo, x, p)
        restricao_sem_duplo_periodo(modelo, x, p)
        restricao_com_duplo_periodo(modelo, x, p)
        restricao_professor_maximo_uma_aula_por_tempo(modelo, x, p)
        restricao_professor_indisponivel(modelo, x, p)
        restricao_salas(modelo, x, p)
        restricao_carga_semanal(modelo, x, p)
        restricao_blocos_consecutivos(modelo, x, p)

        if com_objetivo:
            menos_buracos(modelo, x, p)
        return modelo, x

    return (construir_modelo,)


@app.cell
def _(cp_model):
    def resolver(modelo, x, tempo_max=None):
        solver = cp_model.CpSolver()
        if tempo_max:
            solver.parameters.max_time_in_seconds = tempo_max
        estado = solver.Solve(modelo)
        if solver.StatusName(estado) not in ("OPTIMAL", "FEASIBLE"):
            return None
        return {chave: solver.Value(var) for chave, var in x.items()}

    return (resolver,)


@app.function
def contar(f, modelo, x, p):
    antes = len(modelo.Proto().constraints)
    f(modelo, x, p)
    print(f.__name__, len(modelo.Proto().constraints) - antes)


@app.cell
def _(cp_model, dados, lista_de_dados):
    def modelo_vazio(dados):
        p = lista_de_dados(dados)
        modelo = cp_model.CpModel()
        x = {(t, d, i, h): modelo.NewBoolVar(f"x_{t}_{d}_{i}_{h}")
             for t in p["T"] for d in p["D"] for i in p["I"] for h in p["H"]}
        return modelo, x, p

    _modelo, _x, _p = modelo_vazio(dados)
    contar(restricao_sem_aulas_simultaneo, _modelo, _x, _p)
    contar(restricao_sem_duplo_periodo, _modelo, _x, _p)
    contar(restricao_com_duplo_periodo, _modelo, _x, _p)
    contar(restricao_professor_maximo_uma_aula_por_tempo, _modelo, _x, _p)
    contar(restricao_professor_indisponivel, _modelo, _x, _p)
    contar(restricao_salas, _modelo, _x, _p)
    contar(restricao_carga_semanal, _modelo, _x, _p)
    contar(restricao_blocos_consecutivos, _modelo, _x, _p)
    return


@app.cell
def _(construir_modelo, dados, resolver):
    modelo, x = construir_modelo(dados)
    sol = resolver(modelo, x)
    print("Nº de restrições:", len(modelo.Proto().constraints))
    return (sol,)


@app.cell
def _(
    construir_modelo,
    contar_buracos,
    dados,
    lista_de_dados,
    resolver,
    sol,
    verificar,
):
    _p = lista_de_dados(dados)

    _m1, _x1 = construir_modelo(dados, com_objetivo=False)
    _sol1 = resolver(_m1, _x1)
    print("Sem objetivo:", contar_buracos(_sol1, _p), "buracos")

    _m2, _x2 = construir_modelo(dados, com_objetivo=True)
    _sol2 = resolver(_m2, _x2)
    print("Com objetivo:", contar_buracos(_sol2, _p), "buracos")
    print("Horário válido:", verificar(dados, _sol2) == [])
    for t in _p["T"]:
        print(t)
        for h in _p["H"]:
            linha = []
            for i in _p["I"]:
                aula = [d for d in _p["D"] if sol[(t, d, i, h)] == 1]
                linha.append(aula[0] if aula else "-")
            print(f"{h}º tempo:", " | ".join(f"{a:<16}" for a in linha))
        print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Construção Incremental

    Quando os recursos mudam ligeiramente, resolver o problema do zero tem dois problemas: é mais lento e, sobretudo, o solver escolhe um horário qualquer entre os que cumprem as regras, que costuma ser muito diferente do anterior. Para a escola isso significa mudar aulas que não precisavam de mudar.

    A nossa abordagem usa o horário anterior $H_0$ de duas formas:

    1. **Ponto de partida.** Sugerimos ao solver os valores de $H_0$ (`AddHint`), para começar a procura perto de uma solução conhecida.
    2. **Custo por mudança.** Acrescentamos ao objetivo um termo que penaliza cada aula de $H_0$ que deixa de estar em $H_1$:

    $$\min \;\; \text{peso}\cdot\sum_{(t,d,i,h)\,:\,x^0_{t,d,i,h}=1}\left(1-x^1_{t,d,i,h}\right) \;+\; \sum_{p,i,h} b_{p,i,h}$$

    O `peso` (100) é muito maior do que o número de buracos que se pode ganhar, por isso a estabilidade tem prioridade sobre os buracos. Isto é uma escolha: aceitamos mais buracos se isso evitar mover uma aula.

    O $H_1$ cumpre as mesmas regras R1–R7, porque usa o mesmo `construir_modelo` com os dados novos. As variáveis de $H_0$ que não existem no novo modelo (por exemplo, de uma turma que desapareceu) são ignoradas.

    **Resultados** com `dados` → `dados_v2` (tempo médio de 5 execuções, só da resolução):

    | | Tempo | Aulas alteradas | Válido |
    |---|---|---|---|
    | Do zero | 0,054 s | 25 | sim |
    | Incremental | 0,038 s | 2 | sim |

    O ganho principal é na estabilidade: o horário novo mantém quase tudo e muda 2 aulas, em vez de 25. A diferença de tempo existe mas é pequena, porque a instância é pequena e ambos os métodos resolvem em milissegundos. O benefício de velocidade só deve aparecer em instâncias maiores.

    #### Outros cenários

    Para mostrar que a abordagem não depende do cenário de `dados_v2`, aplicámo-la a mais alterações de recursos, todas feitas só sobre os dados, sem mexer no código:

    | Alteração | Aulas alteradas (incremental) | Aulas alteradas (do zero) |
    |---|---|---|
    | Disponibilidade (`dados_v2`) | 2 | 25 |
    | Turma e disciplina novas | 3 | 27 |
    | Professor substituído | 0 | 30 |
    | Sala Normal com menos salas | 6 | 33 |

    Em todos os casos os dois horários são válidos, e o incremental muda muito menos aulas. A avaria de uma sala modela-se baixando a `quantidade` do tipo em `salas.csv`, porque o formato dos dados só guarda a quantidade por tipo de sala e não a disponibilidade por tempo.
    """)
    return


@app.cell
def _(construir_modelo, lista_de_dados):
    def construcao_incremental(dados_novos, sol0, peso=100):
        modelo, x = construir_modelo(dados_novos, com_objetivo=False)
        p = lista_de_dados(dados_novos)
        antigas = [k for k, v in sol0.items() if v == 1 and k in x]
        mudancas = sum(1 - x[k] for k in antigas)
        menos_buracos(modelo, x, p, extra=peso * mudancas)

        for k, v in sol0.items():
            if k in x:
                modelo.AddHint(x[k], v)

        return modelo, x

    return (construcao_incremental,)


@app.cell
def _(ler_dados):
    dados0 = ler_dados("dados")
    dados1 = ler_dados("dados_v2")
    return dados0, dados1


@app.cell
def _(construcao_incremental, construir_modelo, dados0, dados1, resolver):
    modelo0, x0 = construir_modelo(dados0)
    sol0 = resolver(modelo0, x0)

    modelo1, x1 = construcao_incremental(dados1, sol0)
    sol1 = resolver(modelo1, x1)
    return sol0, sol1


@app.function
def mudancas_entre(sol_antigo, sol_novo):
    return sum(1 for k, v in sol_antigo.items() if v == 1 and sol_novo.get(k, 0) == 0)


@app.cell
def _(dados0, dados1, sol0, sol1, verificar):
    verificar(dados0, sol0)    
    verificar(dados1, sol1) 
    mudancas_entre(sol0, sol1)
    return


@app.cell
def _(
    construcao_incremental,
    construir_modelo,
    dados1,
    resolver,
    sol0,
    time,
    verificar,
):
    def medir(construir, repeticoes=5):
        tempos = []
        for _ in range(repeticoes):
            modelo, x = construir()
            t0 = time.perf_counter()
            sol = resolver(modelo, x)
            tempos.append(time.perf_counter() - t0)
        return sol, sum(tempos) / len(tempos)

    sol1_zero, t_zero = medir(lambda: construir_modelo(dados1))
    sol1_inc, t_inc = medir(lambda: construcao_incremental(dados1, sol0))

    print(f"Do zero: {t_zero:.3f} s, {mudancas_entre(sol0, sol1_zero)} aulas alteradas")
    print(f"Incremental: {t_inc:.3f} s, {mudancas_entre(sol0, sol1_inc)} aulas alteradas")
    print("Válidos:", verificar(dados1, sol1_zero) == [], verificar(dados1, sol1_inc) == [])
    return


@app.cell
def _(
    construcao_incremental,
    construir_modelo,
    dados0,
    resolver,
    sol0,
    verificar,
):
    import copy

    dados3 = copy.deepcopy(dados0)      # professor substituído
    dados3["disciplinas"].loc[dados3["disciplinas"]["disciplina"] == "Matemática", "professor"] = "Prof. Nova"

    dados4 = copy.deepcopy(dados0)      # sala avariada: menos salas normais
    dados4["salas"].loc[dados4["salas"]["sala"] == "Sala Normal", "quantidade"] = 1

    for _nome, _dn in [("Professor substituído", dados3), ("Sala Normal reduzida", dados4)]:
        _mi, _xi = construcao_incremental(_dn, sol0)
        _si = resolver(_mi, _xi)
        _mz, _xz = construir_modelo(_dn)
        _sz = resolver(_mz, _xz)
        print(_nome, "| incremental:", mudancas_entre(sol0, _si),
              "| do zero:", mudancas_entre(sol0, _sz),
              "| válidos:", verificar(_dn, _si) == [], verificar(_dn, _sz) == [])
    return


@app.cell
def _(
    construcao_incremental,
    construir_modelo,
    ler_dados,
    resolver,
    sol0,
    verificar,
):
    _dados_t = ler_dados("dados_teste")

    _mi, _xi = construcao_incremental(_dados_t, sol0)
    _si = resolver(_mi, _xi)

    _mz, _xz = construir_modelo(_dados_t)
    _sz = resolver(_mz, _xz)

    print("Incremental:", mudancas_entre(sol0, _si), "aulas alteradas")
    print("Do zero:", mudancas_entre(sol0, _sz), "aulas alteradas")
    print("Válidos:", verificar(_dados_t, _si) == [], verificar(_dados_t, _sz) == [])
    return


@app.cell
def _(lista_de_dados, pd):
    def grelha_df(dados, sol, turma):
        p = lista_de_dados(dados)
        linhas = {}
        for h in p["H"]:
            linha = {}
            for i in p["I"]:
                aula = [d for d in p["D"] if sol[(turma, d, i, h)] == 1]
                linha[i] = aula[0] if aula else "-"
            linhas[f"{h}º tempo"] = linha
        return pd.DataFrame.from_dict(linhas, orient="index")

    return (grelha_df,)


@app.cell
def _(dados, grelha_df, lista_de_dados, mo, sol):
    mo.vstack([
        item
        for _t in lista_de_dados(dados)["T"]
        for item in (mo.md(f"**Turma {_t}**"), grelha_df(dados, sol, _t))
    ])
    return


@app.cell
def _(dados0, dados1, grelha_df, mo, sol0, sol1):
    mo.hstack([
        mo.vstack([mo.md("**7ºA, H0**"), grelha_df(dados0, sol0, "7ºA")]),
        mo.vstack([mo.md("**7ºA, H1**"), grelha_df(dados1, sol1, "7ºA")]),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Escala (bónus)

    Para estudar o comportamento com mais turmas, geramos conjuntos de dados sintéticos (`gerar_dados_escala`) com 16 disciplinas de carga semanal 1, cada uma com um professor próprio, e 4 a 24 turmas. Os dados continuam a ser lidos de ficheiros CSV, sem alterar o código do modelo.

    | Turmas | Variáveis | Tempo de resolução (s) | Resultado |
    |---|---|---|---|
    | 4 | 1 600 | 0,22 | válido |
    | 8 | 3 200 | 0,35 | válido |
    | 12 | 4 800 | 0,48 | válido |
    | 16 | 6 400 | 0,79 | válido |
    | 20 | 8 000 | 0,86 | válido |
    | 24 | 9 600 | 1,05 | válido |

    Em todos os casos o horário cumpre as regras (verificado pelo validador independente) e o tempo cresce de forma aproximadamente linear com o número de variáveis, ficando perto de 1 s para 9 600 variáveis.

    **Limites encontrados.** Até às 24 turmas não encontrámos um limite computacional, mas encontrámos um limite estrutural dos dados. Com o formato atual, cada turma tem todas as disciplinas e cada disciplina um único professor, pelo que a carga de um professor cresce com o número de turmas. Com 8 disciplinas de carga 2, um professor dá $2N$ tempos por semana e só tem 25, logo o problema fica impossível a partir de 13 turmas (confirmámos com 16: o solver prova rapidamente que não há solução). Por isso os dados de escala usam carga 1 e mais disciplinas, o que permite até 25 turmas.

    A dificuldade de uma instância depende não só do tamanho mas de quão apertada está: com salas, professores ou tempos muito escassos, o solver tem de explorar muito mais, e é aí que o tempo pode crescer depressa.
    """)
    return


@app.cell
def _(Path, pd):
    def gerar_dados_escala(pasta, n_turmas, n_disc=16, carga=1):
        pasta = Path(pasta)
        pasta.mkdir(exist_ok=True)
        pd.DataFrame({"turma": [f"T{k}" for k in range(n_turmas)]}).to_csv(pasta / "turmas.csv", index=False)
        pd.DataFrame({
            "disciplina": [f"Disc{j}" for j in range(n_disc)],
            "professor": [f"Prof{j}" for j in range(n_disc)],
            "carga_semanal": [carga] * n_disc,
            "duplo_periodo": ["nao"] * n_disc,
            "sala_especial": [""] * n_disc,
        }).to_csv(pasta / "disciplinas.csv", index=False)
        pd.DataFrame({"sala": ["Sala Normal"], "tipo": ["normal"], "quantidade": [n_turmas]}).to_csv(pasta / "salas.csv", index=False)
        pd.DataFrame({"professor": [], "dia": [], "periodo": []}).to_csv(pasta / "disponibilidade_excecoes.csv", index=False)

    return (gerar_dados_escala,)


@app.cell
def _(
    construir_modelo,
    gerar_dados_escala,
    ler_dados,
    pd,
    resolver,
    time,
    verificar,
):
    resultados = []
    for _n in (4, 8, 12, 16, 20, 24):
        gerar_dados_escala(f"dados_escala_{_n}", _n)
        _d = ler_dados(f"dados_escala_{_n}")
        _modelo, _x = construir_modelo(_d)
        _t0 = time.perf_counter()
        _sol = resolver(_modelo, _x, tempo_max=60)
        _dt = time.perf_counter() - _t0
        resultados.append({
            "turmas": _n,
            "variáveis": len(_x),
            "tempo (s)": round(_dt, 2),
            "resultado": "sem solução" if _sol is None
                else ("válido" if verificar(_d, _sol) == [] else "INVÁLIDO"),
    })

    pd.DataFrame(resultados)
    return


if __name__ == "__main__":
    app.run()
