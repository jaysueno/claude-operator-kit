---
name: secret-exposure-responder
description: >
  Respond the moment a credential is exposed: a key, token or secret printed into chat, a
  log, a pull request body, a process or environment dump, or a committed file. Run on "a
  key got exposed", "rotate this credential", "secret in the output", "I leaked a token",
  or the instant you notice secret-shaped material in any output. Names the credential
  (never reprints the value), gives the rotation location for that credential type, and
  blocks "rotate later": the standing rule is rotate NOW. NOT for choosing among secrets
  or routine secret handling; this is the incident response for an exposure that already
  happened.
argument-hint: "<what leaked, in words, for example 'database service key in a log'>"
---

# secret-exposure-responder: rotate now, not later

**Why:** the standing rule is that an exposed credential is rotated immediately; "rotate
later" is not an accepted state. In practice rotation kept getting deferred (2026-06-09,
2026-07-12 twice, 2026-07-13), usually because nobody had the rotation location at hand in
the moment. This skill puts it at hand and refuses the deferral.

## The moment a secret is exposed

1. **Do NOT reprint the value.** Refer to it by provider and purpose plus its last 4
   characters only ("the database service key ending in 9x2"). Never echo the full or a
   partial secret again; that re-exposes it into another surface.
2. **Contain.** If it is in a file that is local or gitignored, strip it in place now. If
   it was **committed**, it is in git history, so removing the line does not make it
   safe: the key MUST be rotated regardless (history is forever).
3. **Rotate at the source** (table below), then **update every consumer**: each env file,
   config file, scheduled job, CI secret, or server credential file that reads it.
4. **Verify** that the old key is dead (a call with it is refused) and the new key works.
5. **Log it where the owner sees it.** Never a silent fix. If the owner decides a specific
   exposed key is not worth rotating (for example, a decommissioned system), record that
   decision explicitly rather than leaving it open.

## Rotation locations for common providers

Providers are named in words on purpose. This file never shows a literal key prefix, so a
secret scanner run over it stays quiet.

| Credential | Rotate at | Then update |
|---|---|---|
| **GitHub personal token** | github.com, Settings, Developer settings, Personal access tokens: delete it, then generate a new one with the smallest scopes that work | local git credential helpers, CI secrets, any env file that holds it |
| **Anthropic API key** | console.anthropic.com, Settings, API Keys: delete, then create | the env file of the service that calls the API |
| **OpenAI API key** | platform.openai.com, API keys: revoke, then create | the env file of the service that calls the API |
| **OpenRouter key** | openrouter.ai, Keys: delete, then create | eval or judge env files |
| **AWS access key** | AWS console, IAM, Users, the user, Security credentials: create a new key, switch consumers, then deactivate and delete the old one | the shared credentials file, CI secrets, any env file |
| **Google Cloud API key or OAuth client secret** | console.cloud.google.com, APIs and Services, Credentials: regenerate the key or reset the client secret; revoke issued tokens at myaccount.google.com, Security, Third-party access | every env file that holds the client id, secret, or refresh token |
| **Slack bot token** | revoke it with Slack's auth.revoke API method (or uninstall the app), then reinstall the app to the workspace at api.slack.com/apps to issue a new token | the bot's env file |
| **Stripe secret key** | dashboard.stripe.com, Developers, API keys: roll the key | the server env file and CI secrets |
| **Supabase service-role or anon key** | the Supabase dashboard, the project, Settings, API keys: rotate or reset the key | server env files, hosting provider env vars |
| **Cloudflare tunnel token** | the Cloudflare dashboard, Zero Trust, Networks, Tunnels, the tunnel: refresh the token (it does not show under the general API tokens page), or delete and recreate the tunnel | the tunnel config or the service that runs the tunnel with the token |
| **Telegram bot token** | the BotFather chat in Telegram: send /revoke, pick the bot, take the new token | every alert script or env file that sends as the bot |
| **Airtable personal access token** | airtable.com, Builder Hub, Personal access tokens: revoke | any script or env file that read the base |

When the type is not listed: name the provider, open its API keys or console page, rotate
there, update the consumers. Never guess a value; never accept "rotate later" for a live key.

## Gate

Incident response, not routine handling. It never transmits the secret anywhere: no paste
into chat, a pull request, a log, or a model prompt. The output is a checklist plus the
containment edit, never the secret.
