// Builds the two README diagrams in this folder: two-hooks.svg and rules-timeline.svg.
// Node built-ins only. Same script, same bytes: no clock, no randomness, no network.
// Run from the repo root: node docs/img/make.mjs
import { writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const OUT = dirname(fileURLToPath(import.meta.url));

// The palette and type from the visual brand guide. No other colors appear in the output.
const NAVY = '#001B3B';
const SAND = '#EDE7DC';
const TERRACOTTA = '#8C5348';
const OLIVE = '#59591D';
const HEAD = '#F2EDE2';
const SUB = '#D8D3CA';
const SERIF = "Georgia, 'Playfair Display', serif";
const SANS = "-apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif";

const W = 1200;

const esc = (s) =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const num = (v) => (Number.isInteger(v) ? String(v) : v.toFixed(1));

// A rough width for layout decisions. Generous on purpose, so wider system fonts still fit.
const widthOf = (s, size, bold) => s.length * size * (bold ? 0.6 : 0.55);

function text(x, y, s, o = {}) {
  const a = [`x="${num(x)}"`, `y="${num(y)}"`, `font-family="${o.serif ? SERIF : SANS}"`, `font-size="${o.size || 18}"`];
  if (o.bold) a.push('font-weight="700"');
  if (o.anchor) a.push(`text-anchor="${o.anchor}"`);
  a.push(`fill="${o.fill || SUB}"`);
  return `<text ${a.join(' ')}>${esc(s)}</text>`;
}

function rect(x, y, w, h, o = {}) {
  const a = [`x="${num(x)}"`, `y="${num(y)}"`, `width="${num(w)}"`, `height="${num(h)}"`];
  if (o.rx) a.push(`rx="${o.rx}"`);
  a.push(`fill="${o.fill || 'none'}"`);
  if (o.stroke) a.push(`stroke="${o.stroke}"`, `stroke-width="${o.sw || 1}"`);
  return `<rect ${a.join(' ')}/>`;
}

function line(x1, y1, x2, y2, o = {}) {
  const dash = o.dash ? ` stroke-dasharray="${o.dash}"` : '';
  return `<line x1="${num(x1)}" y1="${num(y1)}" x2="${num(x2)}" y2="${num(y2)}" stroke="${o.stroke || SUB}" stroke-width="${o.sw || 1}"${dash}/>`;
}

function circle(cx, cy, r, o = {}) {
  const s = o.stroke ? ` stroke="${o.stroke}" stroke-width="${o.sw || 1}"` : '';
  return `<circle cx="${num(cx)}" cy="${num(cy)}" r="${r}" fill="${o.fill || 'none'}"${s}/>`;
}

function svg(h, title, desc, body) {
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" role="img" aria-labelledby="title desc">`,
    `<title id="title">${esc(title)}</title>`,
    `<desc id="desc">${esc(desc)}</desc>`,
    rect(0.5, 0.5, W - 1, h - 1, { fill: NAVY, stroke: SAND }),
    ...body,
    '</svg>',
    '',
  ].join('\n');
}

// A deny or pass mark: a filled pill with a drawn cross or tick, then the word.
function mark(x, cy, deny) {
  const out = [rect(x, cy - 22, 114, 44, { rx: 6, fill: deny ? TERRACOTTA : OLIVE })];
  if (deny) {
    out.push(line(x + 17, cy - 8, x + 33, cy + 8, { stroke: HEAD, sw: 3 }));
    out.push(line(x + 33, cy - 8, x + 17, cy + 8, { stroke: HEAD, sw: 3 }));
  } else {
    out.push(`<polyline points="${x + 15},${cy} ${x + 22},${cy + 7} ${x + 35},${cy - 8}" fill="none" stroke="${HEAD}" stroke-width="3"/>`);
  }
  out.push(text(x + 46, cy + 7, deny ? 'DENY' : 'PASS', { size: 19, bold: true, fill: HEAD }));
  return out;
}

function twoHooks() {
  const H = 512;
  const b = [];
  b.push(text(40, 56, 'Two hooks: one blocks, one reports.', { serif: true, size: 30, fill: HEAD }));

  // Lane one: the guard, before each Bash call.
  b.push(rect(40, 92, 5, 166, { fill: TERRACOTTA }));
  b.push(text(62, 112, 'BEFORE EACH BASH CALL', { size: 17, bold: true }));
  b.push(text(62, 142, 'guard-git-destructive.py', { size: 21, bold: true, fill: HEAD }));
  b.push(text(62, 180, 'Reads the command.', { size: 19 }));
  b.push(text(62, 208, 'Denies the destructive list.', { size: 19 }));
  b.push(text(62, 236, 'Passes quoted text.', { size: 19 }));

  const examples = [
    ['git stash; echo x', true, 'starts the command'],
    ['(cd sub && git reset --hard)', true, 'after &&'],
    ['echo "git reset --hard"', false, 'inside quotes'],
  ];
  examples.forEach(([cmd, deny, why], i) => {
    const top = 96 + i * 56;
    const cy = top + 23;
    b.push(rect(400, top, 380, 46, { rx: 4, fill: NAVY, stroke: SAND }));
    b.push(text(420, cy + 7, cmd, { size: 20, fill: HEAD }));
    b.push(...mark(796, cy, deny));
    b.push(text(928, cy + 7, why, { size: 18 }));
  });

  b.push(line(40, 284, 1160, 284, { stroke: SUB }));

  // Lane two: the leftover check, at session start.
  b.push(rect(40, 300, 5, 190, { fill: OLIVE }));
  b.push(text(62, 322, 'AT SESSION START', { size: 17, bold: true }));
  b.push(text(62, 352, 'leftover-check.py', { size: 21, bold: true, fill: HEAD }));
  b.push(text(62, 390, 'Lists what was left running.', { size: 19 }));
  b.push(text(62, 418, 'Never stops anything.', { size: 19 }));
  b.push(text(62, 446, 'Silent on a clean machine.', { size: 19 }));

  b.push(text(400, 322, 'What past sessions left running:', { size: 18 }));
  const rows = [
    ['hidden browsers', 'orphan dev servers', 'endless shell loops'],
    ['Docker Desktop open for days', 'Claude sessions open for days'],
  ];
  rows.forEach((row, r) => {
    let x = 400;
    const top = 340 + r * 54;
    for (const label of row) {
      const w = Math.round(widthOf(label, 18, false) + 32);
      b.push(rect(x, top, w, 40, { rx: 20, fill: NAVY, stroke: SAND }));
      b.push(text(x + w / 2, top + 26, label, { size: 18, fill: HEAD, anchor: 'middle' }));
      x += w + 14;
    }
  });
  b.push(text(400, 476, 'Output: nothing at all, or a short list the session relays in one line.', { size: 18 }));

  return svg(
    H,
    'Two hooks: one blocks, one reports',
    'Before each Bash call the guard denies two destructive git commands and passes a quoted mention; at session start the leftover check lists five kinds of leftover process and stops none.',
    b,
  );
}

function rulesTimeline() {
  const H = 460;
  const AXIS_Y = 236;
  const X0 = 80;
  const X1 = 1120;
  const day = (m, d) => Date.UTC(2026, m - 1, d) / 86400000;
  const start = day(3, 5);
  const span = day(10, 4) - start;
  const xOf = (m, d) => X0 + ((day(m, d) - start) / span) * (X1 - X0);

  // tier: above, near (just below the axis) or far (further below, to clear a neighbor).
  const rules = [
    { m: 3, d: 5, date: 'March 5', name: 'human-go-gates', what: '1,399 emails, real people', tier: 'above', anchor: 'start', lx: 60 },
    { m: 6, d: 16, date: 'June 16', name: 'verify-the-live-object', what: 'Pay figure from spreadsheet', tier: 'near' },
    { m: 7, d: 3, date: 'July 3', name: 'many-chats-one-tree', what: 'Fix over uncommitted edits', tier: 'above' },
    { m: 8, d: 13, date: 'August 13', name: 'write-like-a-person', what: 'Chatbot voice in drafts', tier: 'far' },
    { m: 9, d: 2, date: 'September 2', name: 'ask-before-shared-state-writes', what: '8,500 rows, nobody asked', tier: 'above', lx: 985 },
    { m: 10, d: 4, date: 'October 4', name: 'stop-what-you-start', what: 'Laptop hot, memory full', tier: 'near', anchor: 'end', lx: 1160 },
  ];
  const TIERS = {
    above: { lead: [190, AXIS_Y - 10], rows: [128, 154, 180] },
    near: { lead: [AXIS_Y + 10, 262], rows: [284, 310, 336] },
    far: { lead: [AXIS_Y + 10, 354], rows: [376, 402, 428] },
  };

  const b = [];
  b.push(text(40, 54, 'Each rule carries the date of its mistake.', { serif: true, size: 30, fill: HEAD }));
  b.push(text(40, 84, 'Six rules, March 5 to October 4, 2026.', { size: 18 }));

  for (const r of rules) {
    const x = xOf(r.m, r.d);
    const t = TIERS[r.tier];
    b.push(line(x, t.lead[0], x, t.lead[1], { stroke: SUB }));
  }
  b.push(line(X0, AXIS_Y, X1, AXIS_Y, { stroke: SAND, sw: 2 }));
  for (const r of rules) {
    const x = xOf(r.m, r.d);
    const t = TIERS[r.tier];
    const anchor = r.anchor || 'middle';
    const lx = r.lx ?? x;
    b.push(circle(x, AXIS_Y, 10, { fill: TERRACOTTA, stroke: SAND, sw: 2 }));
    b.push(text(lx, t.rows[0], r.date, { size: 17, bold: true, anchor }));
    b.push(text(lx, t.rows[1], r.name, { size: 19, bold: true, fill: HEAD, anchor }));
    b.push(text(lx, t.rows[2], r.what, { size: 18, anchor }));
  }

  return svg(
    H,
    'Each rule carries the date of its mistake',
    'A timeline from March 5 to October 4, 2026 with six dots, one per rule, each labeled with the rule name and a four-word summary of the mistake behind it.',
    b,
  );
}

writeFileSync(join(OUT, 'two-hooks.svg'), twoHooks());
writeFileSync(join(OUT, 'rules-timeline.svg'), rulesTimeline());
console.log('wrote two-hooks.svg and rules-timeline.svg');
