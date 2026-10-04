import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Trabalho Prático 1

    ## Exercício 2: **Sudoku Genérico como CSP**

    Um Sudoku clássico consiste numa grelha de dimensão $n^2 \times n^2$, onde cada linha, coluna e cada bloco de dimensão $n \times n$ contém valores entre `1` e `n²` e todos diferentes.

    O problema por decifrar é modelação e resolução de CSP, utilizando a restrição `AllDifferent()`.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import random
    from ortools.sat.python import cp_model

    return cp_model, mo, random


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **R1: box**

    A classe `box` constitui a representação genérica de um grupo de células da grelha.

    Cada célula é identificada pelas coordenadas `(linha,coluna)` e um valor fixo pertencente ao intervalo $[1,n^2]$ (célula fixa a esse valor) ou `None` (célula livre).

    O construtor permite criar um `box` vazio ou, opcionalmente, fornecer um conjunto inicial de células. Quando são fornecidas células no momento da criação, estas são adicionadas através do método `add()`, garantindo que são aplicadas as mesmas validações de coordenadas e valores.

    O método `add()` permite posteriormente acrescentar novas células ao grupo, rejeitando coordenadas exteriores à grelha e valores que não pertencem ao domínio.

    A classe disponibiliza ainda uma representação matricial $n^2 \times n^2$, na qual as células livres são representadas por `0`.

    A classe `box` não contém qualquer conhecimento específico sobre linhas, colunas ou blocos, constituindo assim a estrutura genérica que será reutilizada nas restantes partes do trabalho.
    """)
    return


@app.class_definition
# grupo genérico de células
class box:

    # inicializa um box
    def __init__(self,n,cells=None):
        self.n = n
        self.dim = n**2
        self.cells = {}

        # considera células iniciais fornecidas
        if cells is not None:
            for (i,j), valor in cells.items():
                self.add(i,j,valor)


    # adiciona uma célula ao box
    def add(self, i, j, val=None):

        # verifica se as coordenadas são válidas
        if (0 <= i < self.dim and 0<= j <self.dim):

            # verifica se o valor é válido
            if (val is None or 1 <= val <= self.dim):
                self.cells[(i,j)] = val

            else:
                raise ValueError("Valor fora do alcance")

        else:
            raise IndexError("Coordenadas fora do alcance")


    # matriz de box
    def matriz(self):
        dim = self.dim

        m = []

        # inicializa a matriz com 0 (para o caso das células livres)
        for i in range(dim):
            linha = []
            
            for j in range(dim):
                    linha.append(0)
                
            m.append(linha)

        # percorre as células fixas e atualiza o valor na matriz
        for (i,j),valor in self.cells.items():
            if valor is not None:
                m[i][j] = valor

        return m


    # imprime a matriz de box
    def imprimir(self):
        m = self.matriz()

        for linha in m:
            for valor in linha:
                print(valor, end=" ")
            print()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Teste sobre as funcionalidades de R1:
    """)
    return


@app.cell
def _():
    # cria um box 4x4
    b1 = box(2)

    # adiciona células fixas e livres
    b1.add(0,1,3) # posição (0,1) com valor 3
    b1.add(1,2) # posição (1,2) com valor None
    b1.add(3,3,4) 

    # imprime a matriz b para verificar se foi adicionado com sucesso
    print("n = 2: ")
    b1.imprimir()

    print()

    # cria um box 9x9 com células iniciais
    b2 = box(3, {(4,8): 9,
                 (2,4): 1,
                 (6,1): None,
                 (7,2): 6,
                 (1,5): 3,
                 (3,3): None})
    print("n = 3: ")
    b2.imprimir()
    return


@app.cell
def _():
    # verificar se deteta as coordenadas inválidas
    # b3 = box(2, {(4,8): 9})

    try:
        b3 = box(2, {(4,8): 9})
        print("Erro: a coordenada inválida foi aceite.")
    except IndexError:
        print("Teste concluído: coordenada inválida corretamente rejeitada.")
    return


@app.cell
def _():
    # verificar se deteta os valores inválidos
    b4 = box(2, {(1,2): 9})
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Os testes confirmam que a classe `box` pode ser criada tanto vazia como com um conjunto inicial de células. As células fornecidas inicialmente são corretamente armazenadas e representadas na matriz, sendo igualmente verificadas as situações de coordenadas e valores inválidos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **R2: cube**

    A classe `cube` representa um bloco $n \times n$ do Sudoku e é definida como uma subclasse de `box`.

    Esta opção permite reutilizar toda a estrutura já implementada em `box`, nomeadamente o armazenamento das células, a validação das coordenadas e o método `add()`. Assim, `cube` não precisa de redefinir a forma como um grupo de células é representado, sendo apenas responsável por determinar quais as células que pertencem a um determinado bloco.

    Cada bloco é identificado pelos índices `(i,j)`, com `0 <= i,j < n`. O canto superior esquerdo do bloco é dado por $(i \cdot n,\ j \cdot n)$.

    A partir dessa posição inicial, são percorridas `n` linhas e `n` colunas, sendo cada célula adicionada ao grupo através do método `add()` herdado de `box`.

    Desta forma, mantém-se uma implementação mais genérica e evita-se a duplicação de código.
    """)
    return


@app.class_definition
# um bloco n*n do Sudoku
class cube(box): # subclasse de box

    # inicializa um cube
    def __init__(self,n,i,j):

        # herda de box os dados iniciais
        super().__init__(n)

        # verifica se o i e j estão dentro dos requisitos
        if not (0 <= i < n and 0 <= j < n):
            raise IndexError("Posição fora do alcance")

        # cálculo das posições reais do cube no sudoku
        self.linha_inicial = i*n
        self.coluna_inicial = j*n

        # adiciona as células nas posições reais
        for l in range(n):
            for c in range(n):
                
                # herda a função add de box
                self.add(self.linha_inicial + l,
                         self.coluna_inicial + c)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Teste sobre as funcionalidades de R2:
    """)
    return


@app.cell
def _():
    # cria um cube com n=2
    c1 = cube(2,0,1) # linha inicial=0 e coluna inicial=2
    print("n = 2: ")
    print(c1.cells)

    print()

    # cria um cube com n=3
    c2 = cube(3,1,2) # linha inicial=3 e coluna inicial=6
    print("n = 3: ")
    print(c2.cells)
    return


@app.cell
def _():
    # validar se tem capacidade identificar posições inválidas
    c3 = cube(3,4,0) # bloco de n=3, linha inicial=12 (fora do bloco)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Os testes realizados confirmam que a classe `cube` identifica corretamente as células pertencentes a um bloco `n × n`, tanto para `n = 2` como para `n = 3`.

    Verifica-se também que a classe rejeita índices de bloco inválidos, através da geração de uma exceção apropriada.

    Assim, conclui-se que a implementação de `cube` cumpre os requisitos definidos para a representação e validação dos blocos do Sudoku.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **R3: path**

    A classe `path` representa uma sequência reta de células entre duas coordenadas da grelha, podendo essa sequência ser horizontal ou vertical.

    Tal como `cube`, a classe `path` é definida como uma subclasse de `box`. Esta escolha permite reutilizar a estrutura de `box` e reutilizar o seu método `add()` para adicionar células. Assim, `path` fica responsável apenas por determinar quais as células que pertencem ao percurso definido entre as coordenadas inicial e final.

    Dadas duas coordenadas `inicio` e `fim`, é verificado 3 casos:
    - se as linhas forem iguais, o percurso é horizontal;
    - se as colunas forem iguais, o percurso é vertical;
    - caso contrário, as coordenadas não definem um percurso reto válido.

    O percurso deve ainda funcionar nos dois sentidos. Por exemplo, `path(3, (2,1), (2,5))` e `path(3, (2,5), (2,1))` representam o mesmo conjunto de células, apenas percorrido em sentidos opostos.

    Para controlar o sentido do percurso, é utilizado um `passo` de valor `1` quando o índice aumenta e `-1` quando diminui.

    Desta forma, a mesma classe pode ser utilizada posteriormente para representar tanto as linhas como as colunas do Sudoku.
    """)
    return


@app.class_definition
# uma sequência reta de células
class path(box): # subclasse de box

    # inicializa um path
    def __init__(self, n, inicio, fim):

        # herda de box os dados iniciais
        super().__init__(n)

        # separa as coordenadas para facilitar as verificações
        l_inicio, c_inicio = inicio
        l_fim, c_fim = fim

        # verifica se as coordenadas são válidas
        if not (0 <= l_inicio < self.dim and 
                0 <= c_inicio < self.dim and
                0 <= l_fim < self.dim and 
                0 <= c_fim < self.dim):
            raise IndexError("Coordenadas fora do alcance")

        # se for direção horizontal
        if l_inicio == l_fim:

            # descobrir o sentido
            if c_inicio <= c_fim:
                passo = 1
            else:
                passo = -1

            for j in range(c_inicio, c_fim + passo, passo):
                self.add(l_inicio, j)

        # se for direção vertical
        elif c_inicio == c_fim:

            # descobrir o sentido
            if l_inicio <= l_fim:
                passo = 1
            else:
                passo = -1

            for i in range(l_inicio, l_fim + passo, passo):
                self.add(i, c_inicio)

        else:
            raise ValueError("Coordenadas não formam uma reta")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Teste sobre as funcionalidades de R3:
    """)
    return


@app.cell
def _():
    # cria um path
    p1 = path(3, (2,1), (2,5)) # path de n=3, com início em (2,1) e fim em (2,5)
    print(p1.cells)
    return


@app.cell
def _():
    # verifica a função no sentido inverso
    p2 = path(3, (2,5), (2,1))
    print(p2.cells)
    return


@app.cell
def _():
    # validar se tem capacidade de identificar casos de erro
    p3 = path(3, (1,2), (2,7))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Os testes confirmam que a classe `path` consegue representar corretamente uma sequência reta de células entre duas coordenadas, funcionando tanto no sentido direto como no sentido inverso.

    Foi também verificado que coordenadas que não pertencem à mesma linha nem à mesma coluna são corretamente rejeitadas.

    Desta forma, conclui-se que `path` pode ser utilizado de forma segura para representar linhas e colunas do Sudoku em ambos os sentidos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **R4: geração aleatória de pistas**

    As pistas iniciais do Sudoku são representadas através de um objeto da classe `box`, não sendo necessária a criação de uma nova classe específica para esse efeito.

    A função `gerar_pistas(n, k=None)` cria um `box` com `k` células escolhidas aleatoriamente na grelha. Para cada posição selecionada é também escolhido aleatoriamente um valor entre `1` e `n²`, que fica associado a essa célula como valor fixo.

    Caso `k` não seja indicado, é utilizado por omissão o valor de `n`.

    Antes da geração das pistas, é verificado se o valor de `k` é válido, isto é, se não é negativo e se não ultrapassa o número total de células da grelha.

    Durante a geração, são escolhidas aleatoriamente uma linha e uma coluna. Antes de adicionar a nova pista, é verificado se essa posição ainda não foi utilizada, evitando assim a sobreposição de pistas na mesma célula.

    A escolha aleatória das posições e dos valores é realizada através da biblioteca `random` do Python.

    No final, a função devolve o `box` contendo todas as pistas geradas, mantendo assim a mesma representação genérica utilizada nas restantes estruturas do Sudoku.
    """)
    return


@app.cell
def _(random):
    def gerar_pistas(n, k=None):

        # cria um box associado à grelha n² x n²
        pistas = box(n)

        # utiliza por omissão o n como k
        if k is None: 
            k = n

        # verifica se k é válido
        if k < 0 or k > pistas.dim**2: # dim**2 porque é o total de células
            raise ValueError("Número de pistas inválido")

        # adiciona pistas até atingir k células
        while len(pistas.cells) < k:
            linha = random.randint(0, pistas.dim - 1)
            coluna = random.randint(0, pistas.dim - 1)

            # evitar sobreposição na mesma célula
            if (linha,coluna) not in pistas.cells:
                valor = random.randint(1, pistas.dim)

                pistas.add(linha, coluna, valor)

        return pistas

    return (gerar_pistas,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Teste sobre as funcionalidades de R4:
    """)
    return


@app.cell
def _(gerar_pistas):
    # gerar pistas
    pista1 = gerar_pistas(2, 3)
    print(pista1.cells)
    print("pistas geradas: " + str(len(pista1.cells)))
    pista1.imprimir()
    return


@app.cell
def _(gerar_pistas):
    # verificar a capacidade de identificar erro
    pista2 = gerar_pistas(3, -1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Os testes realizados confirmam que a função `gerar_pistas` produz exatamente o número de pistas solicitado, sem repetir posições e atribuindo apenas valores válidos para a dimensão da grelha.

    A representação matricial permite ainda verificar visualmente a localização das pistas geradas.

    Foi também testado um valor inválido para `k`, sendo corretamente rejeitado através de uma exceção.

    Assim, conclui-se que a geração aleatória de pistas cumpre os requisitos definidos no R4.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **R5: criação do modelo CSP**

    Nesta fase é construído o modelo de satisfação de restrições responsável por representar o Sudoku.

    A função `modelo_sudoku(n)` cria um modelo `CpModel` e uma variável inteira para cada célula da grelha. Como a dimensão do Sudoku é $n^2 \times n^2$, cada uma com domínio entre `1` e `n²`.

    As variáveis são guardadas numa estrutura `x`, onde `x[i][j]` representa o valor atribuído à célula localizada na linha `i` e coluna `j`.

    A função `restringe_grupos(model, x, *grupos)` permite receber um número arbitrário de grupos de células. Estes grupos podem ser objetos `box`, `cube`, `path` ou o conjunto de pistas, uma vez que todos disponibilizam a mesma representação através de `cells`.

    Para cada grupo são aplicadas **duas formas de restrição**:

    - `AddAllDifferent()`, garantindo que todas as células do grupo possuem valores distintos;
    - restrições de igualdade para as células que possuem um valor previamente fixado.

    Desta forma, o modelo não necessita de distinguir se um grupo corresponde a uma linha, coluna, bloco ou conjunto de pistas, mantendo a modelação genérica pretendida.
    """)
    return


@app.cell
def _(cp_model):
    # cria o modelo CSP
    def modelo_sudoku(n):

        # define a dimensão da grelha do Sudoku
        dim = n**2 

        # cria o modelo CP_SAT (sugerido no enunciado)
        model = cp_model.CpModel()

        # dicionário que guarda as variáveis da grelha
        x = {}

        # cria as variáveis
        for i in range(dim):
            x[i] = {}

            # cada variável assume valores entre 1 e n²
            for j in range(dim):
                x[i][j] = model.NewIntVar(1, dim, f"x_{i}_{j}")

        return model, x


    # aplica ao modelo as restrições associadas a grupos
    def restringe_grupos(model, x, *grupos):

        # percorre todos os grupos fornecidos
        for grupo in grupos:

            # utilizada para guardar as variáveis do grupo
            variaveis = []

            for (i,j) in grupo.cells:
                variaveis.append(x[i][j])

            # restrição principal do Sudoku
            # todas as células do grupo devem possuir valores diferentes
            model.AddAllDifferent(variaveis)

            # trata das células fixas
            for (i,j), valor in grupo.cells.items():
                if valor is not None:
                    model.Add(x[i][j] == valor)


    # apresenta a estrutura das variáveis em formato matricial
    def imprimir_variaveis(x):
        for i in range(len(x)):
            for j in range(len(x[i])):
                print(x[i][j], end=" ")
            print()

    return modelo_sudoku, restringe_grupos


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Teste sobre as funcionalidades de R5:
    """)
    return


@app.cell
def _(cp_model, modelo_sudoku, restringe_grupos):
    # cria um modelo para um Sudoku 4x4
    print("n = 2: ")

    model1, x1 = modelo_sudoku(2)

    # grupo correspondente à primeira linha
    linha1 = path(2, (0,0), (0,3))

    # grupo contendo uma célula fixa
    pista3 = box(2, {(0,0): 1})

    # adicionar simultaneamente as restrições dos dois grupos
    restringe_grupos(model1, x1, linha1, pista3)

    # cria o solver e resolve o modelo
    solver1 = cp_model.CpSolver()
    status1 = solver1.Solve(model1)

    # apresentar a primeira linha caso exista solução
    if status1 == cp_model.OPTIMAL or status1 == cp_model.FEASIBLE:
        for j in range(4):
            print(solver1.Value(x1[0][j]), end=" ")
        print()

    print()

    # criar um modelo para um Sudoku 9x9
    print("n = 3: ")

    model2, x2 = modelo_sudoku(3)

    # grupo correspondente à primeira linha
    linha2 = path(3, (0,0), (0,8))

    # grupo contendo uma célula fixa
    pista4 = box(3, {(0,0): 1})

    # adicionar simultaneamente as restrições dos dois grupos
    restringe_grupos(model2, x2, linha2, pista4)

    # cria o solver e resolve o modelo
    solver2 = cp_model.CpSolver()
    status2 = solver2.Solve(model2)

    # apresentar a primeira linha caso exista solução
    if status2 == cp_model.OPTIMAL or status2 == cp_model.FEASIBLE:
        for j in range(9):
            print(solver2.Value(x2[0][j]), end=" ")
        print()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    O teste utiliza simultaneamente uma linha e um grupo contendo uma célula fixa, demonstrando que `restringe_grupos` aceita vários grupos numa única chamada.

    A solução obtida apresenta valores distintos em toda a primeira linha e mantém a célula `(0,0)` fixada ao valor `1`, confirmando tanto a aplicação de `AddAllDifferent` como das restrições de valores previamente definidos.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **R6: montagem e resolução do Sudoku completo**

    Nesta fase são reunidas todas as estruturas e restrições definidas anteriormente, permitindo construir o modelo completo do Sudoku.

    A função `resolver_sudoku(n, k=None)` começa por criar o modelo CSP e a grelha de variáveis através da função desenvolvida no R5.

    De seguida, são adicionados ao mesmo modelo os diferentes grupos que definem as regras do Sudoku:

    - cada linha é representada por um `path` horizontal;
    - cada coluna é representada por um `path` vertical;
    - cada bloco $n \times n$ é representado por um `cube`;
    - as pistas iniciais são representadas por um `box`.

    Para cada um destes grupos é utilizada a função `restringe_grupos`, que aplica a restrição `AllDifferent()` e fixa os valores previamente atribuídos, quando existirem.

    Após a adição de todas as restrições, o modelo é resolvido através de `CpSolver`. Caso seja encontrada uma solução, os valores atribuídos às variáveis são apresentados em formato matricial. Caso contrário, é indicado que não foi encontrada uma solução.

    Desta forma, a resolução do Sudoku resulta da combinação das várias estruturas genéricas desenvolvidas nas etapas anteriores, sem ser necessário implementar separadamente a lógica das linhas, colunas, blocos e pistas.
    """)
    return


@app.cell
def _(cp_model, gerar_pistas, modelo_sudoku, restringe_grupos):
    def resolver_sudoku(n, k=None):

        # cria o modelo CSP e as variáveis (reutilizar o R5)
        model, x = modelo_sudoku(n)

        # dimensão real da grelha n² x n²
        dim = n**2

        # guarda os grupos para aplicar a restrição AllDifferent()
        grupos = []

        # linhas 
        for i in range(dim):
            # cada linha é um path horizontal
            linha = path(n, (i,0), (i, dim-1))

            grupos.append(linha)


        # colunas 
        for j in range(dim):
            # cada coluna é um path vertical
            coluna = path(n, (0,j), (dim-1, j))

            grupos.append(coluna)


        # existem nxn blocos
        for i in range(n):
            for j in range(n):
                # cada bloco é criado através da classe cube
                bloco = cube(n, i, j)

                grupos.append(bloco)


        # gera k pistas aleatórias
        pistas = gerar_pistas(n, k)
        grupos.append(pistas)


        # aplicar ao modelo as restrições de todos os grupos
        restringe_grupos(model, x, *grupos)


        # resolução do modelo
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # se existir uma solução, apresenta a grelha resultante
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for i in range(dim):
                for j in range(dim):
                    print(solver.Value(x[i][j]), end=" ")
    
                print()

            # objetos necessários para posterior validação
            return solver, x, pistas

        else:
            print("Não foi encontrada solução.")
            return None

    return (resolver_sudoku,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Teste sobre as funcionalidades de R6:
    """)
    return


@app.cell
def _(resolver_sudoku):
    resultado_n2 = resolver_sudoku(2)
    return (resultado_n2,)


@app.cell
def _(resolver_sudoku):
    resultado_n3 = resolver_sudoku(3)
    return (resultado_n3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Depois de construídas todas as linhas, colunas e blocos, estes são reunidos numa lista juntamente com o grupo de pistas.

    Todos os grupos são então fornecidos à função `restringe_grupos`, que aplica ao modelo as restrições correspondentes sem necessidade de distinguir a origem de cada grupo.

    Esta abordagem evidencia a generalidade da estrutura desenvolvida: linhas, colunas, blocos e pistas são tratados uniformemente pelo modelo CSP.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## **Validação final da solução**

    Apesar de o solver encontrar uma solução para os casos testados com `n=2` e `n=3`, é necessário verificar automaticamente se essa solução respeita todas as regras do Sudoku.

    Para isso, foi criada a função `valida_solucao`, responsável por confirmar que:

    1. cada linha contém exatamente os valores de `1` a `n²`, sem repetições;
    2. cada coluna contém exatamente os valores de `1` a `n²`, sem repetições;
    3. cada bloco $n \times n$ contém exatamente os valores de `1` a `n²`;
    4. todas as pistas mantêm os valores que lhes foram inicialmente atribuídos.

    A validação das linhas, colunas e blocos é feita comparando os valores obtidos com a lista esperada `[1, ..., n²]`, após ordenação.

    No caso das pistas, é verificado diretamente se o valor atribuído pelo solver à respetiva célula coincide com o valor fixado inicialmente.
    """)
    return


@app.function
def valida_solucao(solver, x, pistas, n):
    dim = n**2

    # lista de valores que cada linha, coluna e bloco deve conter
    val_esperado = list(range(1, dim+1)) 


    # validação das linhas
    for i in range(dim):
        linha = []
        for j in range(dim):
            # recolhe os valores atribuídos pelo solver
            linha.append(solver.Value(x[i][j]))

        # linha ordenada deve coincidir exatamente com a lista esperada
        if sorted(linha) != val_esperado:
            return False


    # validação das colunas
    for j in range(dim):
        coluna = []
        for i in range(dim):
            # recolhe os valores atribuídos pelo solver
            coluna.append(solver.Value(x[i][j]))

        # coluna ordenada deve coincidir exatamente com a lista esperada
        if sorted(coluna) != val_esperado:
            return False


    # validação dos blocos
    # bi e bj identificam a posição do bloco em análise
    for bi in range(n):
        for bj in range(n):
            bloco = []

            # calcula as (linhas,colunas) pertencentes ao bloco no Sudoku
            for i in range(bi*n, bi*n+n):
                for j in range(bj*n, bj*n+n):
                    # recolhe os valores atribuídos pelo solver
                    bloco.append(solver.Value(x[i][j]))

            # bloco ordenado deve coincidir exatamente com a lista esperada
            if sorted(bloco) != val_esperado:
                return False


    # validação das pistas
    for (i, j), valor in pistas.cells.items():
        # confirma que o solver manteve o valor atribuído pela pista
        if solver.Value(x[i][j]) != valor:
            return False


    return True


@app.cell
def _(resultado_n2, resultado_n3):
    # validação do Sudoku 4x4
    if resultado_n2 is not None:
        solver2, x2, pistas2 = resultado_n2
        print("Validação n = 2:", valida_solucao(solver2, x2, pistas2, 2))

    print()

    # validação do Sudoku 9x9
    if resultado_n3 is not None:
        solver3, x3, pistas3 = resultado_n3
        print("Validação n = 3:", valida_solucao(solver3, x3, pistas3, 3))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    O teste final devolveu `True`, confirmando que a solução encontrada pelo solver respeita todas as restrições verificadas: linhas, colunas, blocos e pistas.

    Desta forma, fica validado automaticamente o correto funcionamento do modelo para o Sudoku resolvido.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Conclusão da implementação base

    Ao longo deste trabalho foi desenvolvido um resolvedor genérico de Sudoku recorrendo à modelação por CSP.

    A solução foi construída de forma modular, partindo da classe genérica `box`, utilizada para representar qualquer grupo de células sujeito a restrições. A partir dessa estrutura foram definidas as classes `cube` e `path`, responsáveis por representar, respetivamente, os blocos e os percursos horizontais ou verticais da grelha.

    Foi também implementada a geração aleatória de pistas, mantendo a mesma representação genérica através de `box`.

    Na fase de modelação, foi criado um modelo CP-SAT com uma variável inteira por célula, sendo aplicadas as restrições `AllDifferent()` aos diferentes grupos e fixados os valores das pistas sempre que necessário.

    A montagem final do Sudoku foi realizada através da combinação das linhas, colunas, blocos e pistas, permitindo ao solver encontrar uma solução completa para diferentes valores de `n`.

    Os testes realizados com `n=2` e `n=3`, juntamente com a validação automática das linhas, colunas, blocos e pistas, confirmam que a implementação satisfaz os requisitos definidos para a parte obrigatória do trabalho.

    A utilização de uma representação genérica para os grupos de células permite ainda estender facilmente o modelo a outras variantes de Sudoku, sem alterar a lógica principal de resolução.
    """)
    return


if __name__ == "__main__":
    app.run()
