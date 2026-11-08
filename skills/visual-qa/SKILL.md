---
name: visual-qa
description: >
  Run the visual-QA pass on any UI change before calling it done or showing it to
  anyone: screenshot at 3 viewports, READ the screenshots like a human, report by
  severity, fix before reporting. Run on "/visual-qa", "visual QA", "check the page",
  "screenshot it", or after ANY change to a page, component, chart, layout, or
  responsive behavior in any repo. NOT for pure logic, API, script or doc changes with
  no rendered surface.
argument-hint: "<url-or-site> [port]  (for example 'web 3000', or a full localhost URL)"
---

# visual-qa: screenshot, READ, fix, then report

**Why:** UI has been called "done" and shipped broken more than once: two broken email
renders in one week (2026-07-06 and 2026-07-07), and a visual-QA rule that had to be
stated three times. Looking at the rendered pixels is the gate.

**Proportionality:** a new surface, a layout change, or a new interaction gets the full
pass below. A copy-only text edit gets one focused screenshot of the changed section, and
you still READ it. Never zero QA.

## Steps

1. **Resolve the target and get the dev server up.** Parse `$ARGUMENTS` for a site or URL
   and a port; if none is given, ASK which surface. `curl` the URL; if it is down, start
   that repo's dev server and wait for it to answer.
2. **Screenshot at 3 viewports:** desktop 1440x900, tablet 768x1024, mobile 375x812. Use
   the repo's screenshot tool if it has one, else Playwright directly. Save to the session
   scratchpad, never the repo. **Always JPEG at quality 80, never PNG** (a full-page PNG at
   1440 wide runs 3 to 8 MB; JPEG 80 is about a tenth and reads the same). Use a full-page
   shot only when page-level layout is the question; a viewport shot otherwise.
3. **READ every screenshot** with the Read tool. Actually look, as a human would. This step
   is the whole point; never skip it or report from the code alone.
4. **Evaluate each viewport:** layout and grid alignment; spacing (margins, padding, gaps);
   typography (fonts loaded, sizes, weights); colors; images (loaded, sized, not cropped
   wrong); NO horizontal overflow; nothing cut off or hidden; mobile looks intentional
   (not a broken desktop); empty and error states; would this look good to a human?
5. **Data-backed surfaces (dashboards, admin screens, any live-data view):** cross-check the
   displayed values against the real source (the database or the API) and confirm dates
   render in the intended timezone. A right-looking chart with wrong numbers still fails.
6. **Report by severity:** CRITICAL (broken layout, missing content, visual bug), WARNING
   (spacing, alignment, fonts), INFO (polish).
7. **Fix before reporting done.** If anything is off: fix, re-screenshot, re-READ, repeat.
   Only then report, naming what you verified at which viewports.

## Capture mechanics (the protocol above is universal)

- If the repo ships a screenshot script, use it and read its output folder.
- Otherwise:
  `npx playwright screenshot --viewport-size=1440,900 http://localhost:{port} out.jpg`
  (Playwright picks the format from the extension, so `.jpg` gives JPEG). With the
  Playwright MCP server, pass `type: "jpeg"`, `quality: 80`, and a `.jpg` filename on every
  screenshot call.

## Gate

Visual QA inspects only. It never publishes or deploys. A public deploy follows its own
process and `rules/human-go-gates.md`.

<!-- allowed-tools intentionally omitted: this skill spans capture (Bash, Playwright),
     inspect (Read), and fix (Edit, Write); restricting it would break the fix loop. -->
