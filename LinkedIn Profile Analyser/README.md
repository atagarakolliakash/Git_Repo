# LinkedIn Growth Agents

Two approval-first agents for LinkedIn profile growth:

1. **Profile Optimization Agent** - analyzes a LinkedIn profile export/snapshot and produces recommended profile edits for approval.
2. **Posting Agent** - stores daily LinkedIn posts in an approval queue and publishes approved posts through LinkedIn's official Posts API.

LinkedIn does not provide a general public API for editing personal profile sections. This project therefore prepares precise profile changes for you to review and apply manually. Publishing posts can be automated if you configure an official LinkedIn OAuth access token with `w_member_social`.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Create a profile snapshot:

```powershell
Copy-Item templates\profile.example.json profile.json
```

Run profile analysis:

```powershell
python -m linkedin_growth_agents.cli analyze-profile --profile-json profile.json --out reports
```

Seed the posting queue:

```powershell
python -m linkedin_growth_agents.cli seed-calendar --days 30
```

Review and approve a post:

```powershell
python -m linkedin_growth_agents.cli list-posts
python -m linkedin_growth_agents.cli approve-post --id 1
```

Publish the next approved post:

```powershell
python -m linkedin_growth_agents.cli publish-next-approved
```

## Important Compliance Notes

- The agents do not scrape LinkedIn, bypass login, or store your LinkedIn password.
- Profile edits are generated as an approval checklist because LinkedIn profile editing is intended to happen in LinkedIn's UI.
- Automatic posting requires official LinkedIn developer access, OAuth, and a token with `w_member_social`.
- If no token is configured, the posting command runs in dry-run mode and writes the pending post to the console.

See [docs/SETUP.md](docs/SETUP.md) for configuration and [docs/APPROVAL_WORKFLOW.md](docs/APPROVAL_WORKFLOW.md) for the human approval workflow.
