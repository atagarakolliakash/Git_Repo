# Approval Workflow

## Profile Optimization Agent

1. Export or manually copy your current LinkedIn sections into `profile.json`.
2. Run:

   ```powershell
   python -m linkedin_growth_agents.cli analyze-profile --profile-json profile.json --out reports
   ```

3. Review `reports/profile_approval_report.md`.
4. Apply approved profile changes manually inside LinkedIn.

LinkedIn profile editing is not automated because public profile-edit APIs are not generally available for personal LinkedIn accounts.

## Posting Agent

1. Seed draft posts:

   ```powershell
   python -m linkedin_growth_agents.cli seed-calendar --days 30
   ```

2. Review queued posts:

   ```powershell
   python -m linkedin_growth_agents.cli list-posts
   ```

3. Approve individual posts:

   ```powershell
   python -m linkedin_growth_agents.cli approve-post --id 1
   ```

4. Publish:

   ```powershell
   python -m linkedin_growth_agents.cli publish-next-approved
   ```

Only approved posts are eligible for publishing. Rejected and draft posts are never published.
