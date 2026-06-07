# Setup

## 1. Create a LinkedIn Developer App

To publish automatically, create a LinkedIn developer application and request access to a product that grants `w_member_social`.

LinkedIn's current Posts API uses:

- Endpoint: `POST https://api.linkedin.com/rest/posts`
- Scope: `w_member_social`
- Required headers: `Linkedin-Version` and `X-Restli-Protocol-Version`

If access is not approved, keep `LINKEDIN_DRY_RUN=true` and use the agent as a draft and approval system.

## 2. Configure Environment

Copy `.env.example` to `.env` and set:

```text
LINKEDIN_ACCESS_TOKEN=your_oauth_access_token
LINKEDIN_AUTHOR_URN=urn:li:person:your_member_id
LINKEDIN_DRY_RUN=false
```

Keep `LINKEDIN_DRY_RUN=true` until a test post has been reviewed.

## 3. Daily Automation on Windows

Create a Windows Task Scheduler task that runs once per day:

```powershell
C:\Path\To\Project\.venv\Scripts\python.exe -m linkedin_growth_agents.cli publish-next-approved
```

The command publishes only posts already marked `approved`.
