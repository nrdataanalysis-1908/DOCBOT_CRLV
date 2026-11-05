# ============================================================
# SOFTWARE PROPRIETÁRIO
#
# DOCUMENT INTELLIGENCE ENGINE
# MOTOR DE INTERPRETAÇÃO DOCUMENTAL VEICULAR
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
import uuid
import warnings
import hashlib
from datetime import datetime

import PyPDF2
from PyPDF2.errors import PdfReadWarning, PdfReadError

warnings.filterwarnings("ignore", category=PdfReadWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ============================================================
# IDENTIFICAÇÃO DO SISTEMA
# ============================================================

EXECUCAO_ID = str(uuid.uuid4())

NOME_SISTEMA = "DOCUMENT_INTELLIGENCE_ENGINE"

MODULO = "CRLV_DOCUMENT_PARSER"

VERSAO_SISTEMA = "2.0.0"

AUTOR = "NADISON ROBERTO FERREIRA RIBEIRO MINTO"

DIREITOS_AUTORAIS = "© TODOS OS DIREITOS RESERVADOS"

DATA_EXECUCAO = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

ASSINATURA_SISTEMA = hashlib.sha256(
    f"{NOME_SISTEMA}_{VERSAO_SISTEMA}_{AUTOR}".encode()
).hexdigest()

# ============================================================
# EXPRESSÕES REGULARES
# ============================================================

REGEX_PLACA = re.compile(r"([A-Z]{3}\d[A-Z0-9]\d{2})")

# ============================================================
# CAMPOS ESTRUTURADOS DO CRLV
# ============================================================

CAMPOS_COMPLETOS_CRLV = [
    "EXERCICIO",
    "ANO_FABRICACAO",
    "ANO_MODELO",
    "CODIGO_SEGURANCA_CLA",
    "CATEGORIA_CLA",
    "MARCA_MODELO_VERSAO",
    "ESPECIE_TIPO",
    "PLACA_ANTERIOR_UF",
    "CHASSI",
    "COR_PREDOMINANTE",
    "COMBUSTIVEL",
    "CATEGORIA",
    "CAPACIDADE",
    "POTENCIA_CILINDRADA",
    "PESO_BRUTO_TOTAL",
    "CMT",
    "EIXOS",
    "LOTACAO",
    "CARROCERIA",
    "DATA_DOCUMENTO",
    "DATA_EMISSAO",
    "HORA_EMISSAO",
]

# ============================================================
# LEITURA PDF
# ============================================================

def extrair_texto_pdf(caminho_pdf):

    try:

        with open(caminho_pdf, "rb") as arquivo:

            try:
                leitor = PyPDF2.PdfReader(
                    arquivo,
                    strict=False
                )

            except (PdfReadError, Exception):
                return "__ERRO_PDF__"

            texto = ""

            for pagina in leitor.pages:

                try:
                    conteudo = pagina.extract_text()

                    if conteudo:
                        texto += conteudo + "\n"

                except Exception:
                    return "__ERRO_PDF__"

            return texto if texto.strip() else "__ERRO_PDF__"

    except Exception:
        return "__ERRO_PDF__"


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalizar_texto_pdf(texto):

    if texto == "__ERRO_PDF__" or not texto:
        return []

    return [
        linha.strip()
        for linha in texto.splitlines()
        if linha.strip()
    ]


# ============================================================
# EXTRAÇÃO PLACA
# ============================================================

def extrair_placa(texto):

    if not texto:
        return "PLACA_NAO_ENCONTRADA"

    match = REGEX_PLACA.search(texto.upper())

    if match:
        return match.group(1)

    return "PLACA_NAO_ENCONTRADA"


# ============================================================
# EXTRAÇÃO MOTOR + CRV
# ============================================================

def extrair_motor_crv(texto):

    if texto == "__ERRO_PDF__" or not texto:
        return "ERRO", "ERRO"

    linhas = normalizar_texto_pdf(texto)

    motor = "ERRO"
    crv = "ERRO"

    for i, linha in enumerate(linhas):

        if re.search(r"\b20\d{2}\s+20\d{2}\b", linha):

            for j in range(i + 1, min(i + 8, len(linhas))):

                numeros = re.findall(
                    r"\b\d{9,12}\b",
                    linhas[j]
                )

                if numeros:
                    crv = numeros[0]
                    break

            break

    def limpar_motor(valor):

        valor = str(valor).upper().strip()

        valor = valor.replace(" ", "")

        valor = valor.strip(".,;:/|()[]{}")

        if not valor:
            return ""

        if not re.search(r"\d", valor):
            return ""

        if len(valor) < 6 or len(valor) > 25:
            return ""

        if REGEX_PLACA.fullmatch(valor):
            return ""

        if re.fullmatch(r"19\d{2}|20\d{2}", valor):
            return ""

        if re.fullmatch(r"[A-Z0-9][A-Z0-9*\-]{5,24}", valor):
            return valor

        return ""

    for i, linha in enumerate(linhas):

        if re.search(
            r"\d+\s*CV\s*/\s*(?:\d+|\*+)",
            linha.upper()
        ):

            janela = linhas[i + 1:i + 6]

            for prox in janela:

                partes = re.split(
                    r"\s+",
                    prox.upper()
                )

                for parte in partes:

                    motor_ok = limpar_motor(parte)

                    if motor_ok:
                        motor = motor_ok
                        return motor, crv

    return motor, crv


# ============================================================
# EXTRAÇÃO OBSERVAÇÕES
# ============================================================

def extrair_observacao(texto):

    if texto == "__ERRO_PDF__":
        return "ERRO"

    linhas = [
        l.strip()
        for l in texto.splitlines()
        if l.strip()
    ]

    up = [l.upper() for l in linhas]

    padroes = [

        ("ALIENA", "FIDU"),
        ("RECALL",),
        ("BLINDAD",),
        ("RESTRI", "ROUB"),
        ("RESTRI", "FURT"),
        ("SINISTRO", "MEDIA", "MONTA"),
        ("GNV",),
        ("COMODAT",),
        ("INTRANSFER",),

    ]

    observacoes = []

    for i, up_line in enumerate(up):

        for padrao in padroes:

            if all(p in up_line for p in padrao):
                observacoes.append(linhas[i])
                break

    if not observacoes:
        return "SEM OBSERVACOES"

    return " | ".join(
        list(dict.fromkeys(observacoes))
    )


# ============================================================
# EXTRAÇÃO DADOS COMPLETOS CRLV
# ============================================================

def extrair_dados_completos_crlv(texto):

    dados = {
        campo: ""
        for campo in CAMPOS_COMPLETOS_CRLV
    }

    if texto == "__ERRO_PDF__" or not texto:
        return dados

    linhas = normalizar_texto_pdf(texto)

    texto_completo = chr(10).join(linhas)

    match_emissao = re.search(

        r"Documento emitido por .*? em "
        r"([0-9]{2}/[0-9]{2}/[0-9]{4}) "
        r"às "
        r"([0-9]{2}:[0-9]{2}:[0-9]{2})",

        texto_completo,
        flags=re.IGNORECASE,

    )

    if match_emissao:

        dados["DATA_EMISSAO"] = match_emissao.group(1)

        dados["HORA_EMISSAO"] = match_emissao.group(2)

    idx_placa = None

    for i, linha in enumerate(linhas):

        if re.fullmatch(
            r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2} +20[0-9]{2}",
            linha.upper().strip()
        ):

            idx_placa = i
            break

    if idx_placa is None:
        return dados

    vals = linhas[idx_placa:]

    def linha(pos):
        return vals[pos].strip() if 0 <= pos < len(vals) else ""

    match = re.fullmatch(

        r"([A-Z]{3}[0-9][A-Z0-9][0-9]{2}) +(20[0-9]{2})",

        linha(0).upper()

    )

    if match:
        dados["EXERCICIO"] = match.group(2)

    match = re.fullmatch(

        r"(19[0-9]{2}|20[0-9]{2}) "
        r"+"
        r"(19[0-9]{2}|20[0-9]{2})",

        linha(1)

    )

    if match:

        dados["ANO_FABRICACAO"] = match.group(1)

        dados["ANO_MODELO"] = match.group(2)

    dados["MARCA_MODELO_VERSAO"] = linha(4)

    dados["ESPECIE_TIPO"] = linha(5)

    return dados


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def processar_documento_crlv(caminho_pdf):

    texto = extrair_texto_pdf(caminho_pdf)

    placa = extrair_placa(texto)

    motor, crv = extrair_motor_crv(texto)

    observacoes = extrair_observacao(texto)

    dados = extrair_dados_completos_crlv(texto)

    resultado = {

        "PLACA": placa,

        "MOTOR": motor,

        "CRV": crv,

        "OBSERVACOES": observacoes,

        "ARQUIVO_ORIGEM": os.path.basename(caminho_pdf),

        "EXECUCAO_ID": EXECUCAO_ID,

        "VERSAO_SISTEMA": VERSAO_SISTEMA,

        "AUTOR": AUTOR,

        "ASSINATURA_SISTEMA": ASSINATURA_SISTEMA,

        "DATA_EXECUCAO": DATA_EXECUCAO,

    }

    resultado.update(dados)

    return resultado


# ============================================================
# EXECUÇÃO MANUAL
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("DOCUMENT INTELLIGENCE ENGINE")
    print("Desenvolvido por Nadison Roberto | NR TECH | © 2026")
    print("=" * 60)

    caminho = input(
        "\nInforme o caminho do PDF CRLV: "
    ).strip().strip('"')

    if not os.path.isfile(caminho):

        print("\n❌ Arquivo não encontrado.")

    else:

        resultado = processar_documento_crlv(caminho)

        print("\n✅ DOCUMENTO PROCESSADO\n")

        for chave, valor in resultado.items():

            print(f"{chave}: {valor}")

    print("\n" + "=" * 60)
