# ============================================================
# SOFTWARE PROPRIETÁRIO
#
# DATASET NORMALIZATION ENGINE
# MOTOR DE NORMALIZAÇÃO E PADRONIZAÇÃO DE DADOS
#
# DESENVOLVIDO POR:
# NADISON ROBERTO FERREIRA RIBEIRO MINTO
#
# © TODOS OS DIREITOS RESERVADOS
# ============================================================

import re
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR.parent / "input"

OUTPUT_DIR = BASE_DIR.parent / "output"

INPUT_DIR.mkdir(exist_ok=True)

OUTPUT_DIR.mkdir(exist_ok=True)

APENAS_MAIS_RECENTE = True

# ============================================================
# MAPEAMENTOS
# ============================================================

COL_TITULO = "Título"

COL_PLACA = "Placa"

COL_UF = "UF Cliente"

COL_ESTADO = "Estado"

COL_DATA_VENDA = "Data da venda"

COL_DATA_IMPRESSAO = "Data da impressão"

# ============================================================
# ORDEM ESTRUTURAL
# ============================================================

COLUNAS_FIXAS = [

    "Placa",

    "Fase atual",

    "Criador",

    "Criado em",

    "Etiquetas",

    "Responsáveis",

    "Segmento",

    "Chassi",

    "Renavam",

    "Data da venda",

    "Data da impressão",

    "Nome do cliente",

    "UF Cliente",

    "Estado",

    "Cidade Cliente",

    "Contrato",

    "Empresa",

    "Regional",

    "Loja",

    "Impedimento",

    "Observação",

]

# ============================================================
# ESTADOS
# ============================================================

UF_PARA_ESTADO = {

    "AC": "ACRE",

    "AL": "ALAGOAS",

    "AP": "AMAPÁ",

    "AM": "AMAZONAS",

    "BA": "BAHIA",

    "CE": "CEARÁ",

    "DF": "DISTRITO FEDERAL",

    "ES": "ESPÍRITO SANTO",

    "GO": "GOIÁS",

    "MA": "MARANHÃO",

    "MG": "MINAS GERAIS",

    "MS": "MATO GROSSO DO SUL",

    "MT": "MATO GROSSO",

    "PA": "PARÁ",

    "PB": "PARAÍBA",

    "PE": "PERNAMBUCO",

    "PI": "PIAUÍ",

    "PR": "PARANÁ",

    "RJ": "RIO DE JANEIRO",

    "RN": "RIO GRANDE DO NORTE",

    "RO": "RONDÔNIA",

    "RR": "RORAIMA",

    "RS": "RIO GRANDE DO SUL",

    "SC": "SANTA CATARINA",

    "SE": "SERGIPE",

    "SP": "SÃO PAULO",

    "TO": "TOCANTINS",

}

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def limpar_nome_coluna(valor):

    texto = "" if valor is None else str(valor)

    texto = texto.replace("\u00A0", " ")

    texto = re.sub(
        r"\s+",
        " ",
        texto
    ).strip()

    return texto

# ============================================================
# NORMALIZAÇÃO DE DATA
# ============================================================

def normalizar_data(serie):
    """Normalize Brazilian and ISO date strings without locale ambiguity."""
    dt = pd.to_datetime(
        serie,
        errors="coerce",
        format="mixed",
        dayfirst=True,
    )
    return dt.dt.strftime("%d/%m/%Y")

# ============================================================
# LISTAGEM DE EXCEL
# ============================================================

def listar_xlsx():
    if not INPUT_DIR.is_dir():
        return []
    return sorted(
        (
            path for path in INPUT_DIR.glob("*.xlsx")
            if not path.name.startswith("~$")
        ),
        key=lambda path: (path.stat().st_mtime_ns, path.name.casefold()),
    )

# ============================================================
# ARQUIVO MAIS RECENTE
# ============================================================

def escolher_mais_recente(arquivos):

    if not arquivos:
        raise ValueError("Nenhum arquivo XLSX disponível para seleção.")
    return max(
        arquivos,
        key=lambda path: (path.stat().st_mtime_ns, path.name.casefold()),
    )

# ============================================================
# PROCESSAMENTO
# ============================================================

def tratar_arquivo(arq):

    print()

    print(f"📄 Processando: {arq.name}")

    df = pd.read_excel(
        arq,
        engine="openpyxl"
    )

    df.columns = [limpar_nome_coluna(column) for column in df.columns]

    duplicates = df.columns[df.columns.duplicated()].unique().tolist()
    if duplicates:
        raise ValueError(
            "Colunas duplicadas após normalização: "
            + ", ".join(str(column) for column in duplicates)
        )

    if COL_TITULO in df.columns:
        df.rename(columns={COL_TITULO: COL_PLACA}, inplace=True)

    duplicates = df.columns[df.columns.duplicated()].unique().tolist()
    if duplicates:
        raise ValueError(
            "Colunas duplicadas após mapeamento: "
            + ", ".join(str(column) for column in duplicates)
        )

    if COL_PLACA not in df.columns:

        raise RuntimeError(
            "Coluna PLACA não encontrada."
        )

    if COL_UF in df.columns:

        df[COL_UF] = (

            df[COL_UF]

            .astype("string")

            .str.upper()

            .str.strip()

        )

        if COL_ESTADO not in df.columns:

            df[COL_ESTADO] = pd.NA

        vazio = (

            df[COL_ESTADO].isna()

            | (

                df[COL_ESTADO]

                .astype(str)

                .str.strip() == ""

            )

        )

        df.loc[
            vazio,
            COL_ESTADO
        ] = df.loc[
            vazio,
            COL_UF
        ].map(UF_PARA_ESTADO)

    if COL_DATA_VENDA in df.columns:

        df[COL_DATA_VENDA] = normalizar_data(
            df[COL_DATA_VENDA]
        )

    if COL_DATA_IMPRESSAO in df.columns:

        df[COL_DATA_IMPRESSAO] = normalizar_data(
            df[COL_DATA_IMPRESSAO]
        )

    existentes = df.columns.tolist()

    fixas = [

        c

        for c in COLUNAS_FIXAS

        if c in existentes

    ]

    extras = [

        c

        for c in existentes

        if c not in fixas

    ]

    df = df[fixas + extras]

    caminho_saida = (

        OUTPUT_DIR
        / f"NORMALIZADO_{arq.name}"

    )

    df.to_excel(

        caminho_saida,

        index=False,

        engine="openpyxl"

    )

    print(
        "✅ Dataset normalizado."
    )

    print(caminho_saida)

# ============================================================
# MAIN
# ============================================================

def main():

    arquivos = listar_xlsx()

    if not arquivos:

        print(
            "⚠️ Nenhum Excel encontrado."
        )

        return

    if APENAS_MAIS_RECENTE:

        arquivos = [
            escolher_mais_recente(arquivos)
        ]

    for arq in arquivos:

        tratar_arquivo(arq)

    print()

    print(
        "🎉 PROCESSAMENTO FINALIZADO"
    )

# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
