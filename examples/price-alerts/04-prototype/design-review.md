# Price alerts · Design review (2026-11-04)

> Worked example. Review of the product screens against `prototype-craft.md` before the PM
> walkthrough. The workspace's `DESIGN.md` was still the blank template, so colours and type are
> a neutral, provisional system.

| Heuristic (0–4) | Quick set | Guided set |
|---|---|---|
| Visibility of system status | 3 | 4 |
| Match with the real world | 3 | 4 |
| User control and freedom | 4 | 3 |
| Consistency and standards | 4 | 4 |
| Error prevention | 2 | 4 |
| Recognition rather than recall | 3 | 4 |
| Flexibility and efficiency | 4 | 3 |
| Minimalism | 4 | 3 |
| Error recovery | 3 | 3 |
| Help | 2 | 3 |

**Weakest:** Quick set on error prevention and help (the investor never sees what will be sent);
Guided set on minimalism (presets and preview add reading).

## Fixed before the walkthrough
- P1 · Both: the bell and ID icons were emoji; redrawn as inline SVG in one stroke weight.
- P1 · Both: direction hints used ▲ and ▼ as icons; replaced with words ("Alerts you when the price
  rises to this").
- P1 · Guided set: the preview read "Bitcoin reached …" before a target was entered; it now updates
  as the investor types.

## Remaining
- P2 · Quick set: the sheet's backdrop is static; a real sheet would dim and dismiss on tap.
- P3 · Both: amounts are formatted for one locale only; the PRD's markets use the app's existing
  formats, so this waits for real copy.
