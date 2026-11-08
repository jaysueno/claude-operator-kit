> Since 2026-03-05. A script meant for a test list read an environment variable, found it set the
> wrong way, and sent 1,399 emails to real people. The variable was the only safety.

# Things that always need a human go

An environment variable is never a safety mechanism. These actions get a hard gate: an explicit
`--live` flag on the script, the exact target list shown to a human first, and that human's go
for that run. Test targets first, always.

1. **Outbound messages to the public**, on any channel: email, chat, SMS, review replies, posts.
   Changing what an automated responder says also needs a go before it deploys.
2. **Money movement**: payments, refunds, price changes, pay runs, ledger entries. Each one also
   needs a deterministic pre-check that can say no. Never state a figure you did not compute from
   live data.
3. **Personal or health records**: they stay inside their system boundary. Never into a marketing
   send, an alert, a log, a commit, a pull request body, or a model prompt beyond the pre-scoped
   fetch. Log aggregates, never individuals.
4. **Spending** above a small fixed amount per action, and any ad budget change.
5. **Publishing**: nothing goes public without the owner's go. Sending content to an external
   service is publishing; it can be cached or indexed even if deleted.

Standing automation never overrides a gate. A deploy pipeline with autonomy still stops here.
