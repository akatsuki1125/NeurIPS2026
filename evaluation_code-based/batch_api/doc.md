# Batch API Evaluation Workflow

This folder contains a lightweight pipeline for running evaluation jobs through the Batch APIs of OpenAI, Gemini, and Claude.

The workflow is split into three stages:

1. Generate request JSONL from metadata.
2. Submit the JSONL to the provider-specific Batch API and wait for completion.
3. Extract structured scores from the batch output and save them as CSV.

## 1. Prepare the Inputs

Before running the pipeline, prepare the following files:

- A metadata JSONL file with one record per evaluation example.
- TikZ source files referenced by the metadata records.
- An experiment configuration file in TOML format.
- Provider credentials in the environment, loaded through a `.env` file or your shell.

The metadata records are expected to contain a stable key plus paths to the original, reference, and generated TikZ code. The generator also supports alternate field names and nested generated-code paths, so the same pipeline can be reused across experiments.

Typical metadata fields include:

- `key`
- `org_tikz_code_path`
- `reference_tikz_code_path` or `reference_tikz_path`
- `edited_tikz_code_path`, `generated_tikz_code_path`, `edited_code_path`, or `generated_code_path`
- `question_id` when you need a per-row identifier

If you want to evaluate only a subset of rows, you can optionally provide a CSV file and filter the metadata by the edited image URL key.

## 2. Create an Experiment Config

Each run is controlled by a TOML file that defines one or more experiments. A minimal configuration looks like this:

```toml
[metadata_fields]
key = "key"
org_image_path = "org_image_path"
visual_instruction_image_path = "visual_instruction_image_path"
org_tikz_code_path = "org_tikz_code_path"
text_instruction = "text_instruction"
visual_instruction_model_outputs = "visual_instruction_model_outputs"

[[configs]]
name = "example_openai"
judge_provider = "openai"
judge_model = "gpt-5.4"
metadata_path = "<workspace-root>/data/metadata.jsonl"
save_path = "<workspace-root>/runs/{name}/input.jsonl"
append = false
```

Supported `judge_provider` values are:

- `openai`
- `google`
- `anthropic`

The `judge_model` field should match the model name you want to use for scoring, such as a GPT, Gemini, or Claude model.

If `save_path` is omitted, the generator writes to a default location under `runs/<experiment-name>/input.jsonl`.

## 3. Generate Batch Requests

Use `steps/01_generate_jsonl.py` to build the request JSONL.

Example:

```bash
python steps/01_generate_jsonl.py \
	--config <path-to-config.toml> \
	--config-name example_openai
```

Useful options:

- `--limit <N>`: process only the first `N` examples.
- `--preview`: print the first request without saving it.
- `--amt-csv <path>`: filter examples using an external CSV.
- `--strict-csv-rows`: require every CSV row to match metadata exactly.
- `--gemini-use-local`: send Gemini images as local inline data instead of URLs.

This stage reads the metadata file, loads the referenced TikZ text, and writes a provider-specific request JSONL file. The request format is automatically adapted for each provider:

- OpenAI uses chat-completions batch requests with a strict JSON schema response format.
- Gemini uses batch requests with JSON output settings.
- Claude uses tool-based structured output.

The evaluation prompt compares three artifacts:

- the original TikZ code
- the reference TikZ code
- the generated TikZ code to be judged

## 4. Run the Batch Job

Use `steps/02_run_batch.py` to submit the generated JSONL and wait for the provider response.

Example:

```bash
python steps/02_run_batch.py \
	--config <path-to-config.toml> \
	--config-name example_openai
```

The script selects the provider from the config and calls the matching backend:

- OpenAI: upload the JSONL and create a `/v1/chat/completions` batch job.
- Gemini: upload the JSONL and create a Gemini batch job.
- Claude: submit the JSONL through the messages batch API.

The default output path is derived from the experiment name, usually:

```text
runs/<experiment-name>/output_<experiment-name>.jsonl
```

You can override this with `--batch-output-path`.

## 5. Extract Scores

After the batch finishes, use `steps/03_extract_scores.py` to turn the raw output into a CSV file.

Example:

```bash
python steps/03_extract_scores.py \
	--config <path-to-config.toml> \
	--config-name example_openai
```

By default, the script reads the batch output JSONL from the standard run directory and writes:

```text
runs/<experiment-name>/scores_<experiment-name>.csv
```

The CSV contains one row per successful response and includes the provider-independent score columns extracted from the JSON response.

## 6. Logs and Outputs

The scripts write logs under a local pipeline log directory. Keep these outputs out of public releases if they contain environment-specific details.

Typical outputs are:

- request JSONL: the generated Batch API input
- output JSONL: the raw provider response records
- CSV: the extracted scores
- log files: run-time status and progress messages

## 7. Recommended End-to-End Order

1. Prepare metadata and code files.
2. Write or sanitize the TOML config.
3. Generate request JSONL with `01_generate_jsonl.py`.
4. Submit the batch with `02_run_batch.py`.
5. Extract scores with `03_extract_scores.py`.


## Batch size split

`steps/02_run_batch.py` (and `eval.py code-batch ... run/pipeline`) now split input JSONL into **3 parts by default**, submit them sequentially, and merge outputs into one JSONL.

- Default: `--num-splits 3`
- You can override: `--num-splits <N>`

This helps avoid provider request-size limits (for example HTTP 413).
