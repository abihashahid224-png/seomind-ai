# SEOmind AI
**🔗 Live app:** https://seomind-ai-rjegjavhuvllwrcqn5hxxd.streamlit.app/

SEOmind AI is a web app that helps bloggers and small business owners improve their blog posts for search engines. You paste your blog content, and six AI agents, each powered by Gemma 4, return keyword ideas, SEO titles, meta descriptions, a content quality review, heading suggestions, internal link ideas, and a full rewritten version of your post.

The project was built for the **Hacktoberfest Hack Day** challenges:
- Best Open-Source AI Project
- Best Use of Gemma 4

---

## Table of contents

- [Problem](#problem)
- [Features](#features)
- [How it works](#how-it-works)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Agents and skill files](#agents-and-skill-files)
- [Model and fallback](#model-and-fallback)
- [Setup and run locally](#setup-and-run-locally)
- [Deployment (Streamlit Community Cloud)](#deployment-streamlit-community-cloud)
- [Troubleshooting](#troubleshooting)
- [Future plans](#future-plans)
- [Security notes](#security-notes)
- [License](#license)

---

## Problem

Many bloggers write useful content but their posts do not rank on Google. Common reasons include:
- They do not know which keywords people search for.
- Their titles and meta descriptions are weak or too long.
- Headings do not follow a clear structure.
- Posts do not link to related articles on the same site.

SEO tools can solve these, but many are expensive or hard for beginners. SEOmind AI gives free, plain-language suggestions in one place.

## Features

- **Keyword research:** primary, secondary, and long-tail keywords, with attention to search intent (maximum 10 keywords).
- **Title and meta:** 3 SEO titles (up to 60 characters each) and 2 meta descriptions (up to 160 characters each).
- **Content analysis:** a list of issues related to length, readability, and keyword use, plus an SEO score from 1 to 10.
- **Heading optimization:** one H1 and a list of H2 suggestions.
- **Internal linking:** up to 3 link ideas, each with anchor text and a target topic.
- **Rewrite:** an improved version of the post that applies the suggestions from the other agents, plus a list of the changes made.
- **Agent selection:** you can choose which agents to run from a dropdown.
- **Error handling:** retries and a backup model if the main model is busy.

## How it works

1. The user pastes blog content into the Streamlit web page.
2. The user selects agents (all six are selected by default) and clicks **Analyze**.
3. `orchestrator.py` runs the selected agents **in a fixed order**: keywords, title_meta, content, headings, linking, rewrite.
4. Each agent in `agents.py`:
   - loads its instructions from `skills/<skill-name>/SKILL.md`,
   - combines those instructions with the blog content and the outputs of earlier agents,
   - sends the prompt to Gemma 4 through the Gemini API,
   - parses the reply as JSON.
5. The orchestrator collects all results in one dictionary.
6. `app.py` shows each agent's result as a section, using JSON views. If the model returns text that is not valid JSON, the raw text is shown instead, so nothing is lost.

Because the rewrite agent runs last, it can use the keywords, titles, issues, headings, and links found by the earlier agents.

## Technology stack

| Layer | Tool or service | Purpose |
|---|---|---|
| Language | Python 3.14 | All backend and UI code |
| Web UI | Streamlit | Text box, dropdown, buttons, and results display |
| AI model | Gemma 4 (`gemma-4-26b-a4b-it`, backup `gemma-4-31b-it`) | Generates keywords, titles, analysis, headings, links, and rewrite |
| Model access | Google Gemini API via Google AI Studio | Hosts and serves Gemma 4 |
| SDK | `google-genai` | Python client for the Gemini API |
| Config | `python-dotenv` | Loads `GEMINI_API_KEY` from a `.env` file |
| Version control | Git and GitHub | Source code hosting (public repository) |
| Editor | Visual Studio Code | Writing and running code |
| Hosting | Streamlit Community Cloud | Free public deployment of the app |
| License | MIT (this project), Apache 2.0 (Gemma 4 model) | Open-source licensing |

Python packages in `requirements.txt`:
```
streamlit
google-genai
python-dotenv
```

## Project structure

```
seomind-ai/
├── app.py              # Streamlit UI: input box, agent selection, results
├── agents.py           # Generic agent: loads SKILL.md, calls Gemma, parses JSON
├── orchestrator.py     # Runs the selected agents in order and merges results
├── skills/             # One folder per agent, each with a SKILL.md file
│   ├── keyword-research/SKILL.md
│   ├── title-meta/SKILL.md
│   ├── content-analysis/SKILL.md
│   ├── heading-optimization/SKILL.md
│   ├── internal-linking/SKILL.md
│   └── rewrite/SKILL.md
├── requirements.txt    # Python dependencies
├── .gitignore          # Keeps .env and __pycache__ out of GitHub
├── LICENSE             # MIT license
├── list_models.py      # Helper: lists Gemma models available to your API key
├── test.py             # Helper: one test call to check the API connection
└── README.md
```

### What each main file does

- **`app.py`**: Builds the Streamlit page. It reads the text box and agent selection, calls `run_pipeline()`, and displays each result with a subheader.
- **`agents.py`**:
  - `client = genai.Client()` reads `GEMINI_API_KEY` from `.env`.
  - `AGENTS` maps agent names to skill folder names.
  - `load_skill()` reads a `SKILL.md` file and removes the YAML header (the part between `---` lines).
  - `call_gemma()` tries each model in `MODELS` up to two times, waiting 3 seconds between attempts.
  - `parse_json()` removes code fences such as ```` ```json ```` and converts the reply to a Python dictionary.
  - `run_agent()` builds the full prompt and returns the parsed result.
- **`orchestrator.py`**: `run_pipeline()` loops over `AGENTS` in order. Each agent receives the outputs of the earlier agents as JSON text.
- **`skills/*/SKILL.md`**: Plain-language instructions for each agent, with an input description, output JSON keys, and rules.
- **`list_models.py`**: Prints the model names your API key can access. Used to confirm that Gemma 4 is available.
- **`test.py`**: Sends one short prompt to Gemma to confirm that the connection works.

## Agents and skill files

| Agent key | Skill folder | Output JSON keys |
|---|---|---|
| `keywords` | `keyword-research` | `primary`, `secondary`, `long_tail` |
| `title_meta` | `title-meta` | `titles` (3 items), `meta_descriptions` (2 items) |
| `content` | `content-analysis` | `issues` (list), `score` (1 to 10) |
| `headings` | `heading-optimization` | `h1`, `h2_suggestions` |
| `linking` | `internal-linking` | `links` (list of `anchor` and `topic`, up to 3) |
| `rewrite` | `rewrite` | `rewritten_text`, `changes` |

Every skill file uses the same format:

```markdown
---
name: keyword-research
description: Suggest SEO keywords for a blog post
---
# Instructions
- Input: blog content
- Output: JSON with keys "primary", "secondary", "long_tail"
- Rules: follow search intent, return no more than 10 keywords
```

To change how an agent behaves, edit its `SKILL.md`. You do not need to change Python code. To add a new agent, create a new skill folder and add one line to `AGENTS` in `agents.py`.

## Model and fallback

- **Primary model:** `gemma-4-26b-a4b-it`
- **Backup model:** `gemma-4-31b-it`

`call_gemma()` tries the primary model first. If it fails (for example with a `500` server error), it waits and retries, and then moves to the backup model. If both fail, the error is shown in the app.

The model list is defined in `agents.py`:
```python
MODELS = ["gemma-4-26b-a4b-it", "gemma-4-31b-it"]
```

## Setup and run locally

### Requirements
- Python 3.10 or newer (this project was run on Python 3.14)
- Git
- A Google account
- A Gemini API key from Google AI Studio

### Step 1: Get an API key
1. Go to https://aistudio.google.com and sign in with your Google account.
2. Click **Get API key**, then **Create API key**.
3. Copy the key. Keep it private.

### Step 2: Clone the repository
```bash
git clone https://github.com/abihashahid224-png/seomind-ai.git
cd seomind-ai
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create the `.env` file
Create a file named `.env` in the project root (same folder as `app.py`) with this line:
```
GEMINI_API_KEY=your_key_here
```
This file is listed in `.gitignore`, so it will not be uploaded to GitHub.

### Step 5: Check the connection (optional)
```bash
python list_models.py
python test.py
```
`test.py` should print a short answer about APIs.

### Step 6: Run the app
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser, paste a blog post, and click **Analyze**.

### Sample input
```
Coffee is one of the most popular drinks in the world. Many people drink it every morning to feel energized. In this blog, we explain how coffee works, the benefits of drinking coffee, and simple tips to brew a good cup at home. Choosing fresh beans and the right grind size makes a big difference.
```

## Deployment (Streamlit Community Cloud)

1. Push the code to GitHub (the repository must be public).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, then **Deploy a public app from GitHub**.
4. Fill in:
   - Repository: `abihashahid224-png/seomind-ai`
   - Branch: `main`
   - Main file path: `app.py`
5. Open **Advanced settings**, then **Secrets**, and add:
   ```
   GEMINI_API_KEY = "your_key_here"
   ```
   Use straight double quotes and keep it on one line. The key must not be pushed to GitHub.
6. Click **Deploy**. The app will be available at a `*.streamlit.app` link.

Note: `.env` is not uploaded to the cloud. The app reads the key from Streamlit Secrets, and `python-dotenv` only needs `.env` when running locally.

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `500 INTERNAL` error | Google's Gemma server is busy | Wait 1 to 2 minutes and click Analyze again. The backup model is tried automatically. |
| `404 NOT_FOUND` for a model | The model name is retired or unavailable | Run `python list_models.py`, then update `MODELS` in `agents.py`. |
| `streamlit run app.py` says file not found | Terminal is not in the project folder | Run `cd seomind-ai` first, and check that `app.py` is in the root folder. |
| Results show as raw text | The model did not return valid JSON | The output is still shown. Try again, or tighten the rules in the SKILL.md file. |
| Secrets error on deploy | Invalid TOML format | Use `GEMINI_API_KEY = "key"` on one line, with straight quotes. |
| `ModuleNotFoundError` | Missing package | Check that `requirements.txt` lists `streamlit`, `google-genai`, and `python-dotenv`. |

## Future plans

- Analyze a live web page directly by entering its URL.
- Export the report as a PDF or Word file.
- Add Urdu and other language support.
- Save analysis history for each user.
- Add more agents, such as schema markup and image alt text suggestions.
- Add automated tests for the JSON parsing and skill loading.

## Security notes

- The API key is read from `.env` locally and from Streamlit Secrets when deployed. It is never stored in the code.
- `.gitignore` contains `.env` so the key is not pushed to GitHub.
- If a key is ever pushed by mistake, delete it in Google AI Studio and create a new one.

## Acknowledgements

- Google for the Gemma 4 model and the Gemini API.
- Streamlit for the web framework and free hosting.
- Hacktoberfest and MLH for the Hack Day challenges.

## License

- **This project:** MIT License. See [LICENSE](LICENSE).
- **Gemma 4 model:** Apache 2.0. See the [Gemma terms](https://ai.google.dev/gemma/terms) for details.
