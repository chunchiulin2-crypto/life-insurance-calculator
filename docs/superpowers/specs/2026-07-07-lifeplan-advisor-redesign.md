# LifePlan Advisor Redesign Spec

## Product Positioning

Turn the existing actuarial calculator into a bilingual life insurance planning workspace for Hong Kong and overseas Chinese insurance advisors.

The product should no longer feel like a collection of actuarial demo pages. It should feel like a professional client-case tool that helps an advisor produce a clear customer-facing protection planning report.

One-sentence positioning:

> A bilingual life protection planning tool for Chinese-speaking advisors, turning client needs, coverage gaps, and actuarial pricing into a professional customer report.

## Target User

Primary user: Hong Kong or overseas Chinese insurance advisor.

The advisor needs to:

- Explain protection needs to Chinese-speaking clients.
- Compare protection-oriented life insurance structures.
- Produce a polished Chinese/English report after a client conversation.
- Use actuarial assumptions as credibility, without exposing every technical detail to the client.

This is not a regulated quotation system and must not claim to replace insurer illustrations, licensed advice, or official product documents.

## MVP Scope

The first commercial version is a professional protection planner, not a full sales CRM.

Core flow:

1. Client Case
2. Needs Analysis
3. Plan Comparison
4. Bilingual Report

The product should open directly into the workspace. A marketing-style landing page is not required for the first version.

## Page Structure

### 1. Home Workspace

Purpose: make the app feel like a professional advisor cockpit.

Layout:

- Left rail: case workflow steps and existing expert modules.
- Top bar: product name, language switch, currency/table assumptions.
- Main area: active case form and calculation results.
- Right panel: live report preview, key coverage gap, recommended sum assured, and export action.

The current scattered product pages should become secondary expert tools, not the first thing users see.

### 2. Client Case

Collect only enough data for planning:

- Client age and gender.
- Preferred language: Simplified Chinese, Traditional Chinese, English, or bilingual.
- Currency: HKD, USD, CNY.
- Annual income.
- Years of income replacement.
- Outstanding mortgage or debt.
- Children education need.
- Existing life coverage.
- Planning horizon.

Avoid collecting real identity data in the MVP.

### 3. Needs Analysis

Calculate a protection gap:

`recommended coverage = income replacement + debts + education needs + final expenses - existing coverage`

Show three recommendation bands:

- Basic: essential liabilities and short-term family protection.
- Standard: balanced income replacement and debt coverage.
- Comprehensive: higher replacement period and stronger family buffer.

The output must be written in advisor-friendly language, not only formulas.

### 4. Plan Comparison

Use existing actuarial modules to compare protection structures:

- Term life: primary MVP product.
- Whole life: included as a long-duration protection comparison.
- Endowment/annuity modules: available as expert modules, not central in the first customer report.

Show:

- Annual premium estimate.
- Monthly payment estimate.
- Coverage amount.
- Coverage period.
- Net/gross premium distinction.
- Main trade-off in plain language.

The comparison should include clear disclaimers that results are educational estimates based on selected assumptions.

### 5. Report Builder

Generate a polished bilingual HTML report first. PDF can follow after the HTML report is stable.

Report sections:

- Cover page with advisor name/company fields.
- Client profile summary.
- Protection gap summary.
- Recommended coverage bands.
- Plan comparison table.
- Selected actuarial assumptions.
- Plain-language interpretation.
- Disclaimer.

The report should have two modes:

- Client version: simple, explanatory, suitable for sharing.
- Advisor version: includes assumptions, mortality table, interest rate, expenses, and reserve/pressure-test references.

## Existing Feature Migration

Keep existing actuarial functions, but reorganize the navigation:

- Primary workflow: Client Case, Needs Analysis, Plan Compare, Report.
- Expert tools: Term Life, Whole Life, Annuity, Endowment, Deferred products, AI Mortality, Fraud Detection, Pricing Optimizer, Stress Testing, Reinsurance, Product Compare, Sensitivity.

Existing pages can remain available, but the app should lead with the new advisor workflow.

## Visual Direction

The interface should feel like a serious financial planning tool:

- Dense but readable.
- Calm professional palette.
- Less demo-like decoration.
- Clear hierarchy between client-facing outputs and technical assumptions.
- Compact cards only for individual metrics or repeated comparisons.
- No oversized marketing hero on the first screen.

Recommended visual rhythm:

- Left workflow rail.
- Central form/results canvas.
- Right sticky report preview.
- Metrics shown as concise KPI tiles.
- Tables for comparisons.
- Charts only where they clarify a client decision.

## Monetization Path

Free or demo version:

- Limited reports per month.
- Watermark on reports.
- Basic assumptions only.

Professional version:

- Remove watermark.
- Advisor branding.
- More reports.
- Bilingual report templates.

Advanced version:

- Expert assumptions.
- Stress testing.
- Sensitivity analysis.
- Advisor version report.
- Custom deployment or consulting package.

Payment and account systems are out of MVP implementation unless the report flow is already strong.

## Non-Goals For MVP

- Full CRM.
- Lead management.
- Payment integration.
- User accounts.
- Official insurer quotation replacement.
- Real product illustration import.
- Complex savings product IRR illustrations.
- Tax, legal, or regulatory advice.

## Implementation Constraints

The existing Streamlit app should be refactored conservatively:

- Reuse current calculation modules.
- Add new planning/report modules before deeply rewriting product pages.
- Keep legacy product calculators accessible.
- Prefer a focused new advisor workflow page over editing every product page at once.
- Preserve tests around premium, reserve, validation, and UI helpers.

## Success Criteria

The redesign is successful when:

- A user can complete a sample client case in one guided workflow.
- The app generates a professional bilingual report from that case.
- Existing premium/reserve calculations remain usable.
- The first screen communicates a paid advisor tool, not a school project.
- The result can support either a portfolio demo or an early paid pilot with advisors.
