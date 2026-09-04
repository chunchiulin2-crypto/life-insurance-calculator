# Foundation Optimization Design

Date: 2026-07-07
Project: life-insurance-calculator
Scope: Phase 1 of a full optimization program

## Goal

Improve the calculator foundation before larger UI or AI product changes. This phase should make the app faster, easier to maintain, and safer around edge cases while preserving existing actuarial outputs.

The current baseline is stable: 65 tests pass. The implementation should keep those tests green and add focused regression coverage for new shared helpers and boundary behavior.

## Non-Goals

This phase will not redesign the full Streamlit interface, change product formulas, replace the mortality tables, retrain models with real external data, or alter deployed product positioning. Those belong to later UX and product-depth phases.

## Current Context

The app is a Python and Streamlit actuarial platform with product pages for term life, whole life, annuity, endowment, deferred products, pure endowment, AI mortality, fraud detection, pricing optimization, stress testing, reinsurance, product comparison, and sensitivity analysis.

The main issues are structural rather than mathematical:

- Multiple pages repeat life table loading and life table construction helpers.
- CSV reads happen from several locations with inconsistent caching.
- ML modules cache trained models in module globals, but Streamlit pages do not present one clear cached path.
- Several pages define local `get_lt()` functions with similar behavior.
- Age and term bounds are partly enforced in UI, but core helper behavior is less explicit.
- `app.py` owns a large block of CSS and global navigation, which makes later UI changes harder.

## Recommended Approach

Use a moderate modular foundation pass:

1. Add shared utility modules for common app behavior.
2. Centralize cached mortality table loading and life table construction.
3. Keep premium and reserve formulas compatible with current results.
4. Add explicit validation helpers for age, term, deferment, and table range checks.
5. Refactor product pages incrementally to use shared helpers where it is low risk.
6. Verify with the current test suite and a small set of new helper tests.

This avoids a risky full rewrite while removing enough duplication to support later UX cleanup and AI/product improvements.

## Proposed Modules

### `app_utils.py`

Shared Streamlit-facing helpers:

- `init_session_defaults()` sets language, table column, and table path defaults in one place.
- `selected_table_state()` returns the active table path and column from session state.
- `table_column_for_gender(table_col, gender_code)` resolves CLT gender columns vs AM92 columns.
- `format_currency()`, `format_percent()`, and small display helpers can be added only if they replace real repetition.

### `life_table_cache.py`

Shared data and life table helpers:

- `cached_load_table(path)` reads CSV once per path in Streamlit with `st.cache_data` when Streamlit is available, and falls back to an `lru_cache` path for CLI/tests.
- `cached_life_table(path, table_col, gender_code, risk_factor)` returns a built life table through the shared resolver.
- The helper should return copied DataFrames or immutable-safe values where needed so callers do not accidentally mutate cached state.

### `validation.py`

Small actuarial input validation helpers:

- `validate_issue_age(age, max_age)`
- `validate_term(age, term, max_age)`
- `validate_deferment(age, defer, max_age)`
- `validate_coverage_window(age, defer, coverage, max_age)`

These helpers should raise clear `ValueError` messages for CLI/tests and can be wrapped by Streamlit pages to show `st.error()`.

## Data Flow

The target flow for traditional mortality pages is:

1. Page reads session state for language, table path, and table column.
2. Page collects product inputs.
3. Shared validation checks whether the requested ages fit the active table.
4. Shared cache helper loads the CSV and builds the life table.
5. Existing premium/reserve functions calculate results.
6. Page displays metrics and charts.

The target flow for ML mortality pages is:

1. User chooses AI mortality source.
2. ML model is trained lazily once.
3. ML life table is built for selected user factors.
4. Existing premium/reserve functions consume the resulting life table.

## Error Handling

Validation should make out-of-range inputs explicit. Examples:

- If `age + term` exceeds the table maximum, show a clear message and skip calculation.
- If AM92 is selected, gender-specific CLT columns should not be requested.
- If a table file is missing or malformed, surface a concise error instead of allowing a low-level index error.

Core calculation functions can keep returning current values for existing valid inputs. This phase should avoid changing legacy behavior for valid scenarios.

## Testing Plan

Keep the existing tests passing:

- `test_mortality.py`
- `test_premium.py`
- `test_reserve.py`

Add focused tests for:

- cached table helper returns expected columns and does not alter calculations;
- table/gender resolver handles CLT and AM92 correctly;
- validation rejects impossible age and term combinations;
- refactored pages or helper paths produce the same premium results for representative scenarios.

The acceptance condition is that all existing tests pass and new helper tests cover the shared foundation behavior.

## Implementation Boundaries

Refactor only pages touched by the shared foundation changes. Do not rewrite all Streamlit pages in one pass. Start with one or two representative product pages, then apply the same helper to the remaining product pages where the change is mechanical and low risk.

Avoid broad visual redesign in this phase. CSS extraction can be considered if it is needed to reduce `app.py` complexity, but detailed visual polish belongs to the UX phase.

## Acceptance Criteria

- Existing actuarial outputs remain compatible for valid representative inputs.
- The test suite remains green.
- Life table loading and life table construction have a single shared path.
- Product pages no longer need to define duplicate `get_lt()` helpers where the shared helper applies.
- Invalid age/term/deferment inputs produce clear user-facing messages.
- The codebase is easier to extend in the later UX and product-depth optimization phases.

## Later Phases

After this foundation phase:

1. UX Cleanup: unify page layouts, result cards, input grouping, empty/error states, and navigation polish.
2. Product Depth: improve AI module explanations, comparison workflows, report exports, README/deployment docs, and demo scenarios.
