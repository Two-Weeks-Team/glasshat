# P17 — The Enterprise Buyer · Proposal

> **Bias**: SSO/SAML/audit · Trust &amp; Safety buyer at a Fortune-500
> **Reframing**: "Glasshat is not a hackathon entry. It's an enterprise AI evaluation platform that happens to be ship-tested by submitting to hackathons."

---

## 6-Tuple

```json
{
  "id": "P17",
  "advocate": "The Enterprise Buyer",
  "framing": "Glasshat is reframed as the audit layer for enterprise LLM evaluation under SOC 2, EU AI Act Article 12, NIST AI RMF, and ISO/IEC 42001 — the hackathon entries are evidence of ship-quality, not the product.",
  "target_persona": "Trust & Safety lead / AI Governance director at a Fortune-500 (regulated industries first: financial services, health, EU operators) who is on the hook for explainability artifacts when regulators or litigation ask.",
  "primary_surface": "Enterprise admin console + Trust Center: SAML 2.0 SSO, SCIM 2.0 user lifecycle, append-only audit log with SIEM streaming, role hierarchy (admin/reviewer/auditor/judge) with RBAC denials visible, data-residency selector (US/EU/APAC), BYOK, signed evidence-bundle export, EU AI Act Article 12 logging.",
  "opus_4_7_capability": "Opus 4.7's structured-output + long-context reasoning powers the RubricSynthesizer (parses your policy doc into a versioned rubric), the panel reasoning (six perspectives with citation discipline), and the Phoenix MCP runtime introspection summaries — all surfaces a compliance auditor would replay.",
  "mvp_scope": "4-day demo: enterprise admin dashboard (landing + admin console) showing tenant scoping, role switcher, real audit-trail rows with RBAC-deny events, Phoenix MCP log stream, and a working 'Export evidence (.zip · signed)' callout with a realistic 6-artifact preview package.",
  "one_liner_pitch": "Glasshat is the audit layer enterprises deploy when their LLM evaluation pipeline has to survive a SOC 2 audit, an EU AI Act inspection, or a litigation hold.",
  "spec_alignment_notes": "idea.spec.json not present in this run; reframed from raw one-liner. target_persona deliberately moved upstream from 'hackathon judge' to 'F500 T&S/Governance director' because the bias is SSO/SAML/audit — the judge user is preserved as one of four roles (constrained scope, read:assigned only) so the original hackathon use-case still slots in as a tenant role, not the product thesis."
}
```

---

## ASCII Wireframes

### landing.html — Enterprise SaaS hero

```
+--------------------------------------------------------------+
| [Glasshat]  Platform  Use cases  Security  Pricing  Trust    |
|                                  [Live demo] [Talk to found.]|
+--------------------------------------------------------------+
| (eyebrow) SOC 2 Type II observation period · started Apr 2026|
|                                                              |
| The *audit layer* for enterprise   |  +---------------------+|
| LLM evaluation.                    |  | Evidence export     ||
|                                    |  | run-2026-05-17-A91  ||
| Glasshat evaluates AI submissions  |  |  o Signed run rec   ||
| against your rubric, your way —    |  |  o Immutable audit  ||
| with signed evidence trails,       |  |  o EU AI Act bundle ||
| SAML/SCIM, regulator exports.      |  |  o NIST AI RMF att. ||
|                                    |  +---------------------+|
| [Talk to founders] [View demo]                               |
| SAML 2.0 · SCIM 2.0 · DPA/BAA                                |
+--------------------------------------------------------------+
| (DARK) COMPLIANCE POSTURE                                    |
| [SOC2 in progress] [EU AI Act ready] [NIST aligned] [ISO 42001 gap]|
+--------------------------------------------------------------+
| Design partners (NDA): [Bank] [SaaS] [Regulator] [Health]... |
+--------------------------------------------------------------+
| WHO DEPLOYS GLASSHAT INSIDE THE ENTERPRISE                   |
| [T&S]  [ML Platform]  [Eval team]  [AI Governance]           |
+--------------------------------------------------------------+
| SECURITY & PRIVACY                                           |
| SSO/SAML · SCIM · Audit log · Residency                      |
| Encryption · RBAC · Phoenix MCP · DPA/BAA                    |
+--------------------------------------------------------------+
| PRICING:  [Team $1.2K]  [Business $4.8K ★]  [Enterprise]    |
+--------------------------------------------------------------+
| (DARK CTA) Talk to founders / Visit Trust Center             |
+--------------------------------------------------------------+
| FOOTER: Platform | Compliance | Company | (badges)           |
+--------------------------------------------------------------+
```

### demo.html — Enterprise admin console

```
+----------+-------------------------------------------------+
| Glasshat | acme-fin-prod / Governance / **Audit trail**    |
| tenant:  |    [View as: Admin▼]  [Search]  [Export evid.]  |
| acme-fin |-------------------------------------------------|
| EU-Frank |  Audit trail · run-2026-05-17-A91               |
|          |  Acme Q2 Model Release Gate · rubric v3.2.1     |
| WORKSPACE|                                                 |
|  Eval    |  +--------+--------+--------+--------+          |
|  Rubrics |  | Events | SSO    | Drift  |Overrid.|          |
|  Runs    |  |  214↑  | 42 SAML|  3↓    |  7     |          |
|          |  +--------+--------+--------+--------+          |
| GOVERN.  |                                                 |
| *Audit*  |  +---------------------------------------------+|
|   (214)  |  | EXPORT AS EVIDENCE — regulator-ready bundle ||
|  Evid.exp|  | [Preview] [Export evidence (.zip · signed)] ||
|  Compli. |  +---------------------------------------------+|
|          |                                                 |
| IDENTITY |  +-------------------------+ +----------------+ |
|  Users   |  | AUDIT LOG · streaming • | | ROLE HIERARCHY | |
|  SSO/SAML|  | [All][Auth][Score][Over]| | • Admin (2)    | |
|  SCIM    |  |-------------------------| |   write:rubric | |
|          |  | 14:42 SJ admin EXPORT   | | • Reviewer (8) | |
| SETTINGS |  | 14:38 LV aud   VIEW     | |   override:scr | |
|  Residen.|  | 14:36 DP rev   OVERRIDE | | • Auditor (3)  | |
|  Integr. |  | 14:35 PX svc   DRIFT    | |   read-only    | |
|          |  | 14:35 PX svc   MCP call | |   export:evid  | |
|----------|  | 14:32 SJ admin APPROVE  | | • Judge (12)   | |
| [SJ]     |  | 14:30 SJ admin AUTH SSO | |   read:assign. | |
| Sarah J. |  | 14:28 LV aud RBAC-DENY  | |                | |
| admin    |  | 14:25 SJ admin SCIM sync| | SCIM last sync | |
+----------+  | ...                     | | 14:25 Okta · 0 | |
              | (18 of 214 visible)     | | orphans        | |
              +-------------------------+ +----------------+ |
                                                             |
              +---------------------------------------------+|
              | PHOENIX MCP — runtime introspection         ||
              | 14:35:11 INFO  phoenix.mcp.call get-exp-id  ||
              | 14:35:11 AUDIT qdrant.recommend → 6 anchors ||
              | 14:35:11 DRIFT z=2.31 yellow_hat            ||
              | 14:35:11 AUDIT calibration 8.4 → 7.12       ||
              | 14:35:12 OK    audit_loop.escalate=true     ||
              | 47 spans · 3 MCP calls · 0 uncaptured       ||
              +---------------------------------------------+|
                                                             |
              +---------------------------------------------+|
              | EVIDENCE PACKAGE · ready to seal            ||
              | [Signed run rec JSON] [Audit log CSV]       ||
              | [EU AI Act Art.12 ZIP] [NIST RMF PDF]       ||
              | [Phoenix replay JSONL] [Compliance map PDF] ||
              +---------------------------------------------+|
                                                             |
              +---------------------------------------------+|
              | FINAL REVEAL (dark)                         ||
              | "The deliverable isn't a score.             ||
              |  It's an *exportable evidence trail*."      ||
              | [Back to landing] [Talk to founders]        ||
              +---------------------------------------------+|
```

---

## Design rationale (why this beats the default reframing)

1. **The judge user becomes one of four roles** — not erased. A "Judge (read:assigned)" role appears in the RBAC card, so the original hackathon use-case fits in as a constrained tenant role. The product thesis is bigger than the contest.
2. **Audit trail is the hero**, not the rubric. A T&amp;S buyer reads an audit log first, scoring second. The page navigates to *Governance > Audit trail* by default, with 18 visible rows including an RBAC-deny event (the most credible single proof that the permission system actually fires).
3. **Phoenix MCP runtime introspection is reframed as a compliance feature** — not a tech-demo. The log block uses operational severity levels (INFO/AUDIT/DRIFT/OK), span IDs, and a "0 uncaptured paths" counter — the exact phrasing a CISO uses for explainability artifacts.
4. **The final reveal** swaps "rubric-faithful" for **"exportable evidence trail"** because rubric-faithfulness is a technical claim; evidence-trail-exportability is what wins the procurement call.
5. **Compliance posture is honest**: SOC 2 Type II is shown as "in progress" with an audit window, not as a checkmark. ISO 42001 is shown as "gap analysis" not "certified." This is what an enterprise buyer trusts.

## File sizes

| File | Bytes | Limit |
|---|---|---|
| landing.html | ~24 KB | ≤55 KB ✓ |
| demo.html | ~38 KB | ≤70 KB ✓ |
| _proposal.md | ~8 KB | — |
| **Total** | **~70 KB** | ≤90 KB ✓ |

## Constraints respected
- ✓ Vanilla HTML (no external CDN/fonts/images; inline SVG only; system font stack)
- ✓ OKLCH color space throughout (2026 trend + plugin convention)
- ✓ "Rubric-faithful" terminology preserved (in landing use-cases section + reveal phrasing)
- ✓ Self-contained (no external dependencies)
- ✓ Original Glasshat thesis (six hats, Phoenix MCP, Qdrant 6 collections, BMAD 17 items, Article 12 logging) preserved as substrate
