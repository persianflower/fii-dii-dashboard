# Debug Report — nse_fiidii DataFrame Crash

## Bug Summary
**What failed:** `get_fiidii_data()` in `src/fetch.py` crashes on every call.
**Where:** `src/fetch.py:36-38`
**Under what conditions:** Every time `nsepython.nse_fiidii()` is called (it returns a pandas DataFrame).

## Root Cause
`nsepython.nse_fiidii()` returns a `pandas.DataFrame`, but the code assumes it returns a list of dicts. Two specific incompatibilities:
1. **Line 36:** `if not raw_rows:` — `pandas.DataFrame.__bool__()` raises `ValueError` (ambiguous truthiness). Should use `.empty`.
2. **Line 39:** `for row in raw_rows:` — iterating a DataFrame directly yields column names (strings), not rows. Should use `.iterrows()` or `.to_dict('records')`.

## Fix Applied
Changed `get_fiidii_data()` to:
1. Check `.empty` instead of truthiness
2. Convert DataFrame to list of dicts via `.to_dict('records')` with a single `.empty` guard
3. Already-existing `parse_fiidii_row()` handles the dict format correctly

**Files changed:** `src/fetch.py` — 3 lines changed (`if not raw_rows` → `if raw.empty`, `for row in raw_rows` → iterate dict)
**Why this fix:** Minimal change (3 lines), preserves the existing parser, zero structural refactor needed.

## Regression Test
**Added:** `test_handles_dataframe_input` — verifies `get_fiidii_data()` handles a DataFrame-shaped mock correctly.
**Note:** Existing test mocks return raw dict lists, which bypass `nse_fiidii()` entirely. The new test patches at the right level.

## Similar-Risk Scan
Checked all other uses of `nsepython` in the codebase:
- `nse_fiidii()` — the only nsepython function called. No other risk points.

## Prevention Note
Any function wrapping a third-party API should verify the actual return type with a small script before writing the production code. The original test mocked the return as a list, which hid the DataFrame reality. An integration test hitting the real nse_fiidii() would have caught this immediately.
