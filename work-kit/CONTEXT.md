# RevOps glossary

Revenue operations: the shared language for pipeline, bookings, revenue, and forecast at <company>. One
definition per term. If two teams use a word differently, that conflict is recorded here, not hidden.
Format: `.claude/skills/domain-modeling/CONTEXT-FORMAT.md`, plus two RevOps lines per metric:
`_Source_` (the system/report that is the source of truth) and `_Owner_` (who signs off on the definition).
`<confirm>` marks a seed definition not yet checked against how the company actually uses the term.

## Pipeline

**Opportunity**: A tracked potential deal with an amount, stage, owner, and expected close date. <confirm: object name in the CRM>
_Avoid_: Deal (unless that's the CRM's name), op

**Stage**: The opportunity's position in the sales process, using the CRM's actual picklist values: <list stages>.
_Avoid_: generic names ("Discovery") unless they're the real picklist values

**Pipeline**: Open opportunities expected to close in a stated period, measured at a fixed snapshot date. <confirm: which stages count>
_Avoid_: "the funnel" for open pipe
_Source_: <CRM report> · _Owner_: <name/role>

**Pipeline coverage**: Open pipeline for a period divided by the remaining target for that period. Always state both numbers.
_Source_: <report> · _Owner_: <name/role>

**Slip**: An opportunity whose close date moved out of the period it was forecast in, or whose forecast category was downgraded between two snapshots. Say which.
_Avoid_: "pushed" without saying whether it was a managed reschedule

**Stale opportunity**: An open opportunity with no logged activity for <N, default 14> days.

## Forecast

**Forecast category**: The rep's or manager's call on an opportunity (e.g. Commit / Best case / Pipeline / Omitted). Mutable, so analyze it only from snapshots. <confirm: category names>
_Source_: <CRM field> · _Owner_: <name/role>

**Commit**: Opportunities the owner expects to close in the period with high confidence. <confirm: the company's bar>

**Forecast accuracy**: Final closed-won amount for a period divided by the forecast submitted at a fixed point (state which week).

## Bookings and revenue

**Bookings**: Contract value signed in a period. <confirm: TCV vs first-year vs ACV>
_Avoid_: "revenue" for bookings

**ACV**: Annualized contract value of a deal. <confirm: treatment of one-time fees and ramps>

**ARR**: Annualized value of recurring contracts active at a point in time. <confirm: whether committed usage counts>
_Avoid_: run-rate (unless the company means usage run-rate, then define it separately)
_Source_: <finance system> · _Owner_: <finance owner>

**Usage revenue**: Revenue billed on metered consumption (e.g. compute hours) rather than a fixed subscription.
_Avoid_: ARR for pure pay-as-you-go usage

**Committed spend**: A customer's contractual minimum spend over a term, drawn down by usage. <confirm: how overage and true-ups work>

**NRR**: Revenue from a starting cohort of customers at the end of a period divided by their revenue at the start, including expansion, contraction, and churn. State the cohort and period.
_Source_: <finance> · _Owner_: <finance owner>

**GRR**: Same as NRR but excluding expansion. Capped at 100%.

## Conversion and velocity

**Win rate**: Closed-won opportunities divided by all closed opportunities (won + lost) in a period. State count- or amount-based.

**Sales cycle**: Days from opportunity creation to closed-won. <confirm: start at creation or at a qualifying stage>

## Segmentation

**Segment**: <field name> with cutoffs <e.g. Enterprise / Mid-market / SMB by employee count or spend band>.

**Territory**: The set of accounts assigned to a rep or team by <rules>. <confirm: where territory assignments live>
