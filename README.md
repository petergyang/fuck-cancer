# Fuck Cancer

Turn a cancer brain dump, medical report, or treatment question into a calm, practical brief with the next steps first.

## Problem

Cancer gives patients and families too much information at the exact moment it becomes hardest to process.

Reports arrive full of unfamiliar terms. Results appear before a doctor has explained them. Family members hear different versions of the plan. Then someone has to research treatments, clinical trials, specialists, records, appointments, and questions while trying to support the person they love.

Most people do not need another giant cancer guide. They need help understanding their situation and deciding what to do next.

## How to install /fuck-cancer

The easiest way to install the skill is to paste this into ChatGPT, Claude Code, Codex, or your favorite coding agent:

```text
Install the /fuck-cancer skill globally from https://github.com/petergyang/fuck-cancer
```

You can also install it with `npx`:

```sh
npx skills add petergyang/fuck-cancer --skill fuck-cancer --global --yes
```

## How to use /fuck-cancer

Start with a brain dump:

```text
/fuck-cancer My dad was just diagnosed. Here is everything I know so far...
```

Paste or upload reports:

```text
/fuck-cancer Help me understand these pathology and imaging reports and prepare for Friday's appointment.
```

Research clinical trials or second opinions:

```text
/fuck-cancer Find relevant clinical trials near Toronto and the three best-fit places for a second opinion.
```

Share new information as it arrives:

```text
/fuck-cancer Update our brief with this new biomarker report and tell me what changed.
```

The skill asks only for missing information that could change the immediate guidance. It does not make you complete a long intake form.

## What this skill does

- **Explains medical information plainly.** It translates pathology, imaging, biomarkers, staging, and treatment language without talking down to you.
- **Puts the next decision first.** It identifies the current priority and turns it into a short, ordered action list.
- **Researches current options.** It uses current guidelines, government sources, peer-reviewed research, and major cancer centers, then summarizes each option in two or three sentences.
- **Finds clinical trials carefully.** It searches the official ClinicalTrials.gov API, checks the individual site's recruitment status, and names the eligibility questions that still need confirmation.
- **Finds focused second opinions.** It returns up to three specialists or centers that fit the cancer type, disease setting, location, and practical constraints.
- **Keeps the family aligned.** It creates a concise brief and updates it when new results or treatment decisions arrive.

## The brief

Every report has no more than three sections:

1. **Current priority.** What needs to happen next and why.
2. **What to do next.** The most useful actions, questions, trials, or second opinions in priority order.
3. **What we know.** A plain-English explanation of the diagnosis, tests, biomarkers, stage, treatment history, and meaningful uncertainty.

Items use a bold stem followed by two or three useful sentences. Sources and the research date appear in a compact footer.

## Encouraging, not empty

Fuck Cancer acknowledges that the situation may be frightening, exhausting, or unfair, then helps with the next step. It does not say “stay positive,” promise that everything will be okay, or force patients to describe cancer as a battle.

The skill supports decisions with current evidence. It does not diagnose cancer, choose treatment, determine trial eligibility, or replace the patient's medical team.

## What's inside

- [`SKILL.md`](skills/fuck-cancer/SKILL.md) contains the complete care-navigation and research workflow.
- [`search_trials.py`](skills/fuck-cancer/scripts/search_trials.py) searches ClinicalTrials.gov API v2 and keeps only locations with an open site status.
- [`openai.yaml`](skills/fuck-cancer/agents/openai.yaml) contains the Codex skill metadata.

The skill does not require an account, database, or API key. The trial-search helper uses only Python's standard library.

## Privacy

Do not put names, birth dates, medical-record numbers, or other identifiers into research queries. Family-facing briefs omit patient identifiers by default. The skill never contacts a doctor, hospital, trial, or family member without explicit permission.

## Independent project

This is an independent open-source project. It is not affiliated with Fuck Cancer, FCancer, or letsfcancer.com.

## License

MIT
