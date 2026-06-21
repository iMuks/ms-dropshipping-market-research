"""Render a set of SpecialistOutputs into the customer-facing markdown brief.

Pure rendering only — no IO, no scoring decisions (the orchestrator owns those
and passes the verdict/score in). The output shape matches the template in
``skills/.../SKILL.md`` so the brief looks the same whether it came from the
engine or the skill fallback (CONVENTIONS.md: DRY — one designed output shape).
"""
from __future__ import annotations

import json
import re
from typing import Any

from niche_research.brief.models import SectionName, SpecialistOutput

_SECTION_TITLE: dict[SectionName, str] = {
    SectionName.DEMAND: "§1 Demand",
    SectionName.COMPETITION: "§2 Competition",
    SectionName.SUPPLY: "§3 Supply",
    SectionName.TRAFFIC: "§4 Traffic",
    SectionName.COMMUNITY_NEEDS: "§5 Community Needs",
}


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "niche"


class BriefWriter:
    """Renders the opportunity brief markdown document."""

    def render(
        self,
        *,
        niche: str,
        geo: str,
        run_date: str,
        verdict: str,
        score: float,
        mode: str,
        contributions: dict[SectionName, float],
        outputs: dict[SectionName, SpecialistOutput],
        failures: dict[SectionName, str],
        provisional_reasons: list[str],
    ) -> str:
        slug = slugify(niche)
        lines: list[str] = []

        # Frontmatter.
        lines += [
            "---",
            f'niche: "{niche}"',
            f"slug: {slug}",
            f"geo: {geo}",
            f"run_date: {run_date}",
            f"verdict: {verdict}",
            f"score: {score:.2f}",
            f"mode: {mode}",
            "---",
            "",
            f"# Opportunity Brief — {niche.title()}",
            "",
        ]

        # Executive summary.
        present = ", ".join(_SECTION_TITLE[s].split(" ", 1)[1] for s in outputs)
        missing = [s for s in SectionName if s not in outputs]
        summary_bits = [
            f"> **Verdict: {verdict}** (score {score:.2f}). "
            f"Sections produced this run: {present or 'none'}."
        ]
        if missing:
            summary_bits.append(
                "Not yet covered: "
                + ", ".join(_SECTION_TITLE[s].split(" ", 1)[1] for s in missing)
                + "."
            )
        if provisional_reasons:
            summary_bits.append("Why PROVISIONAL: " + "; ".join(provisional_reasons) + ".")
        lines += [" ".join(summary_bits), ""]

        # Section bodies.
        for section in (
            SectionName.DEMAND,
            SectionName.COMPETITION,
            SectionName.SUPPLY,
            SectionName.TRAFFIC,
            SectionName.COMMUNITY_NEEDS,
        ):
            lines += self._render_section(section, outputs, failures)

        # §6 reconciliation (honest placeholder until reviewers land).
        lines += [
            "## §6 Cross-section reconciliation",
            "",
            "_F1–F13 cross-section reconciliation and the risk register require the "
            "paired reviewers + Supply/Traffic sections, which are not yet wired into "
            "the engine (see `engine/PLAN.md`). This run does not assert F1–F13._",
            "",
        ]

        # §7 final verdict + score breakdown.
        lines += ["## §7 Final verdict", ""]
        lines.append("| Section | Self-assessed score | Weight | Contribution |")
        lines.append("|---|---|---|---|")
        for section, contrib in contributions.items():
            out = outputs.get(section)
            sec_score = out.findings.get("section_score") if out else None
            lines.append(
                f"| {_SECTION_TITLE[section].split(' ', 1)[1]} | "
                f"{_fmt(sec_score)} | — | {contrib:.3f} |"
            )
        lines += [
            "",
            f"**final_score = {score:.3f}** (weighted over the sections that produced a "
            "score, renormalized).",
            "",
            f"**Verdict: {verdict}.** "
            + (
                "PROVISIONAL is the correct ceiling until Supply (strict), Traffic, and "
                "the paired reviewers land — the engine never emits APPROVED on a partial run."
                if verdict == "PROVISIONAL"
                else ""
            ),
            "",
        ]

        # §9 evidence appendix.
        lines += ["## §9 Evidence appendix", ""]
        any_evidence = False
        for section in outputs:
            out = outputs[section]
            if out.evidence:
                any_evidence = True
                lines.append(f"**{_SECTION_TITLE[section]}**")
                for ev in out.evidence:
                    note = f" — {ev.note}" if ev.note else ""
                    lines.append(f"- {ev.url} _(fetched {ev.fetched_at.isoformat()})_{note}")
                lines.append("")
        if not any_evidence:
            lines += ["_No evidence URLs cited this run._", ""]
        for section, reason in failures.items():
            lines.append(f"- **{_SECTION_TITLE[section]}: UNAVAILABLE** — {reason}")
        if failures:
            lines.append("")

        # §10 self-verification checklist.
        lines += self._render_checklist(outputs, verdict)

        return "\n".join(lines).rstrip() + "\n"

    # --- per-section renderers -------------------------------------------------

    def _render_section(
        self,
        section: SectionName,
        outputs: dict[SectionName, SpecialistOutput],
        failures: dict[SectionName, str],
    ) -> list[str]:
        title = _SECTION_TITLE[section]
        out = outputs.get(section)
        if out is None:
            reason = failures.get(section, "not enabled in pipeline.yaml")
            return [f"## {title} — UNAVAILABLE", "", f"_{reason}_", ""]

        f = out.findings
        body: list[str] = [f"## {title} — produced (confidence: {f.get('confidence', '—')})", ""]
        if out.summary:
            body += [out.summary, ""]

        if section is SectionName.DEMAND:
            body += self._render_demand(f)
        elif section is SectionName.COMPETITION:
            body += [f"**Major top products** (high-ticket validated: {_fmt(f.get('high_ticket_validated'))}):", ""]
            products = f.get("top_products") or []
            if products:
                body.append("| # | Product | Marketplace | Price (USD) | Reviews | Brand | URL |")
                body.append("|---|---|---|---|---|---|---|")
                for i, p in enumerate(products, 1):
                    body.append(
                        f"| {i} | {_s(p.get('name'))} | {_s(p.get('marketplace'))} | "
                        f"{_fmt(p.get('price_usd'))} | {_fmt(p.get('review_count'))} | "
                        f"{_s(p.get('brand'))} | {_s(p.get('url'))} |"
                    )
            else:
                body.append("_No verified bestsellers returned._")
            dist = f.get("price_tier_distribution") or {}
            body += [
                "",
                f"- **Median price:** {_fmt(f.get('median_price_usd'))}",
                f"- **Price-tier distribution:** {json.dumps(dist) if dist else '—'}",
                "",
            ]
        elif section is SectionName.COMMUNITY_NEEDS:
            body += [f"- **Subreddits read:** {_join(f.get('subreddits'))}", ""]
            comments = f.get("reddit_comments") or []
            if comments:
                body += ["**Reddit user comments (verbatim):**", ""]
                for c in comments[:15]:
                    theme = f" _[{c.get('theme')}]_" if c.get("theme") else ""
                    body.append(f"- “{_s(c.get('quote'))}” — {_s(c.get('subreddit'))}{theme}")
                    if c.get("url"):
                        body.append(f"  - {c['url']}")
                body.append("")
            body += self._render_needs(f)
            wtp = f.get("willingness_to_pay")
            if wtp:
                body += [f"**Willingness to pay:** {wtp}", ""]
            angle = f.get("positioning_angle")
            if angle:
                body += ["**Recommended positioning angle:**", "", angle, ""]
            traps = f.get("what_not_to_do") or []
            if traps:
                body += ["**What NOT to do:**"] + [f"- {t}" for t in traps] + [""]

        if f.get("caveats"):
            body += [f"_Caveats: {f['caveats']}_", ""]
        return body

    @staticmethod
    def _render_demand(f: dict[str, Any]) -> list[str]:
        out: list[str] = []
        my = f.get("multi_year") or {}
        intent = f.get("buyer_intent_mix_pct") or {}
        window = f.get("predicted_next_window") or {}

        out += [
            f"- **Head keywords:** {_join(f.get('head_keywords'))}",
            f"- **Approx. total monthly volume:** {_fmt(f.get('approx_total_monthly_volume'))}",
            f"- **Buyer-intent mix:** {_fmt(intent.get('transactional_commercial'))}% transactional/commercial, "
            f"{_fmt(intent.get('informational'))}% informational",
            f"- **Trajectory:** {f.get('trajectory', 'unknown')}",
            "",
        ]

        # Multi-year overlay (D2/D3/D4) — the "2 years back" requirement.
        out += [
            f"**Multi-year overlay** ({_fmt(my.get('window_months'))}-month window — "
            f"profile: {_s(my.get('seasonality_profile'))}, peaks repeat across years: "
            f"{_fmt(my.get('repeats_across_years'))}, peak-month drift: "
            f"{_fmt(my.get('peak_month_drift_days'))} days):",
            "",
        ]
        yoy = my.get("yoy_growth_pct_by_year") or []
        peaks = {str(p.get("year")): p.get("peak_month") for p in (my.get("peak_month_by_year") or []) if isinstance(p, dict)}
        ratios = {str(r.get("year")): r.get("ratio") for r in (my.get("peak_to_trough_ratio_by_year") or []) if isinstance(r, dict)}
        if yoy:
            out.append("| Year | YoY growth | Peak month | Peak/trough |")
            out.append("|---|---|---|---|")
            for row in yoy:
                if not isinstance(row, dict):
                    continue
                y = str(row.get("year"))
                gp = row.get("growth_pct")
                out.append(f"| {y} | {(_fmt(gp) + '%') if gp is not None else '—'} | {_s(peaks.get(y))} | {_s(ratios.get(y))} |")
        if my.get("trends_url"):
            out.append(f"\n_Multi-year Google Trends: {my['trends_url']}_")
        if f.get("seasonality_note"):
            out.append(f"\n{f['seasonality_note']}")
        out.append("")

        # Predicted next window (D8) — the "future seasonal demand" requirement.
        out += [
            "**Predicted next seasonal window (D8):**",
            f"- Starts ~**{_s(window.get('start_month'))}**, duration ~{_fmt(window.get('duration_weeks'))} weeks, "
            f"magnitude {_s(window.get('magnitude_vs_base'))}, confidence **{_s(window.get('confidence'))}**",
        ]
        if window.get("reasoning"):
            out.append(f"  - {window['reasoning']}")
        out.append(
            f"- **Recommended build → launch lead time:** "
            f"{_fmt(f.get('recommended_build_to_launch_lead_weeks'))} weeks"
        )
        out.append("")

        # Geographic breakdown (D6) — the "all geographically" requirement.
        geo = f.get("geographic_breakdown") or []
        out.append("**Geographic breakdown (D6):**")
        if geo:
            out.append("")
            out.append("| Region | Relative demand | Note |")
            out.append("|---|---|---|")
            for g in geo:
                if isinstance(g, dict):
                    out.append(f"| {_s(g.get('geo'))} | {_s(g.get('relative_demand'))} | {_s(g.get('note'))} |")
        else:
            out.append(" _UNAVAILABLE — no per-region breakdown returned._")
        out.append("")

        out += [
            f"- **Macro trend (D7):** {f.get('macro_trend_alignment', 'none')}"
            + (f" ({f['macro_trend_url']})" if f.get("macro_trend_url") else ""),
            f"- **Query freshness (D9):** {_fmt(f.get('query_freshness_pct'))}% of cited queries from last 12 months",
            "",
        ]
        return out

    @staticmethod
    def _render_needs(f: dict[str, Any]) -> list[str]:
        out: list[str] = []
        needs = f.get("top_needs") or []
        if needs:
            out += ["**Top stated needs:**", ""]
            for i, n in enumerate(needs, 1):
                out.append(f"{i}. **{_s(n.get('need'))}**")
                for q in n.get("quotes", []) or []:
                    url = f" ({q['url']})" if q.get("url") else ""
                    out.append(f"   - “{_s(q.get('quote'))}”{url}")
            out.append("")
        unmet = f.get("top_unmet_needs") or []
        if unmet:
            out += ["**Top unmet needs (with workaround):**", ""]
            for i, n in enumerate(unmet, 1):
                url = f" ({n['url']})" if n.get("url") else ""
                out.append(f"{i}. **{_s(n.get('need'))}** — workaround: “{_s(n.get('workaround_quote'))}”{url}")
            out.append("")
        return out

    @staticmethod
    def _render_checklist(outputs: dict[SectionName, SpecialistOutput], verdict: str) -> list[str]:
        comm = outputs.get(SectionName.COMMUNITY_NEEDS)
        comp = outputs.get(SectionName.COMPETITION)
        dem = outputs.get(SectionName.DEMAND)
        df = dem.findings if dem else {}
        my = df.get("multi_year") or {}

        def tick(ok: bool) -> str:
            return "x" if ok else " "

        has_multiyear = bool(my.get("trends_url") or my.get("yoy_growth_pct_by_year"))
        has_window = bool((df.get("predicted_next_window") or {}).get("start_month"))
        has_geo = bool(df.get("geographic_breakdown"))
        has_reddit = bool(comm and (comm.findings.get("reddit_comments") or comm.findings.get("subreddits")))
        has_angle = bool(comm and comm.findings.get("positioning_angle"))
        has_products = bool(comp and comp.findings.get("top_products"))
        all_cite = all(o.evidence for o in outputs.values()) if outputs else False

        return [
            "## §10 Self-verification checklist",
            "",
            f"- [{tick(has_multiyear)}] §1 includes a 24–36 month multi-year overlay (D2/D3 — not 12-month only)",
            f"- [{tick(has_window)}] §1 includes a predicted next seasonal window with confidence (D8)",
            f"- [{tick(has_geo)}] §1 includes a geographic breakdown (D6)",
            f"- [{tick(has_products)}] §2 includes marketplace bestseller intel (major top products)",
            f"- [{tick(has_reddit)}] §5 includes verbatim Reddit user comments / subreddits read",
            f"- [{tick(has_angle)}] §5 recommended positioning angle present",
            f"- [{tick(all_cite)}] Every produced section cites at least one fetched URL",
            "- [ ] §3 Supply has ≥3 verifiable suppliers (specialist not yet implemented)",
            "- [ ] §6 F1–F13 cross-section reconciliation (reviewers not yet implemented)",
            f"- [{tick(verdict != 'APPROVED')}] Verdict is not APPROVED on a partial run",
            "",
            "_Unchecked boxes are why the verdict is capped at PROVISIONAL. The engine "
            "never emits APPROVED until Supply, Traffic, and the paired reviewers land._",
            "",
        ]


# --- tiny formatting helpers (kept module-level; pure) -----------------------


def _s(value: Any) -> str:
    return "—" if value is None else str(value)


def _fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def _join(value: Any) -> str:
    if isinstance(value, list) and value:
        return ", ".join(str(v) for v in value)
    return "—"
