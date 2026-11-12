# Evidence rules

These rules apply to every skill in the PM Harness. They exist because a confident-sounding
summary of thin evidence is the most common way AI-assisted product work goes wrong.

1. **Count your sources.** Every theme, claim about users or problem statement says how many
   independent sources support it, e.g. `(4 interviews, 11 support tickets)`. Two mentions are
   a signal, not a pattern.
2. **Quote, don't paraphrase, the customer.** Customer language comes only from sources you
   actually read in this session. Never invent or "smooth" a quote.
3. **Grade the evidence.** Label each idea, PRD or research finding `strong` (several independent sources,
   including behavioural data), `some` (a few sources or one kind of source) or `hunch`
   (an internal opinion). Hunches are allowed; they are labelled.
4. **Numbers come from governed definitions.** Use the metric definitions listed in
   `context/metrics.md` and the queries or dashboards they point to, through the tool
   `context/tools.md` trusts for that metric. If you write an ad-hoc query, show it and label
   the number `ad hoc`. Never estimate a number and present it as measured.
5. **Show your working.** Every number in a document links to, or names, the query, dashboard
   or file it came from.
6. **Say what you could not see.** If a connector failed or has no tool in `context/tools.md`,
   a source was out of reach or access was refused, say so in the output instead of quietly
   working around it.
7. **Separate fact from inference.** Use "users said…", "data shows…" for facts and
   "this suggests…", "we believe…" for inference.
8. **Respect access.** Do not copy personal data about individual customers into product
   documents. Aggregate it.
9. **External numbers are benchmarks.** A number from outside the company (web research, a
   data provider, a competitor's site, a public report) carries its URL, its publication date
   and the date you read it, and is labelled `external`. It sits in its own section or column,
   never in the place of one of our metric values, and becomes a target only when the PM
   approves it (log that decision). When it disagrees with a governed internal number, the
   internal number stands and the gap is noted. Say when an external figure is more than a
   year old.
10. **Keep what a source requires.** When a source document names a requirement or a control
    (a post-mortem recommendation, a compliance rule), the PRD keeps it in its own words, or
    says `replaces <control>` with the reason and the owner who must agree. A rule the PRD
    attributes to the company names the file it comes from.
