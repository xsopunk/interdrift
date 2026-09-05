PROMPT — Regression Check: Hardcoding Audit

Goal: verify the text/copy rewrites from the previous pass did not accidentally convert any dynamic, data-driven text into a hardcoded static string. This is a real risk when rewriting for clarity — e.g., turning a templated case title (built from rule_id, category, amount, merchant_true_category, etc.) into a fixed literal string, or hardcoding a rupee/percentage value that should update per dataset/audit run.

Check specifically:

Agent Priority Queue case names/titles — confirm names like "MCC_Misclassification" were rewritten as a template/function (still building from rule_id/category/transaction data), not replaced with one fixed display string that would show identically regardless of what the actual audit finds.
Rail breakdown labels (R4, R6b, R10 rows) — confirm human-readable names are derived from the rule's category/description field in the rule table (or a lookup keyed by rule_id), not hardcoded per-rule display strings written once for this specific dataset's current rules — must still work correctly if R10's exposure changes, a new rule is added, or a different rule triggers.
Sub-instrument formatting (RuPay_debit → "RuPay Debit" etc.) — confirm this is a general formatting function (e.g., replace underscores, title-case) applied to whatever value the data contains, not a hardcoded mapping of only the specific values currently visible in the screenshots — must handle any valid sub-instrument value, including ones not shown to you.
Any numbers, counts, or ₹ amounts referenced in your rewritten copy (e.g., in badge text, descriptions, or example strings) — confirm none were accidentally frozen as literals instead of continuing to read live from the underlying data/state.
Filter tab / status label fixes (e.g., "Flagged_For_Review" → cleaned label) — confirm the underlying value/key used for filtering logic is unchanged, and only the displayed label was reformatted — filtering must still function correctly against the real classification value.

For each of the 5 checks: confirm clean, or report exactly which file/line hardcoded something that should remain dynamic in your previous fixes, with a proposed fix. Do not fix anything yet — report only. Output concisely (in 100 words) asking if you can fix. then next 5. 