# Fuck Cancer

Help patients and caregivers navigate cancer with a crisp, practical one-page brief covering what to do next, the key facts, plain-English medical definitions, and relevant clinical trials.

## Problem

Since I published [my mom's cancer story](https://creatoreconomy.so/p/my-mom-survived-breast-cancer-three), I’ve heard from many people supporting a loved one through cancer. Cancer casts a dark cloud over the whole family.

The last thing a patient or caregiver needs is a pile of confusing medical terms, hype, and scattered information. They need clear answers to three questions: What should we do next? What are the key facts? What treatment options should we ask about?

## What this skill does

1. **Explains the key facts and medical terms clearly.** It translates pathology, imaging, biomarkers, staging, and treatment language into plain English.
2. **Puts the next decision first.** It identifies the current priority and turns it into no more than three next actions.
3. **Researches current treatment options.** It starts with official cancer agencies, regulators, and professional guidance instead of citing random health pages.
4. **Finds clinical trials carefully.** It searches the official ClinicalTrials.gov API, checks the individual site's recruitment status, and names the eligibility questions that still need confirmation.
5. **Finds focused second opinions.** It returns up to three specialists or centers that fit the cancer type, disease setting, location, and practical constraints.
6. **Keeps the family aligned.** It creates one concise brief and updates it when new results or treatment decisions arrive.

## How to install /fuck-cancer

The easiest way to install the skill is to paste this into ChatGPT, Claude Code, or your favorite agent:

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
/fuck-cancer My dad was just diagnosed. Here’s what I know.
```

Paste or upload a report:

```text
/fuck-cancer Explain this report and help me prepare for Friday.
```

Research trials or second opinions:

```text
/fuck-cancer Find relevant trials near Toronto for this diagnosis.
```

Share new information as it arrives:

```text
/fuck-cancer Update our brief with this new biomarker report.
```

The skill asks only for missing information that could change the immediate guidance. It does not make you complete a long intake form.

## The output: A practical, concise brief for you and your family

Every report has no more than three sections:

1. **Current priority.** What needs to happen next and why.
2. **What to do next.** The most useful actions, questions, trials, or second opinions in priority order.
3. **What we know.** A plain-English explanation of the diagnosis, tests, biomarkers, stage, treatment history, and meaningful uncertainty.

Every list in the brief is numbered, including medical definitions and trial candidates. “What to do next” contains no more than three items. Each item uses a bold stem followed by two or three useful sentences. Sources and the research date appear in a compact footer.

The canonical output is one Markdown document in chat. If Google Drive is connected, the user can explicitly ask the agent to copy or update the same brief in a Google Doc. The skill does not assume a connector, automate a signed-in browser without permission, or create a separate tracking system.

## Sample brief

This fictional example shows the complete format. The patient is 46, lives near Los Angeles, and has newly diagnosed stage II triple-negative breast cancer. Treatment has not started.

### Breast Cancer Care Brief

#### Current priority

Confirm whether the cancer is stage II and decide whether to start the recommended treatment before surgery or complete clinical-trial screening first. The biopsy shows triple-negative breast cancer, and imaging has not found distant spread, but the oncology team still needs to confirm how the involved underarm lymph node affects the stage and treatment plan.

#### What to do next

1. **Confirm the stage and baseline workup.** Ask the oncologist to confirm the tumour size, whether nearby lymph nodes are involved, and that no distant spread was found. Ask whether any additional imaging, heart testing, bloodwork, or inherited genetic testing is needed before treatment, and get a date for anything still pending.
2. **Discuss the standard treatment before surgery.** NCI's current evidence summary describes chemotherapy plus pembrolizumab before surgery, followed by continued pembrolizumab after surgery, for some patients with stage II or III triple-negative breast cancer. Ask why this regimen fits, its major immune and chemotherapy risks, and how the surgical pathology would affect treatment afterward.
3. **Ask about two relevant clinical trials before starting treatment.** These trials are screening candidates:
   1. **[NCT06966700](https://clinicaltrials.gov/study/NCT06966700): Phase 3 study of sacituzumab tirumotecan in high-risk early breast cancer.** This study includes previously untreated, nonmetastatic triple-negative or hormone-receptor-low/HER2-negative breast cancer and had a recruiting site in Burbank, California. The trial team must confirm the exact T and N stage, performance status, organ function, prior procedures, and whether randomization could delay standard treatment.
   2. **[NCT05929768](https://clinicaltrials.gov/study/NCT05929768): Phase 3 study of shorter anthracycline-free chemo-immunotherapy.** This study compares a shorter pembrolizumab-based regimen without anthracyclines with the usual anthracycline-containing approach and had recruiting Los Angeles sites, including Cedars-Sinai. The trial team must confirm the tumour and node stage, heart function, autoimmune history, and that no treatment has started.

#### What we know

1. **The biopsy shows invasive ductal carcinoma with triple-negative biomarkers.** The breast mass measures 3.2 cm, and a sampled underarm lymph node contains cancer. Current imaging has not found cancer in distant organs, but the oncology team makes the final stage determination.
2. **Medical terms that affect treatment:**
   1. **ER and PR negative:** ER and PR are hormone receptors. Negative results mean hormone-blocking treatments such as tamoxifen or aromatase inhibitors are unlikely to help this cancer.
   2. **HER2 negative:** HER2 is a growth-promoting protein. A negative result means standard HER2-targeted drugs are not expected to be part of the initial plan.
   3. **Triple-negative breast cancer:** This means the cancer is ER-negative, PR-negative, and HER2-negative. Chemotherapy is a central treatment, and immunotherapy may be added in some early-stage or metastatic settings.
   4. **PD-L1:** This marker can affect immunotherapy decisions in metastatic triple-negative breast cancer. It does not control every immunotherapy decision in early-stage disease, so its meaning depends on the treatment setting.
   5. **Stage II:** The cancer is in the breast and may involve nearby lymph nodes, but no distant spread has been found. The oncology team confirms the exact stage.

## Trusted medical sources

The skill grounds its research in trusted medical sources:

1. **Evidence and treatment context:** [NCI's PDQ cancer information summaries](https://www.cancer.gov/publications/pdq/information-summaries) or the official cancer agency for the patient's country. PDQ is evidence-based and regularly updated, but it is an evidence summary rather than a clinical guideline.
2. **Drug approvals and labels:** The patient's national regulator, such as the FDA, Health Canada, EMA, MHRA, or TGA. Approval establishes what is authorized in that country, not what one patient should choose.
3. **Testing and clinical guidance:** Current official publications from groups such as ASCO, ESMO, CAP, or NICE when they directly apply.
4. **Clinical trials:** The official [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api), including the status of the individual site.
5. **Medical definitions:** The [NCI Dictionary of Cancer Terms](https://www.cancer.gov/publications/dictionaries/cancer-terms/) or an equivalent official national source.
6. **Emerging questions:** Peer-reviewed primary research indexed in PubMed. The skill states when evidence is early or does not directly match the patient's situation.

[CIViC](https://civicdb.org/) is a useful open knowledgebase for specific cancer variants, but it is community-curated. The skill may use it as a supplement, never as the sole basis for treatment or trial eligibility.

## Practical and supportive

Fuck Cancer acknowledges that the situation may be frightening, exhausting, or unfair, then helps with the next step. It does not say “stay positive,” promise that everything will be okay, or force patients to describe cancer as a battle.

The skill supports decisions with current evidence. It does not diagnose cancer, choose treatment, determine trial eligibility, or replace the patient's medical team.

## What's inside

1. [`SKILL.md`](skills/fuck-cancer/SKILL.md) contains the complete care-navigation and research workflow.
2. [`search_trials.py`](skills/fuck-cancer/scripts/search_trials.py) searches ClinicalTrials.gov API v2 and keeps only locations with an open site status.
3. [`openai.yaml`](skills/fuck-cancer/agents/openai.yaml) contains the Codex skill metadata.

The skill does not require an account, database, or API key. The trial-search helper uses only Python's standard library.

## Independent project

This is an independent open-source project. It is not affiliated with Fuck Cancer, FCancer, or letsfcancer.com.

## License

MIT
