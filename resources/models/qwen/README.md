# Qwen resource intake — PAE

Status: **INVENTORIED / ORIGINAL FILE TRANSFER NOT YET VERIFIED**

This folder records the original files Matěj uploaded for the PAE project. It is **not** a claim that their full bytes have already been copied into this GitHub repository or the Google Drive vault.

## Placement

- Canonical PAE project: https://github.com/hssgj/PAE
- Original-file vault target: https://drive.google.com/drive/folders/1arobz3Pz9SQ8Oyp3mJYqUurrPaZpGWGi
- PAE resource registry: this folder, pending checksum/variant verification.
- Supabase: eventual metadata and runtime state, not a binary-file dump.

## Known originals (uploaded 2026-09-11)

- `config.json`
- `tokenizer_config.json`
- `tokenizer.json`
- `merges.txt`
- `vocab.json`
- `vocab (1).json`
- `LICENSE.txt`
- `LICENSE (1).txt`

All eight were located as user uploads in the ChatGPT File Library; the original byte stream has **not** been successfully transferred from that library to connected Google Drive/GitHub storage. Do not treat this inventory as a verified file backup.

## Observed properties (not a complete model ID)

- `config.json` declares architecture `Qwen3_5ForConditionalGeneration` and model type `qwen3_5`.
- The text configuration declares `qwen3_5_text`, vocabulary size 248320 and 262144 max positions.
- The supplied licence files contain Apache License 2.0, with an Alibaba Cloud copyright notice.
- Exact upstream repository, checkpoint version, revision, tokenization compatibility across the duplicated files, original byte hashes and file sizes: **UNKNOWN / NOT YET VERIFIED**.
- Model weights: **not included** in this uploaded set.

## Intake gate

Do **not** merge or rename duplicate uploads until their original bytes can be compared and checksums verified. The two `vocab` names and two `LICENSE` names should remain distinct pending comparison. If a compatible original-byte transfer becomes available, save the files to the Drive vault, record each file URL, size and SHA-256, and only then mark the resource STORED / VERIFIED.

## Continuity

CANON ≠ IDEA. UNKNOWN ≠ INVENTED. This is a resource record, not an implementation of cognition or an executable model.
