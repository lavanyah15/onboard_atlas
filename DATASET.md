# Dataset

| File | Source URL | Pages | Licence / terms | Downloaded on |
|---|---|---:|---|---|
| gitlab_handbook_source.md | https://handbook.gitlab.com/handbook/ | To be counted | CC BY-SA 4.0; preserve attribution and comply with share-alike terms | 2026-10-23 |
| posthog_handbook_source.md | https://posthog.com/handbook | To be counted | Verify applicable repository and content licence; preserve required notices | 2026-10-23 |
| synthetic_leave_policy.md | Created for Onboard Atlas | To be counted | Original fictional content created for demonstration | 2026-10-23 |
| synthetic_expense_policy.md | Created for Onboard Atlas | To be counted | Original fictional content created for demonstration | 2026-10-23 |
| synthetic_onboarding_policy.md | Created for Onboard Atlas | To be counted | Original fictional content created for demonstration | 2026-10-23 |
| synthetic_performance_management_policy.md | Created for Onboard Atlas | To be counted | Original fictional content created for demonstration | 2026-10-23 |

Full data lives in `data/raw/` (not committed). A 2–3 file sample is in `data/sample/`.

**Dataset target:** At least 3,000 distinct handbook pages across the two real-company tenants, GitLab and PostHog. Synthetic demo policies are additional and do not count toward this minimum.

**Tenant isolation:** GitLab and PostHog documents must remain separate tenants. Each indexed chunk must include its `tenant_id` and applicable role metadata.