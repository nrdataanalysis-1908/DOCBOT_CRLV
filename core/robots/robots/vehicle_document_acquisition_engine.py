# ============================================================
# SOFTWARE PROPRIETÁRIO
#
# VEHICLE DOCUMENT ACQUISITION ENGINE
# SISTEMA DE AQUISIÇÃO DOCUMENTAL VEICULAR
#
# DESENVOLVIDO POR:
# NADISON ROBERTO FERREIRA RIBEIRO MINTO
#
# © TODOS OS DIREITOS RESERVADOS
#
# É proibida a reprodução, modificação, distribuição,
# engenharia reversa ou utilização comercial sem
# autorização expressa do autor.
#
# Este software possui identificação estrutural,
# rastreabilidade técnica e assinatura de autoria.
#
# REGISTRO DE SOFTWARE: EM PROCESSO
# ============================================================

import os
import re
import time
import uuid
import shutil
import hashlib
from datetime import datetime

import pandas as pd
import pyautogui
import pyperclip
import PyPDF2

# ============================================================
# IDENTIFICAÇÃO
# ============================================================

EXECUCAO_ID = str(uuid.uuid4())

NOME_SISTEMA = "VEHICLE_DOCUMENT_ACQUISITION_ENGINE"

VERSAO_SISTEMA = "3.0.0"

AUTOR = "NADISON ROBERTO FERREIRA RIBEIRO MINTO"

DATA_EXECUCAO = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)

ASSINATURA_SISTEMA = hashlib.sha256(
    f"{NOME_SISTEMA}_{VERSAO_SISTEMA}_{AUTOR}".encode()
).hexdigest()

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

TEMP_DIR = os.path.join(
    BASE_DIR,
    "..",
    "temp"
)

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

ARQUIVO_ENTRADA = os.path.join(
    INPUT_DIR,
    "entrada_documentos.xlsx"
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

TEMPO_ESPERA_DOWNLOAD = 10
TEMPO_ESPERA_RESULTADO = 5
MAX_TENTATIVAS = 3

# ============================================================
# NORMALIZAÇÃO
# ============================================================

def limpar(valor):

    if pd.isna(valor):
        return ""

    return str(valor).strip().upper()

# ============================================================
# LEITURA EXCEL
# ============================================================

def carregar_registros():

    df = pd.read_excel(ARQUIVO_ENTRADA)

    registros = []

    for idx, row in df.iterrows():

        placa = limpar(
            row.iloc[0] if len(row) > 0 else ""
        )

        documento = limpar(
            row.iloc[1] if len(row) > 1 else ""
        )

        if not placa or not documento:
            continue

        registros.append({

            "INDICE": idx + 1,

            "PLACA": placa,

            "DOCUMENTO": documento,

        })

    print(
        f"✅ Registros carregados: {len(registros)}"
    )

    return registros

# ============================================================
# CALIBRAÇÃO
# ============================================================

def calibrar(nome):

    print()

    print(
        f"👉 Posicione o mouse sobre "
        f"{nome} em 5 segundos..."
    )

    time.sleep(5)

    pos = pyautogui.position()

    print(f"📍 {nome}: {pos}")

    return pos

# ============================================================
# ESPERA DOWNLOAD
# ============================================================

def esperar_download():

    inicio = time.time()

    while (
        time.time() - inicio
        < TEMPO_ESPERA_DOWNLOAD
    ):

        arquivos = [

            f for f in os.listdir(TEMP_DIR)

            if f.lower().endswith(".pdf")

        ]

        if arquivos:

            arquivos.sort(
                key=lambda x: os.path.getmtime(
                    os.path.join(TEMP_DIR, x)
                ),
                reverse=True
            )

            return os.path.join(
                TEMP_DIR,
                arquivos[0]
            )

        time.sleep(1)

    return None

# ============================================================
# EXTRAÇÃO TEXTO PDF
# ============================================================

def extrair_texto_pdf(caminho_pdf):

    try:

        texto = ""

        with open(
            caminho_pdf,
            "rb"
        ) as arquivo:

            leitor = PyPDF2.PdfReader(
                arquivo
            )

            for pagina in leitor.pages:

                conteudo = pagina.extract_text()

                if conteudo:
                    texto += conteudo + "\n"

        return texto.upper()

    except Exception:

        return ""

# ============================================================
# VALIDAÇÃO PDF
# ============================================================

def validar_pdf_por_placa(
    caminho_pdf,
    placa
):

    texto = extrair_texto_pdf(
        caminho_pdf
    )

    placa_limpa = re.sub(
        r"[^A-Z0-9]",
        "",
        placa.upper()
    )

    return placa_limpa in texto

# ============================================================
# DOWNLOAD DOCUMENTO
# ============================================================

def baixar_documento(
    placa,
    documento,
    pos_documento,
    pos_botao_busca
):

    pyautogui.click(pos_documento)

    pyautogui.hotkey("ctrl", "a")

    pyautogui.press("backspace")

    pyautogui.write(documento)

    pyautogui.press("tab")

    pyautogui.write(placa)

    pyautogui.click(pos_botao_busca)

    time.sleep(TEMPO_ESPERA_RESULTADO)

    pyautogui.press("enter")

    caminho_pdf = esperar_download()

    if not caminho_pdf:

        raise RuntimeError(
            "DOWNLOAD NÃO IDENTIFICADO"
        )

    if not validar_pdf_por_placa(
        caminho_pdf,
        placa
    ):

        raise RuntimeError(
            "PDF NÃO CORRESPONDE À PLACA"
        )

    return caminho_pdf

# ============================================================
# PROCESSAMENTO
# ============================================================

def processar_registro(
    reg,
    pos_documento,
    pos_botao_busca
):

    placa = reg["PLACA"]

    documento = reg["DOCUMENTO"]

    for tentativa in range(
        1,
        MAX_TENTATIVAS + 1
    ):

        try:

            print()

            print(
                f"🚗 PLACA: {placa}"
            )

            print(
                f"📄 Tentativa: {tentativa}"
            )

            caminho_pdf = baixar_documento(

                placa,
                documento,

                pos_documento,

                pos_botao_busca

            )

            novo_nome = (
                f"{placa}_CRLV.pdf"
            )

            destino = os.path.join(
                OUTPUT_DIR,
                novo_nome
            )

            shutil.move(
                caminho_pdf,
                destino
            )

            print(
                "✅ Documento salvo."
            )

            return {

                "PLACA": placa,

                "DOCUMENTO": documento,

                "STATUS": "SUCESSO",

                "ARQUIVO": novo_nome,

                "EXECUCAO_ID": EXECUCAO_ID,

                "VERSAO_SISTEMA": VERSAO_SISTEMA,

                "DATA_HORA": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            }

        except Exception as e:

            print(
                f"❌ Erro: {e}"
            )

            if tentativa == MAX_TENTATIVAS:

                return {

                    "PLACA": placa,

                    "DOCUMENTO": documento,

                    "STATUS": "ERRO",

                    "ERRO": str(e),

                    "EXECUCAO_ID": EXECUCAO_ID,

                    "VERSAO_SISTEMA": VERSAO_SISTEMA,

                }

# ============================================================
# EXPORTAÇÃO
# ============================================================

def salvar_resultado_excel(
    resultados
):

    if not resultados:
        return ""

    df = pd.DataFrame(resultados)

    caminho = os.path.join(

        OUTPUT_DIR,

        f"RESULTADO_DOCUMENTOS_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    )

    df.to_excel(
        caminho,
        index=False
    )

    return caminho

# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main():

    print("=" * 60)

    print(
        "VEHICLE DOCUMENT ACQUISITION ENGINE"
    )

    print("=" * 60)

    input(
        "\nAbra o sistema externo "
        "e pressione ENTER..."
    )

    registros = carregar_registros()

    if not registros:

        print(
            "\n⛔ Nenhum registro encontrado."
        )

        return

    pos_documento = calibrar(
        "CAMPO DOCUMENTO"
    )

    pos_botao_busca = calibrar(
        "BOTÃO CONSULTAR"
    )

    resultados = []

    total = len(registros)

    for idx, reg in enumerate(
        registros,
        start=1
    ):

        print()

        print(
            f"📦 PROCESSANDO "
            f"{idx}/{total}"
        )

        resultado = processar_registro(

            reg,

            pos_documento,

            pos_botao_busca

        )

        resultados.append(resultado)

    caminho_excel = salvar_resultado_excel(
        resultados
    )

    print()

    print(
        "📄 Resultado final:"
    )

    print(caminho_excel)

    print()

    print("=" * 60)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
