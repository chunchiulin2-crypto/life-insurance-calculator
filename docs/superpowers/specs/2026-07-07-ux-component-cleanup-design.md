# UX Component Cleanup Design

Date: 2026-07-07
Project: life-insurance-calculator
Scope: Phase 2 of the optimization program

## Goal

Improve the user experience by making product, AI, and analysis pages more consistent and easier to scan. This phase should preserve the current restrained Apple-style visual direction while reducing duplicated UI code across Streamlit pages.

The priority is a shared presentation layer, not a visual redesign. Users should still recognize the existing app, but pages should feel more coherent and predictable.

## Non-Goals

This phase will not change actuarial formulas, mortality tables, model behavior, product pricing logic, or data sources. It will not introduce a full dashboard redesign, a step-by-step wizard, or a new visual theme. Those can follow after the UI component layer is stable.

## Current Context

The app already has a strong base style in `app.py`, including Apple-style cards, metric styling, navigation pills, and parameter chips. The issue is that page-level UI patterns are repeated manually:

- Product pages build parameter chips with repeated HTML string assembly.
- Metric rows are assembled differently across pages.
- Chart/table sections use similar `st.container(border=True)` patterns but with inconsistent spacing and labels.
- Error handling is split between sidebar and main page with repeated `st.error()` calls.
- Analysis pages such as Reinsurance, Product Compare, and Sensitivity are more visually isolated than the product pages.

This phase should create shared helpers that keep the current look while making page implementation cleaner.

## Recommended Approach

Use a component cleanup pass:

1. Add a small `ui_components.py` module.
2. Move repeated parameter chip rendering into a helper.
3. Add shared metric-row rendering for common result summaries.
4. Add shared section panel helpers for chart/table sections.
5. Add consistent validation/error display helpers.
6. Migrate representative product and analysis pages incrementally.
7. Verify with Python tests, syntax checks, and Streamlit smoke tests.

This approach is lower risk than a guided-flow or dashboard redesign because it improves consistency without changing each page's workflow.

## Proposed UI Helpers

### `render_param_chips(items)`

Renders a list of `(label, value)` pairs using the existing `.param-chips` and `.param-chip` CSS classes.

Expected behavior:

- Skip items with `None` values.
- Escape text values before injecting HTML.
- Preserve the compact chip look already used across product pages.

### `render_metric_row(metrics, columns=None)`

Renders a row of Streamlit metrics with a shared data shape.

Each metric can include:

- `label`
- `value`
- `help`
- `delta`
- `delta_color`

This should replace repeated `c1, c2, c3 = st.columns(...)` blocks where the layout is straightforward.

### `section_panel(title, caption=None)`

Provides a consistent wrapper around `st.container(border=True)` for chart and table sections.

Expected behavior:

- Render a subheader.
- Optionally render a caption.
- Yield a container so page code can place charts/tables inside it.

### `show_input_error(message, location="main")`

Displays validation errors consistently.

Rules:

- Use `st.sidebar.error()` for invalid sidebar inputs.
- Use `st.error()` for calculation or page-level errors.
- Keep messages concise and user-facing.

### `render_home_nav(label)`

Provides the simple one-link home navigation used by analysis pages. Full product nav strips can be handled later if needed.

## Migration Plan

Start with pages that already share the strongest pattern:

1. Product pages 1-7: migrate `param_items` and metric rows.
2. Product chart/table sections: migrate reserve/survival panels where the structure matches.
3. Analysis pages 13-15: migrate home nav and section panels.
4. AI Chat and AI modules: migrate only obvious section headings and error display, avoiding deeper interaction changes.

Do not force every page into a helper if the helper makes the code harder to read. The target is practical consistency, not abstraction for its own sake.

## Error Handling

Validation behavior should remain the same as the foundation phase. This UX phase only changes how errors are displayed.

Examples:

- Sidebar input range errors remain in the sidebar.
- Calculation exceptions shown in result sections should use a common format.
- Avoid raw exception traces in user-facing UI.

## Testing Plan

Keep the existing test suite green.

Add lightweight tests for pure helper behavior where possible:

- `render_param_chips` escapes labels and values.
- `render_param_chips` skips `None`.
- Metric spec normalization handles missing optional fields.

Streamlit UI helpers are mostly verified through smoke tests:

- Home page opens.
- Representative product pages open without Traceback.
- Analysis pages open without Traceback.
- Product Compare and Sensitivity remain reachable through navigation.

## Acceptance Criteria

- Existing test suite remains green.
- Product pages 1-7 use the shared parameter chip helper.
- At least the main product result metric rows use a shared metric helper where straightforward.
- Repeated chart/table section containers are reduced on representative pages.
- Analysis pages have more consistent section/nav rendering.
- Current Apple-style visual direction is preserved.
- No actuarial outputs change for valid inputs.

## Later Phases

After this component cleanup:

1. Dashboard polish: richer result panels, scenario summaries, and comparison strips.
2. Guided flows: optional step-based product calculators for beginner users.
3. Product depth: improved AI module explanations, report exports, and demo scenarios.
