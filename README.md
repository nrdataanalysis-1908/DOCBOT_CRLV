# DOCBOT_CRLV

A batch-processing tool for CRLV vehicle registration documents, designed to read files from a selected folder and consolidate the extracted data into an Excel spreadsheet in the source folder.

> Repository status: initial specification. The presence of this document does not mean that the reader, field extraction, or export functionality has been implemented.

## Operational objective

Reduce the manual effort involved in reviewing CRLV documents by allowing users to select a folder containing multiple documents, run batch processing, and obtain a consolidated file for review.

## Expected workflow

1. The user starts the application.
2. Selects the folder containing the CRLV documents.
3. The application identifies supported files and processes each document individually.
4. Recognized fields are normalized and associated with their source file.
5. Reading failures are recorded per document without unnecessarily interrupting the batch.
6. A consolidated Excel file is saved in the selected folder.

## Functional requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| FR-01 | Folder selection | The user selects the folder through the system interface |
| FR-02 | Batch scanning | Every supported file is considered exactly once |
| FR-03 | Traceability | Each row retains the source file name |
| FR-04 | Extraction | Recognized fields are stored without inventing missing values |
| FR-05 | Failure handling | An unreadable document receives its own status/error and does not discard other results |
| FR-06 | Export | A consolidated Excel spreadsheet is saved in the selected folder |
| FR-07 | Re-execution | The generated spreadsheet must not be treated as an input document |

## Quality and security

- Do not populate fields that were not actually identified in the document.
- Distinguish between a missing field, an unreadable field, and a validated field.
- Preserve the relationship between each result and its source file.
- Avoid overwriting input documents.
- Handle invalid, protected, or corrupted PDFs without interrupting the entire batch.
- Do not log sensitive document content unnecessarily.
- Use synthetic or anonymized documents in tests.

## Suggested spreadsheet structure

The final structure must reflect the fields actually supported by the extractor. As an operational baseline, consider including:

- source_file;
- processing_status;
- extracted_fields;
- validation_notes;
- error_message, when applicable.

CRLV field names and types must be defined in a versioned contract before implementing the extractor.

## Validation plan

- [ ] A valid PDF with readable fields.
- [ ] A PDF with missing fields.
- [ ] An unreadable or corrupted PDF.
- [ ] An empty folder and a folder without PDFs.
- [ ] A batch containing a mixture of valid and invalid documents.
- [ ] Re-execution without processing the output spreadsheet as an input.
- [ ] Verification that the Excel file was saved in the selected directory.

## Next step

Inspect the reader implementation, define the extracted-field contract, and turn the criteria above into automated tests.
