# Fuck Cancer

Create a practical brief to help patients and caregivers advocate for themselves: what to do next, the key facts, plain-English medical definitions, and relevant clinical trials.

https://github.com/user-attachments/assets/REPLACE-WITH-UPLOADED-VIDEO-URL

## Problem

Since I published [my mom's cancer story](https://creatoreconomy.so/p/my-mom-survived-breast-cancer-three), I’ve heard from many people supporting a loved one through cancer. Cancer casts a dark cloud over the whole family.

The last thing a patient or caregiver needs is a pile of confusing medical terms, hype, and scattered information. They need clear answers to three questions: What should we do next? What are the key facts? What treatment options should we ask about?

## What this skill does

1. **Explains the key facts and medical terms clearly.** It translates pathology, imaging, biomarkers, staging, and treatment language into plain English, and flags treatment-relevant tests that do not appear in the records yet so the family can ask about them.
2. **Puts the next decision first.** It identifies the current priority and turns it into no more than three next actions.
3. **Researches current treatment options.** It starts with official cancer agencies, regulators, and professional guidance instead of citing random health pages.
4. **Finds clinical trials carefully.** It searches the official ClinicalTrials.gov API, checks the individual site's recruitment status, and names the eligibility questions that still need confirmation.
5. **Finds focused second opinions.** It returns up to three specialists or centers that fit the cancer type, disease setting, location, and practical constraints.
6. **Keeps the family aligned.** It creates one concise brief, keeps a dated care log, and finds practical support when the family needs it.

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

Every brief has four sections:

1. **Current priority.** Dated in the heading. The next concrete event, the decision in front of the family and the best-studied path, then what is time-sensitive, with specific trials or options named and linked.
2. **What to do next.** No more than three actions in priority order: questions to bring to the oncologist (at most five, offered as suggestions), missing tests, current options, trials, second opinions, or practical support.
3. **What we know.** A plain-English explanation of the diagnosis, tests, biomarkers, stage, and meaningful uncertainty, tied to the patient's own results.
4. **Care log.** A dated history, newest first, including the day the brief was created or updated.

Every list is numbered. Each item uses a bold stem followed by two or three sentences, and each trial candidate is capped at three sentences. Any drug or medical term gets a few-word explainer in parentheses the first time it appears, so nobody has to leave the page to understand a sentence. Sources sit inline as short links on the claims they support; there is no footer or disclaimer.

The canonical output is one Markdown document in chat. If Google Drive is connected, the user can explicitly ask the agent to copy or update the same brief in a Google Doc. The skill does not assume a connector, automate a signed-in browser without permission, or create a separate tracking system.

## Sample brief

This fictional example shows the complete format. The patient is 46, lives near Los Angeles, and has newly diagnosed stage II triple-negative breast cancer. Treatment has not started. The trials were pulled live from ClinicalTrials.gov within 40 miles of Los Angeles on August 22, 2026.

### Breast Cancer Care Brief

#### Current priority - 8/22

Next week's oncologist visit on 8/29 will likely discuss treatment.

For stage II triple-negative breast cancer (a type that doesn't respond to hormone or HER2-targeted drugs) with one involved lymph node, the best-studied path is chemotherapy plus pembrolizumab (an immunotherapy that helps your immune system attack the cancer) before surgery, then surgery, then more pembrolizumab ([source](https://www.cancer.gov/types/breast/hp/breast-treatment-pdq)).

Two Los Angeles trials, [NCT05929768](https://clinicaltrials.gov/study/NCT05929768) at Kaiser and Cedars-Sinai and [NCT06353997](https://clinicaltrials.gov/study/NCT06353997) at the Ellison Institute, build on that same path but only take patients who have not started treatment. If either interests you, ask about screening at this visit. Once chemotherapy begins, that door closes.

#### What to do next

1. **Questions you might bring to the oncologist.** These are the ones most likely to shape the plan. Pick what feels useful.
   1. What is the confirmed stage and plan? Is it chemotherapy plus pembrolizumab?
   2. What still needs to happen before day one (heart testing, bloodwork, extra imaging), and what's the target start date?
   3. Has inherited genetic testing (e.g., a blood or saliva test for BRCA1 and BRCA2, genes that raise cancer risk and can change treatment) been ordered, and will you wait for results before planning surgery?
   4. Could I get a copy of the pathology report with the exact ER and PR percentages?
   5. I found two clinical trials that might be relevant - NCT05929768 or NCT06353997 - is it worth screening for these?
2. **Bring up the genetic test if it hasn't been ordered.** Triple-negative disease at 46 is a standard reason to test. A positive result can add a year of olaparib (a daily pill that blocks DNA repair in BRCA-related cancers) after surgery, and can change the lumpectomy-versus-mastectomy decision. It's a common test in this situation, so it's reasonable to bring up.
3. **Decide whether to screen for a trial before treatment starts.** Both keep the standard pembrolizumab backbone, so neither means giving up proven care. Eligibility is confirmed only by the site.
   1. **[NCT05929768](https://clinicaltrials.gov/study/NCT05929768), shorter chemo-immunotherapy (phase 3, recruiting at Kaiser LA, Kaiser West LA, Cedars-Sinai).** Tests whether dropping doxorubicin (an older chemotherapy with heart-related side effects) gives the same result with less chemo. Fits your stage on paper. Confirm: ER and PR under 5 percent on your pathology, and comfort with random assignment.
   2. **[NCT06353997](https://clinicaltrials.gov/study/NCT06353997), INBRX-106 plus pembrolizumab (phase 2, recruiting at Ellison Institute, LA).** Adds INBRX-106 (an experimental immunotherapy) ahead of standard treatment. Earlier-phase, so side effects are less known. Confirm: tumor visible on ultrasound at 1 cm or more (yours is), and whether it delays standard treatment.
   3. **Later, after surgery:** [NCT05812807](https://clinicaltrials.gov/study/NCT05812807) and [NCT05633654](https://clinicaltrials.gov/study/NCT05633654) enroll based on what's found in the removed tissue. Ask the team to revisit them then.

#### What we know

1. **Invasive breast cancer with triple-negative biomarkers.** The breast mass is 3.2 cm and one sampled underarm node contains cancer. Imaging found no spread to distant organs. That pattern usually means stage II; the oncology team confirms.
2. **Medical terms that might affect treatment:**
   1. **ER and PR negative:** Hormone receptors. Since the report is negative on both, hormone-blocking pills such as tamoxifen won't help this cancer.
   2. **HER2 negative:** A growth-promoting protein. Your report is negative, so HER2-targeted drugs aren't part of the initial plan.
   3. **Triple-negative breast cancer:** All three of your markers are negative, which puts you in this group. Chemotherapy is the backbone. For stage II and III disease like yours, adding pembrolizumab before and after surgery raised the rate of complete tumor disappearance at surgery from 51 to 65 percent and improved three-year event-free survival (alive without the cancer coming back) from 77 to 85 percent in the KEYNOTE-522 trial. Serious side effects were more common with pembrolizumab (33 versus 20 percent), which is the main tradeoff to talk through.
   4. **PD-L1:** A protein on the tumor that matters for immunotherapy decisions in metastatic (spread to other organs) disease. Your cancer is early-stage, where pembrolizumab helped regardless of PD-L1, so your result likely doesn't change the plan.
   5. **BRCA1 and BRCA2:** Inherited DNA-repair genes, more often involved in triple-negative disease. You haven't been tested yet. A positive result would open the door to olaparib after surgery and affect your surgery choice and family screening.
   6. **Pathologic complete response (pCR):** No cancer left in the breast or nodes at surgery. Whether you reach it after pre-surgery treatment will shape some of your later options and trials.

#### Care log

1. **8/22:** Brief created. Open questions for the oncology visit: stage confirmation, BRCA testing, trial screening.
2. **8/15:** Staging imaging found no distant spread. The decision moved to treatment sequencing and optional trial screening.
3. **8/8:** Biopsies confirmed invasive breast cancer in the breast and the node. Receptors came back triple-negative.
4. **8/4:** Diagnostic mammogram and ultrasound found a 3.2 cm breast mass and a suspicious underarm lymph node.

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

Fuck Cancer acknowledges that the situation may be frightening, exhausting, or unfair, then helps with the next step. It can find a few local services for practical burdens such as transportation, meals, lodging, or caregiver support. It treats asking questions, requesting copies of records, and seeking second opinions as normal parts of good cancer care, and it helps families prepare for those conversations. It does not say “stay positive,” promise that everything will be okay, or force patients to describe cancer as a battle.

The skill supports decisions with current evidence. It does not diagnose cancer, choose treatment, determine trial eligibility, or replace the patient's medical team. For symptom questions, it gives a clear action level without pretending to calculate a medical confidence score.

## What's inside

1. [`SKILL.md`](skills/fuck-cancer/SKILL.md) contains the complete care-navigation and research workflow.
2. [`search_trials.py`](skills/fuck-cancer/scripts/search_trials.py) searches ClinicalTrials.gov API v2, expands common location abbreviations, filters sites by distance from the patient's home with `--near LAT,LON`, labels each site's status, and ranks likely matches first. It retries temporary API failures and marks missing site statuses for confirmation instead of silently dropping them.
3. [`test_search_trials.py`](tests/test_search_trials.py) covers location normalization, distance filtering, site-status handling, pagination, criteria previews, and relevance ordering.
4. [`openai.yaml`](skills/fuck-cancer/agents/openai.yaml) contains the Codex skill metadata.

The skill does not require an account, database, or API key. The trial-search helper uses only Python's standard library and requires Python 3.8 or newer.

## Independent project

This is an independent open-source project. It is not affiliated with Fuck Cancer, FCancer, or letsfcancer.com.

## License

MIT
