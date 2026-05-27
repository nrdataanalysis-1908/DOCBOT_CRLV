# ============================================================
# SOFTWARE PROPRIETÁRIO
#
# VEHICLE RESTRICTION QUERY ENGINE
# SISTEMA DE CONSULTA E VALIDAÇÃO VEICULAR
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
import hashlib
import unicodedata
from datetime import datetime

import keyboard
import pandas as pd
import pyautogui
import pyperclip

# ============================================================
# IDENTIFICAÇÃO DO SISTEMA
# ============================================================

EXECUCAO_ID = str(uuid.uuid4())

NOME_SISTEMA = "VEHICLE_RESTRICTION_QUERY_ENGINE"

VERSAO_SISTEMA = "2.0.0"

AUTOR = "NADISON ROBERTO FERREIRA RIBEIRO MINTO"

DATA_EXECUCAO = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)

ASSINATURA_SISTEMA = hashlib.sha256(
    f"{NOME_SISTEMA}_{VERSAO_SISTEMA}_{AUTOR}".encode()
).hexdigest()

# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CONFIG_DIR = os.path.join(BASE_DIR, "..", "config")

OUTPUT_DIR = os.path.join(BASE_DIR, "..", "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

ARQUIVO_EXCEL = os.path.join(
    OUTPUT_DIR,
    "entrada_consulta_veicular.xlsx"
)

TEMPO_ESPERA_RESULTADO = 8
TEMPO_ESPERA_VOLTAR = 3
SALVAR_PARCIAL_A_CADA = 50

ABORTAR_PROCESSO = False
ERROS = []

# ============================================================
# EXCEÇÕES CUSTOMIZADAS
# ============================================================

class VeiculoNaoCadastradoError(Exception):
    pass

# ============================================================
# ESTRUTURA DE SAÍDA
# ============================================================

COLUNAS_SAIDA = [
    "PLACA",
    "CHASSI",
    "MARCA",
    "MUNICIPIO",
    "ANO_FABRICACAO",
    "ANO_MODELO",
    "IPVA",
    "PARCELA_IPVA",
    "SEGURO_PAGO",
    "PARCELA_SEGURO",
    "SEGURO_PAGO_ANTERIOR",
    "PARCELA_SEGURO_ANTERIOR",
    "TAXA_LICENCIAMENTO_PAGA",
    "DATA_LICENCIAMENTO",
    "SITUACAO_LICENCIAMENTO",
    "QTD_AUTUACOES",
    "QTD_MULTAS",
    "STATUS_CONSULTA",
    "ERRO",
    "DATA_HORA",
    "EXECUCAO_ID",
    "VERSAO_SISTEMA",
]

# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto(texto):

    texto = str(texto).upper()

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    texto = "".join(
        ch for ch in texto
        if unicodedata.category(ch) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def limpar(valor):

    if pd.isna(valor):
        return ""

    return str(valor).strip().upper()

# ============================================================
# ESPERA SEGURA
# ============================================================

def sleep_seguro(segundos):

    global ABORTAR_PROCESSO

    inicio = time.time()

    while time.time() - inicio < segundos:

        if keyboard.is_pressed("esc"):

            op = perguntar_acao_erro(
                "ESC pressionado durante espera."
            )

            if op == "P":

                ABORTAR_PROCESSO = True

                raise RuntimeError(
                    "PROCESSO PAUSADO PELO OPERADOR"
                )

            if op == "S":

                raise RuntimeError(
                    "REGISTRO PULADO PELO OPERADOR"
                )

            if op == "C":
                return

        time.sleep(0.2)

# ============================================================
# CARREGAMENTO DE DADOS
# ============================================================

def carregar_dados():

    df = pd.read_excel(ARQUIVO_EXCEL)

    registros = []

    for idx, row in df.iterrows():

        placa = limpar(
            row.iloc[0] if len(row) > 0 else ""
        )

        chassi = limpar(
            row.iloc[1] if len(row) > 1 else ""
        )

        placa = "".join(
            ch for ch in placa
            if ch.isalnum()
        )

        chassi = "".join(
            ch for ch in chassi
            if ch.isalnum()
        )

        if not placa or not chassi:
            continue

        registros.append({

            "INDICE_ORIGINAL": idx + 1,

            "PLACA": placa,

            "CHASSI": chassi,

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

    sleep_seguro(5)

    pos = pyautogui.position()

    print(f"📍 {nome}: {pos}")

    return pos

# ============================================================
# CAPTURA DE TELA
# ============================================================

def copiar_tela():

    pyperclip.copy("")

    sleep_seguro(0.3)

    pyautogui.hotkey("ctrl", "a")

    sleep_seguro(0.3)

    pyautogui.hotkey("ctrl", "c")

    sleep_seguro(1)

    texto = pyperclip.paste()

    return texto.strip()

# ============================================================
# ESPERA RESULTADO
# ============================================================

def esperar_resultado(
    max_tempo=TEMPO_ESPERA_RESULTADO
):

    inicio = time.time()

    ultimo_texto = ""

    while time.time() - inicio <= max_tempo:

        texto = copiar_tela()

        ultimo_texto = texto

        texto_norm = normalizar_texto(texto)

        if (
            "VEICULO NAO CADASTRADO"
            in texto_norm
        ):
            return texto

        if (
            "PLACA" in texto_norm
            and (
                "MARCA" in texto_norm
                or "IPVA" in texto_norm
            )
        ):
            return texto

        sleep_seguro(0.5)

    return ultimo_texto

# ============================================================
# EXTRAÇÃO DE AUTUAÇÕES
# ============================================================

def extrair_autuacoes_multas(
    texto,
    dados
):

    texto_norm = normalizar_texto(texto)

    m_aut = re.search(
        r"(\d+)\s+AUTUAC",
        texto_norm
    )

    if m_aut:

        qtd = m_aut.group(1)

        dados["QTD_AUTUACOES"] = (
            qtd if qtd != "0"
            else "NÃO"
        )

    m_multa = re.search(
        r"(\d+)\s+MULTA",
        texto_norm
    )

    if m_multa:

        qtd = m_multa.group(1)

        dados["QTD_MULTAS"] = (
            qtd if qtd != "0"
            else "NÃO"
        )

# ============================================================
# EXTRAÇÃO PRINCIPAL
# ============================================================

def extrair_dados(texto):

    linhas = [

        l.strip()

        for l in texto.splitlines()

        if l.strip()

    ]

    dados = {

        "PLACA": "",
        "CHASSI": "",
        "MARCA": "",
        "MUNICIPIO": "",
        "ANO_FABRICACAO": "",
        "ANO_MODELO": "",
        "IPVA": "",
        "PARCELA_IPVA": "",
        "SEGURO_PAGO": "",
        "PARCELA_SEGURO": "",
        "SEGURO_PAGO_ANTERIOR": "",
        "PARCELA_SEGURO_ANTERIOR": "",
        "TAXA_LICENCIAMENTO_PAGA": "",
        "DATA_LICENCIAMENTO": "",
        "SITUACAO_LICENCIAMENTO": "",
        "QTD_AUTUACOES": "NÃO",
        "QTD_MULTAS": "NÃO",
        "STATUS_CONSULTA": "OK",
        "ERRO": "",

    }

    extrair_autuacoes_multas(
        texto,
        dados
    )

    parcela_count = 0

    for i in range(len(linhas)):

        l = normalizar_texto(linhas[i])

        if (
            l == "PLACA"
            and i + 1 < len(linhas)
        ):
            dados["PLACA"] = linhas[i + 1]

        elif (
            l == "MARCA"
            and i + 1 < len(linhas)
        ):
            dados["MARCA"] = linhas[i + 1]

        elif (
            "MUNIC" in l
            and i + 1 < len(linhas)
        ):
            dados["MUNICIPIO"] = linhas[i + 1]

    return dados

# ============================================================
# VALIDAÇÃO
# ============================================================

def validar_tela_resultado(texto):

    if texto.strip() == "":

        raise RuntimeError(
            "Nada foi copiado da tela."
        )

    texto_norm = normalizar_texto(texto)

    if (
        "VEICULO NAO CADASTRADO"
        in texto_norm
    ):

        raise VeiculoNaoCadastradoError(
            "VEÍCULO NÃO CADASTRADO"
        )

    if (
        "PLACA" not in texto_norm
        or "MARCA" not in texto_norm
    ):

        raise RuntimeError(
            "Tela inesperada detectada."
        )

# ============================================================
# CONSULTA
# ============================================================

def consultar(
    reg,
    pos_placa
):

    placa = reg["PLACA"]

    chassi = reg["CHASSI"]

    pyautogui.click(pos_placa)

    sleep_seguro(0.3)

    pyautogui.hotkey("ctrl", "a")

    pyautogui.press("backspace")

    pyautogui.write(placa)

    pyautogui.press("tab")

    sleep_seguro(0.3)

    pyautogui.hotkey("ctrl", "a")

    pyautogui.press("backspace")

    pyautogui.write(chassi)

    pyautogui.press("tab")

    sleep_seguro(0.3)

    pyautogui.press("enter")

    texto = esperar_resultado()

    validar_tela_resultado(texto)

    dados = extrair_dados(texto)

    dados["PLACA"] = placa

    dados["CHASSI"] = chassi

    dados["DATA_HORA"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    dados["EXECUCAO_ID"] = EXECUCAO_ID

    dados["VERSAO_SISTEMA"] = VERSAO_SISTEMA

    return dados

# ============================================================
# EXPORTAÇÃO
# ============================================================

def salvar_excel(
    resultados,
    nome_base
):

    if not resultados:
        return ""

    df = pd.DataFrame(resultados)

    caminho = os.path.join(

        OUTPUT_DIR,

        f"{nome_base}_"
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
        "VEHICLE RESTRICTION QUERY ENGINE"
    )

    print("=" * 60)

    resultados = []

    input(
        "\nAbra o sistema de consulta "
        "e pressione ENTER..."
    )

    registros = carregar_dados()

    if not registros:

        print(
            "\n⛔ Nenhum registro encontrado."
        )

        return

    pos_placa = calibrar(
        "CAMPO PLACA"
    )

    total = len(registros)

    for idx, reg in enumerate(
        registros,
        start=1
    ):

        try:

            print()

            print(
                f"🚗 {idx}/{total} | "
                f"PLACA: {reg['PLACA']}"
            )

            dados = consultar(
                reg,
                pos_placa
            )

            resultados.append(dados)

            print(
                "✅ Consulta concluída."
            )

        except Exception as e:

            print(
                f"❌ Erro: {e}"
            )

    caminho_final = salvar_excel(
        resultados,
        "RESULTADO_CONSULTA_VEICULAR"
    )

    print()

    print(
        "📄 Resultado salvo:"
    )

    print(caminho_final)

    print()

    print("=" * 60)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
