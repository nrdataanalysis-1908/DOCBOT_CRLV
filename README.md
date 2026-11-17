# DOCBOT_CRLV

Conjunto de módulos Python para processamento documental veicular, normalização de planilhas e automação assistida de consultas. O repositório já contém código executável e testes; ainda não constitui uma aplicação integrada com instalador, interface única ou fluxo ponta a ponta validado em ambiente real.

## Estado atual

> Estado: em desenvolvimento; os módulos ainda não formam uma aplicação integrada.

Os componentes são independentes e possuem maturidades distintas:

| Módulo | Implementação disponível | Limite conhecido |
|---|---|---|
| Motor CRLV | Leitura de PDF com PyPDF2, extração de texto e identificação de campos veiculares | A qualidade depende do texto efetivamente presente no PDF; não há garantia de OCR para documentos digitalizados como imagem |
| Normalização de datasets | Leitura de XLSX, limpeza de cabeçalhos, normalização de datas brasileiras/ISO, mapeamento de UF e organização de colunas | O processamento é orientado a arquivos e não é exposto por uma API pública |
| Geração de links documentais | Leitura de planilha, identificação de placa/arquivo e composição de URLs documentais | Requer uma base documental fornecida pelo operador |
| Aquisição documental | Automação assistida de navegador/desktop, leitura de planilhas, tentativas de download e processamento temporário de PDFs | Depende de sessão gráfica, coordenadas/configuração local e comportamento do sistema externo |
| Consulta de restrições | Automação assistida de consultas veiculares em lote, com status e salvamento parcial | Depende do ambiente desktop e do serviço consultado; não há integração de API pública documentada |

## Estrutura do código

- `core/crlv_document_engine.py`: motor de interpretação de PDFs CRLV.
- `core/robots/robots/core/core/dataset_normalization_engine.py`: normalização e publicação de planilhas.
- `core/robots/robots/core/document_link_generation_engine.py`: geração de links documentais a partir de planilhas.
- `core/robots/robots/vehicle_document_acquisition_engine.py`: aquisição documental assistida.
- `core/robots/vehicle_restriction_query_engine.py`: consulta veicular assistida.

Os scripts não devem ser tratados como um único pipeline operacional. Cada módulo precisa ser configurado e validado conforme seu ambiente de execução.

## Qualidade e testes

A suíte automatizada atual cobre principalmente o módulo de normalização:

- importação do normalizador sem efeitos colaterais de criação de diretórios;
- preservação do arquivo de saída anterior quando a gravação de uma nova planilha falha;
- normalização de datas brasileiras e datas ISO;
- validação do contrato de colunas e do esquema de saída.

Execute os testes com:

```powershell
python -m pip install -r requirements-test.txt
python -m pytest -q
```

O GitHub Actions executa a suíte em Python 3.11 para eventos de push na `main`, pull requests direcionados à `main` e execução manual.

Os testes automatizados não substituem a validação ponta a ponta dos módulos que controlam navegador, teclado, mouse, downloads ou serviços externos.

## Dependências e ambiente

O arquivo `requirements.txt` declara as dependências de runtime dos módulos de processamento documental e planilhas. As bibliotecas de automação desktop (`pyautogui`, `pyperclip` e `keyboard`) usam marcadores de ambiente para instalação somente no Windows.

O arquivo `requirements-test.txt` reutiliza o manifesto de runtime e acrescenta o pytest. Instale o ambiente de execução com `python -m pip install -r requirements.txt` e o ambiente de testes com `python -m pip install -r requirements-test.txt`.

As versões são declaradas por limites mínimos, não por lockfile; a reprodução bit a bit do ambiente ainda requer uma estratégia futura de travamento de versões.

Os fluxos de automação desktop devem ser executados em ambiente Windows interativo, com as permissões e aplicações externas exigidas por cada módulo.

## Segurança e privacidade

- Utilize documentos sintéticos ou anonimizados em testes.
- Não versionar CRLVs reais, planilhas de clientes, placas associadas a pessoas, chaves de acesso ou arquivos temporários de consultas.
- Não considerar dados extraídos como validados sem aplicar regras de consistência e revisão.
- Tratar resultados de serviços externos como dados sujeitos a conferência.
- Validar caminhos e destinos de saída antes de processar documentos em lote.

## Próximas etapas técnicas

1. Consolidar dependências de runtime por módulo e documentar versões suportadas.
2. Definir contratos versionados para os campos extraídos e normalizados.
3. Isolar efeitos colaterais de inicialização e padronizar pontos de entrada.
4. Criar fixtures sintéticas de PDFs e planilhas para ampliar testes de regressão.
5. Introduzir testes de integração com adaptadores externos simulados.
6. Separar automação de interface da lógica de domínio para reduzir dependência de coordenadas e estado visual.
7. Definir um fluxo de execução integrado somente depois que os contratos de cada módulo estiverem estáveis.

## Licença e uso

Consulte os avisos de autoria presentes nos módulos e a situação jurídica do repositório antes de redistribuir ou utilizar comercialmente qualquer componente. A existência de código no GitHub não concede, por si só, direitos de reutilização.
