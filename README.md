# DOCBOT_CRLV

Ferramenta de processamento em lote de documentos CRLV, concebida para ler arquivos de uma pasta selecionada e consolidar os dados extraídos em uma planilha Excel na própria pasta de origem.

> Estado do repositório: especificação inicial. A presença deste documento não significa que o leitor, a extração de campos ou a exportação estejam implementados.

## Objetivo operacional

Reduzir o trabalho manual de conferência de CRLVs, permitindo selecionar uma pasta com múltiplos documentos, executar a leitura em lote e obter um arquivo consolidado para revisão.

## Fluxo esperado

1. O usuário inicia a aplicação.
2. Seleciona a pasta que contém os CRLVs.
3. A aplicação identifica os arquivos compatíveis e processa cada documento individualmente.
4. Os campos reconhecidos são normalizados e associados ao arquivo de origem.
5. Falhas de leitura são registradas por documento, sem interromper desnecessariamente o lote.
6. Um arquivo Excel consolidado é salvo na mesma pasta selecionada.

## Requisitos funcionais

| ID | Requisito | Critério de aceite |
|---|---|---|
| FR-01 | Seleção de pasta | O usuário escolhe a pasta pela interface do sistema |
| FR-02 | Varredura em lote | Todos os arquivos suportados são considerados uma única vez |
| FR-03 | Rastreabilidade | Cada linha mantém o nome do arquivo de origem |
| FR-04 | Extração | Campos reconhecidos são armazenados sem inventar valores ausentes |
| FR-05 | Tratamento de falhas | Documento ilegível gera status/erro próprio e não elimina os demais resultados |
| FR-06 | Exportação | Uma planilha Excel consolidada é gravada na pasta selecionada |
| FR-07 | Reexecução | A planilha gerada não deve ser tratada como documento de entrada |

## Qualidade e segurança

- Não preencher campos que não tenham sido efetivamente identificados no documento.
- Diferenciar campo ausente, campo ilegível e campo validado.
- Preservar o vínculo entre resultado e arquivo de origem.
- Evitar sobrescrever documentos de entrada.
- Tratar PDFs inválidos, protegidos ou corrompidos sem interromper todo o lote.
- Não registrar conteúdo documental sensível em logs desnecessários.
- Utilizar documentos sintéticos ou anonimizados em testes.

## Estrutura sugerida para a planilha

A estrutura definitiva deve refletir os campos efetivamente suportados pelo extrator. Como base operacional, recomenda-se incluir:

- arquivo_origem;
- status_processamento;
- campos extraídos;
- observacoes_validacao;
- mensagem_erro, quando aplicável.

Os nomes e tipos dos campos do CRLV devem ser definidos em um contrato versionado antes da implementação do extrator.

## Plano de validação

- [ ] Um PDF válido com campos legíveis.
- [ ] Um PDF com campos ausentes.
- [ ] Um PDF ilegível ou corrompido.
- [ ] Pasta vazia e pasta sem PDFs.
- [ ] Lote com documentos válidos e inválidos misturados.
- [ ] Reexecução sem processar a planilha de saída como entrada.
- [ ] Verificação de que o Excel foi salvo no diretório selecionado.

## Próximo passo

Inspecionar a implementação do leitor, definir o contrato dos campos extraídos e transformar os critérios acima em testes automatizados.
