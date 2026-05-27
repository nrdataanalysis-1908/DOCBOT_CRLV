# ============================================================
# SOFTWARE PROPRIETÁRIO
#
# DOCUMENT LINK GENERATION ENGINE
# MOTOR DE GERAÇÃO E VINCULAÇÃO DOCUMENTAL
#
# DESENVOLVIDO POR:
# NADISON ROBERTO FERREIRA RIBEIRO MINTO
#
# © TODOS OS DIREITOS RESERVADOS
# ============================================================

import os
import urllib.parse
from datetime import datetime

from openpyxl import load_workbook

# ============================================================
# IDENTIFICAÇÃO
# ============================================================

NOME_SISTEMA = "DOCUMENT_LINK_GENERATION_ENGINE"

VERSAO_SISTEMA = "1.0.0"

AUTOR = "NADISON ROBERTO FERREIRA RIBEIRO MINTO"

# ============================================================
# ESTRUTURA
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

INPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "input"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "output"
)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# URL BASE
# ============================================================

def escolher_base_documental():

    print("\n📌 Base documental")

    print("[1] Repositório Web")
    print("[2] Estrutura Cloud")

    while True:

        tipo = input(
            "Escolha 1 ou 2: "
        ).strip()

        if tipo in ("1", "2"):
            break

        print("Opção inválida.")

    base_url = input(
        "\n🌐 Informe URL base: "
    ).strip()

    pasta = input(
        "\n📁 Nome da pasta documental: "
    ).strip()

    pasta_cod = urllib.parse.quote(pasta)

    return f"{base_url}/{pasta_cod}"

# ============================================================
# ENCONTRAR EXCEL
# ============================================================

def encontrar_excel_mais_recente():

    arquivos = [

        os.path.join(INPUT_DIR, f)

        for f in os.listdir(INPUT_DIR)

        if (
            f.lower().endswith(".xlsx")
            and not f.startswith("~$")
        )

    ]

    if not arquivos:

        raise RuntimeError(
            "Nenhum Excel encontrado."
        )

    return max(
        arquivos,
        key=os.path.getmtime
    )

# ============================================================
# PROCESSAMENTO
# ============================================================

def gerar_links():

    base_url = escolher_base_documental()

    arquivo_excel = encontrar_excel_mais_recente()

    print()

    print(
        f"📊 Excel utilizado:"
    )

    print(arquivo_excel)

    wb = load_workbook(arquivo_excel)

    ws = wb.active

    headers = {

        c: ws.cell(1, c).value

        for c in range(
            1,
            ws.max_column + 1
        )

    }

    col_placa = next(

        c for c, h in headers.items()

        if (
            h
            and str(h).strip().upper()
            == "PLACA"
        )

    )

    pares = []

    for c, h in headers.items():

        if (
            isinstance(h, str)
            and h.upper().startswith("ANO_")
        ):

            ano = h.split("_")[1]

            col_arq = next(

                (
                    ca

                    for ca, ha in headers.items()

                    if ha == f"ARQUIVO_{ano}"
                ),

                None

            )

            if col_arq:

                pares.append(
                    (ano, col_arq)
                )

    start_col = ws.max_column + 1

    for idx, (ano, col_arq) in enumerate(pares):

        col_link = start_col + idx

        ws.cell(
            1,
            col_link
        ).value = f"LINK_DOCUMENTO_{ano}"

        for r in range(2, ws.max_row + 1):

            placa = ws.cell(
                r,
                col_placa
            ).value

            arquivo_val = ws.cell(
                r,
                col_arq
            ).value

            if placa and arquivo_val:

                nome_pdf = (
                    f"CRLV_{str(placa).strip()}_{ano}.pdf"
                )

                url = (
                    f"{base_url}/"
                    f"{urllib.parse.quote(nome_pdf)}"
                )

                ws.cell(
                    r,
                    col_link
                ).value = url

    nome_saida = (

        f"LINKS_DOCUMENTAIS_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    )

    caminho_saida = os.path.join(
        OUTPUT_DIR,
        nome_saida
    )

    wb.save(caminho_saida)

    wb.close()

    print()

    print("✅ Links documentais gerados.")

    print(caminho_saida)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    gerar_links()
