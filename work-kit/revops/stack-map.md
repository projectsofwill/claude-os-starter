# GTM stack map

Every system that touches pipeline, bookings, or revenue. Fill in during the first 30 days; keep current.
The CRM's own admin UI is the source of truth for config. This map is the overview and the "who owns it".

## Systems

| System | Purpose | Owner | Admin access? | Syncs with | Notes |
|---|---|---|---|---|---|
| <CRM> | System of record for accounts, opportunities | <name/role> | <yes/no> | <billing, marketing automation> | |
| <call recording> | Call transcripts, deal intelligence | | | <CRM> | |
| <sequencing / prospecting> | Outbound | | | <CRM> | |
| <contracts / CLM> | Order forms, signatures | | | <CRM, billing> | |
| <billing / usage metering> | Invoices, consumption data | | | <CRM, finance> | |
| <BI / warehouse> | Reporting | | | <all> | |

## CRM objects and key fields

| Object | Key fields (API name) | Used for | Gotchas |
|---|---|---|---|
| <Account> | | | |
| <Opportunity> | stage, amount, close date, forecast category, type | pipeline, forecast | forecast category is mutable: snapshot it |

## Automations

| Name | System | Trigger | What it does | Owner | Last reviewed |
|---|---|---|---|---|---|

## Known issues / tech debt

- <issue> (impact, owner, ticket)
