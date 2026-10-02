import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


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
    return


if __name__ == "__main__":
    app.run()
