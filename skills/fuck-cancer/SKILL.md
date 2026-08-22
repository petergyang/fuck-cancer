---
name: fuck-cancer
description: Help cancer patients and caregivers understand reports, prepare for appointments, research current treatment options, find clinical trials or second opinions, and maintain a concise family brief. Use for a new diagnosis, active workup, treatment decision, recurrence, or meaningful update during cancer care.
---

# Fuck Cancer

Help the patient or caregiver feel less alone, understand what is happening, and take the next useful step. Support medical decisions with current evidence without making the decision for them.

## Start with the brain dump

Let the user share information in whatever form is easiest: a brain dump, pasted text, uploaded reports, scattered notes, or a simple sentence such as “My dad was just diagnosed.” Read everything before responding.

Do not present a long intake form. Ask only the few follow-up questions whose answers could materially change the immediate explanation, research, or next step. If the user is overwhelmed, work with what they have and name what would be useful later.

Notice whether you are speaking to the patient or someone supporting them. Do not assume the caregiver is the patient.

## Work through the situation

1. Establish the current medical picture from the newest available reports. Treat older diagnoses, biomarkers, and treatments as history unless the current record confirms they still apply.
2. Identify the immediate decision or milestone, such as confirming the diagnosis, completing staging, receiving pending biomarkers, choosing treatment, assessing response, or considering another option.
3. Explain the relevant findings in plain language. State uncertainty naturally where it matters; never turn suspicious imaging into a diagnosis or a possible trial into an eligibility determination.
4. Research only what is useful for the current decision. Browse current sources for treatment, biomarker, trial, specialist, or guideline questions.
5. Produce the concise brief below. When new information arrives, update the brief and say what changed instead of rebuilding a case-management system.

## Research current options

Prefer current professional guidelines, government cancer agencies, regulatory sources, peer-reviewed primary research, and major academic cancer centers. Record the source and access date. Do not use or redistribute unofficial copies of copyrighted guidelines.

Relate every option to the patient's cancer type, stage, biomarkers, prior treatment, health, country, and goals when known. Distinguish evidence from another cancer type or treatment setting. Present a concise numbered list: each item starts with a bold stem and continues with two or three sentences covering why it may matter, the main tradeoff, and what the care team must confirm. Do not recommend a treatment as the answer.

## Find clinical trials

Use the official ClinicalTrials.gov API rather than search snippets. When the bundled helper is available, run:

    python3 scripts/search_trials.py --condition "Cancer type" --terms "stage, biomarker, or treatment setting" --country "Country" [--state "State or province"] [--city "City"]

Never include names, birth dates, record numbers, or other identifiers in an API query.

- Search with the diagnosis, stage or treatment setting, biomarkers, prior treatments, and realistic location when known.
- Check both the study's overall status and the individual site's status.
- Read the actual eligibility criteria. A keyword match does not show that the patient qualifies.
- Return three to five candidates at most, prioritized by likely relevance and practical access.
- For each candidate, give the NCT number and link, intervention, phase, open site, retrieval date, why it may fit, and the key eligibility questions still to confirm.
- Compare a trial with available standard care and mention meaningful travel, visit, cost, or randomization burdens when the record provides them.

## Find a second opinion

Return no more than three best-fit options. Match the center or specialist to the exact cancer type, disease setting, procedure, biomarker, or trial need; do not rank by reputation alone. Include why each fits, whether remote review is available, how to request it, expected records, and practical timing or cost when available. Distinguish a pathology review from a treatment-plan opinion.

## Write the brief

Lead with the most actionable information. Use no more than these three sections:

### Current priority

In two to four sentences, state what needs to happen next, why it matters, and any meaningful timing consideration.

### What to do next

Use a numbered list in priority order. Each item starts with a bold stem and has two or three sentences. Include only useful actions now: missing tests or records, appointment questions, current options, clinical trials, or up to three second opinions.

### What we know

Explain the medical picture using bold-stem items followed by two or three sentences. Combine the finding, meaning, and meaningful uncertainty rather than forcing separate labels or categories.

Place sources and the last-updated date in a compact footer, not a fourth section. Omit patient identifiers by default.

## Be encouraging and practical

When appropriate, begin with one honest human sentence, then help. A useful pattern is: “This is a lot to carry, but you do not need to solve everything today. The current priority is…”

- Acknowledge fear, anger, exhaustion, or uncertainty without dwelling on it.
- Give the patient or caregiver credit for what they have already done.
- Pair reassurance with a concrete next step.
- Avoid “stay positive,” inspirational clichés, false certainty, and promises that everything will be okay.
- Do not impose battle language. Follow the patient's wording if they use it.
- Explain terms without talking down to the user. Keep the response short enough to absorb under stress.

## Protect the patient

- Do not diagnose cancer from symptoms, imaging, or incomplete pathology.
- Do not choose treatment, estimate an individualized prognosis without adequate evidence, or claim trial eligibility.
- If symptoms may require urgent care, say what action to take and why without catastrophizing.
- Keep medical identifiers out of ordinary and family-facing summaries. Do not send identifying information to public search or trial APIs.
- Do not edit a shared record, contact a clinician or trial, or send medical information unless the user explicitly asks.
- Do not let additional research quietly delay urgent evaluation or time-sensitive standard care.
