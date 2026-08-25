# Fuck Cancer

Creates and updates a practical brief to help patients and caregivers keep track of their case and advocate for themselves.

https://github.com/user-attachments/assets/551549ee-4afa-4c4e-ae07-6266ec4a129d

## Problem

Since I published [my mom's cancer story](https://creatoreconomy.so/p/my-mom-survived-breast-cancer-three), I’ve heard from many people supporting a loved one through cancer. Cancer casts a dark cloud over the whole family.

The last thing a patient or caregiver needs is a pile of confusing medical terms, hype, and scattered information. They need clear answers to three questions: What should we do next? What are the key facts? What should we ask the care team?

## What this skill does

![Sample family medical brief with patient information, specific next steps, key facts, medical terms, and a compact care log](assets/sample-brief.png)

This skill creates a source-of-truth brief from whatever you know now, even when most of the workup is still pending. It keeps the same destination updated as the situation changes. The brief gives you:

1. **Patient information.** Essential identifiers, family doctor, care team, and contact information.
2. **What to do next.** Up to three specific actions naming the relevant test, appointment, clinician, and date.
3. **What we know.** The shortest useful summary of confirmed findings and meaningful uncertainty.
4. **Medical terms.** Plain-English explanations when several markers, tests, or treatments need clarification.
5. **Care log.** A compact history using dates such as `8/24` and years such as `2016`.

Clinical trials, second opinions, and practical support appear under **What to do next** only when they are relevant.

On first use, the skill asks whether to maintain the brief in a local Markdown file or a shareable Google Doc, unless a source of truth already exists. It updates only that destination and never creates a duplicate tracker.

## How to install the skill

The easiest way to install the skill is to paste this into ChatGPT, Claude Code, or your favorite agent:

```text
Install the /fuck-cancer skill globally from https://github.com/petergyang/fuck-cancer
```

You can also install it with `npx`:

```sh
npx skills add petergyang/fuck-cancer --skill fuck-cancer --global --yes
```

## How to use the skill

Start with a brain dump:

```text
/fuck-cancer My dad was just diagnosed. Here’s what I know.
```

Paste or upload a report:

```text
/fuck-cancer Explain this report and help me prepare for doctor meeting.
```

Research trials or second opinions:

```text
/fuck-cancer Find relevant trials near Toronto for this diagnosis.
```

Share new information as it arrives:

```text
/fuck-cancer Update our brief with this new biomarker report.
```

## Trusted medical sources

The skill grounds its research in trusted medical sources:

1. **Evidence and treatment context:** [NCI's PDQ summaries](https://www.cancer.gov/publications/pdq/information-summaries) or the official cancer agency for the patient's country.
2. **Drug approvals and labels:** The patient's national regulator, such as the FDA, Health Canada, EMA, MHRA, or TGA.
3. **Testing and clinical guidance:** Current official publications from groups such as ASCO, ESMO, CAP, or NICE when they directly apply.
4. **Clinical trials:** The official [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api), including the status of the individual site.
5. **Medical definitions:** The [NCI Dictionary of Cancer Terms](https://www.cancer.gov/publications/dictionaries/cancer-terms/) or an equivalent official national source.
6. **Emerging questions:** Peer-reviewed primary research indexed in PubMed, with early or indirect evidence labeled as such.
7. **Specialists and services:** Official academic cancer-center pages for their own clinicians, programs, and trials.

## Disclaimer

The skill supports decisions with current evidence. It does not diagnose cancer, choose treatment, determine trial eligibility, or replace the patient's medical team.

## What's inside

1. [`SKILL.md`](skills/fuck-cancer/SKILL.md) contains the complete care-navigation and research workflow.
2. [`search_trials.py`](skills/fuck-cancer/scripts/search_trials.py) searches ClinicalTrials.gov API v2, filters sites by distance from home with `--near LAT,LON`, labels each site's recruitment status, and ranks likely matches first.
3. [`eval.md`](skills/fuck-cancer/eval.md) checks the destination, brief structure, action specificity, medical boundaries, and concise care-log format.
4. [`test_search_trials.py`](tests/test_search_trials.py) covers location normalization, distance filtering, site-status handling, pagination, criteria previews, and relevance ordering.
5. [`openai.yaml`](skills/fuck-cancer/agents/openai.yaml) contains the Codex skill metadata.

Local Markdown mode requires no account, database, or API key. Google Doc mode uses the user's connected Google Drive integration; if it is not connected, the skill asks the user to enable it before writing. The trial-search helper requires no API key, uses only Python's standard library, and requires Python 3.8 or newer.

## License

MIT
