> Since 2026-10-04. The laptop ran hot: fourteen chats open for days, five preview servers nobody
> remembered, a hidden browser that had burned 191 CPU-minutes, memory full.

# Stop what you start

Anything a session starts in the background, that session stops before it ends.

1. **Servers, previews, hidden browsers, tunnels, loops**: stop them when the check they were
   started for is done. Before the final reply, list what you started and confirm it is gone (the
   process is not in `ps`, the port is closed). If something must stay up, say what it is, the
   port, and how to stop it.
2. **Containers**: use them, then stop them and quit the runtime when the work is done.
3. **No new scheduled job on the machine without a go.** Say how often it runs. Default to hourly
   or slower; anything faster needs a reason.
4. **Never stop another session's process without a go.** Leftovers you find are reported, not
   killed.

A hook can run at session start and print what past sessions left behind. It is silent when the
machine is clean. When it prints a list, relay it in one plain line and offer to stop the items.
