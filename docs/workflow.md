# Physical Plausibility Engine for GST ITC Refund Adjudication

**Working title:** PACE — Premises-Aggregated Capacity Evidence
**Document type:** Study and design reference. No implementation.
**Purpose:** A precise, implementable specification to be consumed by a later implementation run.
**Status:** Draft 2. Sections marked `[CALIBRATE]` contain parameters requiring empirical sourcing; Section 16 defines the procedure and supplies Stage-1 anchors so the pipeline can run end to end before calibration completes. Sections marked `[VERIFY]` contain claims requiring confirmation at implementation time.

---

## 1. Scope of This Document

This document specifies **what** the system detects, **why** each detector is physically and legally defensible, **which open datasets** supply each input, and **how** outputs map to existing statutory instruments. It deliberately excludes code, framework choices, and deployment topology.

**Reading order.** Read Section 4 (Non-Goals) before Section 5 — several intuitively appealing approaches are excluded there for reasons that are load-bearing on the rest of the design. Then read Section 17 (Worked Example), which traces one case end to end with every intermediate value. Where the prose and the worked example disagree, **the worked example is authoritative and the prose is defective.**

For implementation, Sections 13–19 are the normative core: spatial semantics, attribution rules, schema, calibration, invariants, and build order. Sections 1–12 supply the reasoning behind them.

---

## 2. Problem Statement

### 2.1 The fraud being targeted

Fraudulent Input Tax Credit (ITC) refund claims under Indian GST, executed via networks of non-existent or non-operational registered entities. The canonical pattern:

1. A cluster of newly registered GSTINs issue invoices for goods that are never supplied.
2. Recipients accumulate ITC against those invoices without any corresponding tax reaching the treasury.
3. Accumulated ITC is monetised through a refund route — commonly zero-rated supply (exports or SEZ supply), where the refund is a cash outflow from the treasury rather than an offset.
4. Value may be additionally inflated by over-invoicing, so a small physical quantity of cheap goods carries a large declared value.

### 2.2 Why document-based detection is structurally weak

The paper trail in these cases is **internally consistent by construction**. Registrations are valid, invoices are correctly formatted, e-way bills are generated, and customs documentation exists. Any detector that only reads the taxpayer's own declarations is evaluating an artefact the fraudster fully controls.

### 2.3 The exploitable asymmetry

The fraudster controls declarations. The fraudster does not control:

- **The physical world** — the premises they registered either can or cannot hold and move the declared volume of goods.
- **Third-party price formation** — the market price of a commodity is set outside the syndicate.
- **Network topology** — the structure of the invoice graph is an emergent property of the fraud, not a field the fraudster fills in.

The system's entire value proposition rests on measuring quantities from these three uncontrolled channels and testing them against declarations.

---

## 3. Core Hypothesis and the Falsifiable Claim

### 3.1 Hypothesis

> For any entity declaring supply of physical goods, the declared throughput implies a minimum physical footprint and handling capacity at its registered premises. Where declared throughput exceeds what the observed premises can support, the declaration is physically infeasible regardless of documentary consistency.

### 3.2 The claim the system makes

The system does **not** claim "no factory exists at this address." That claim is hard to prove, easy to attack, and often false for legitimate business models.

The system claims:

> **Given premises footprint of A square metres, the aggregate throughput declared by all entities registered to that footprint is infeasible by a factor of N.**

This is arithmetic over two measured quantities. It is falsifiable, quantifiable, and survives cross-examination.

### 3.3 The dual-constraint closure argument

This is the intellectual core and should anchor any presentation of the system.

Let an entity declare value `V` against quantity `Q` for a commodity with HSN `h`, giving unit price `p = V / Q`.

- **Constraint A (price closure):** `p` must lie within the empirical distribution of unit prices observed for HSN `h`.
- **Constraint B (capacity closure):** `Q` must lie within the physical handling capacity of the observed premises over the declared period.

To inflate `V`, a fraudster must raise `p` or raise `Q`. Raising `p` violates A. Raising `Q` violates B.

**The two constraints have no common region in which large-scale value inflation is feasible.** Which constraint binds depends on fraud mode:

| Fraud mode | Binding constraint | Detector |
|---|---|---|
| Over-invoicing (high value, low mass) | Price closure | D1 |
| Volume inflation (high mass, real-ish price) | Capacity closure | D2 |
| Pure paper shell (no goods at all) | Existence / aggregation | D3 |
| Syndicate coordination | Network topology | D4 |

No single detector covers all modes. This is by design, and the coverage matrix above should be stated explicitly rather than glossed over.

---

## 4. Non-Goals and Explicit Exclusions

These exclusions are design decisions with reasons. Reversing any of them requires revisiting the reasoning.

### 4.1 Excluded: atmospheric trace-gas detection for premises-level verification

**Do not use Sentinel-5P / TROPOMI NO₂ (or SO₂, CO, CH₄) to assess individual premises.**

TROPOMI's native ground footprint is approximately 5.5 × 3.5 km at nadir, roughly 20 km² per retrieval ([Copernicus AMT, 2025](https://amt.copernicus.org/articles/18/4373/2025/index.html)). Gridded Level-3 products resampled to ~1.1 km add no information; adjacent grid cells carry the same underlying measurement.

Two independent failure modes:

1. **No discriminating power.** A bounding-box statistic over a single premises returns regional background, identical for a real and a ghost site in the same district.
2. **Signal inversion and geographic bias.** Tropospheric NO₂ over India is dominated by traffic, power generation, and urban activity. Using it as a filter that "confirms industrial activity in the area" *clears* shell entities registered in dense industrial and urban corridors, and *flags* legitimate small manufacturers in low-background rural areas. The variable proxies urbanisation, not premises existence.

The second failure mode is disqualifying independently of resolution: it would produce a system that systematically penalises rural and small taxpayers.

### 4.2 Excluded: thermal signature as a general-purpose detector

Thermal infrared can indicate operational status for **thermally intensive processes only**. Landsat 8/9 TIRS is 100 m native (delivered on a 30 m grid). VIIRS is 375 m (I-band) and 750 m (DNB) — not 30–100 m, and VIIRS Nightfire is tuned to sub-pixel very-hot combustion sources such as gas flares, not ordinary factory operation.

Thermal is admissible only where the declared HSN maps to an expected thermal signature (see the HSN Signature Map, Section 6.4). For tobacco processing, apparel, packaging, and electronics assembly it contributes nothing and must not be evaluated.

### 4.3 Excluded: sub-pixel structure detection

Free optical imagery (Sentinel-2, 10 m) cannot determine presence or absence of a structure smaller than roughly 1–2 pixels. A 60 m² room is sub-pixel. **Do not attempt per-site existence detection for small premises using 10 m imagery.**

This is the same class of error as 4.1, one order of magnitude down. The design response is aggregation (D3), not higher resolution.

### 4.4 Excluded: automated refund denial

No adverse financial action is taken by the system. Blocking of credit under Rule 86A of the CGST Rules requires an officer to record *reasons to believe* in writing, and the scope of that power has attracted judicial scrutiny. The system produces evidence and drafts reasons; a human officer decides. See Section 10.

### 4.5 Excluded as novelty claims (prior art)

Do not present the following as original contributions. All are established or already deployed:

- Satellite estimation of industrial output for steel, cement, and coal, used for emissions and economic monitoring ([TransitionZero methodology](https://www.transitionzero.org/insights/steel-data-explainer); [thermal IR monitoring of steel plants, MDPI 2023](https://www.mdpi.com/2071-1050/15/11/8575)).
- Aerial and satellite detection of undeclared buildings for **property tax** enforcement, widely deployed.
- Geospatial analytics applied to income tax non-compliance ([Johns Hopkins, 2024](https://jscholarship.library.jhu.edu/items/1f4f8874-de6f-4211-85ed-8822d8e067a3)).
- Machine learning on Indian state tax return data to predict non-existent firms ([ACM JCSS, 2024](https://dl.acm.org/doi/10.1145/3676188)).
- Graph-based fraud detection on transaction networks.
- Geocoding of GST registered addresses — already a GSTN service; geotagging for risky registrations has been [under active CBIC consideration since 2023](http://economictimes.indiatimes.com/news/economy/policy/geotagging-may-become-must-for-gst-registrations/articleshow/101438613.cms).
- Risk-based withholding of exporter refunds — operational via DGARM since 2019 ([CBIC Circular 131/2020](https://cbic-gst.gov.in/pdf/Circular-131-1-2020-GST-Exporter.pdf)).
- Cross-verification of e-way bill vehicle numbers against VAHAN — [already implemented](https://www.vjmglobal.com/blog/integration-of-e-way-bill-portal-with-vahan-portal).

### 4.6 The candidate novelty claim

**Evidence status: preliminary.** The claim below rests on a first-pass literature and web search of roughly a dozen queries across tax analytics, remote sensing of industrial activity, and Indian GST enforcement. That is enough to say no directly comparable work *surfaced*, and not enough to assert novelty. A systematic search is a tracked task (Section 19, Phase 6) covering at minimum: academic databases, patent filings, national revenue authority technical publications, and OECD / IMF tax administration working papers. State it as "we found no directly comparable system" and not as "this is the first."

The candidate claim:

> Use of open earth-observation building footprints to compute **aggregate declared throughput per unit area of shared registered premises**, benchmarked against an empirical sector-and-district distribution, as an evidentiary precondition on ITC refund disbursement — with auto-drafted statutory reasoning.

Supporting context that strengthens rather than weakens this claim: Indian law already accepts capacity-based reasoning for the commodity class most associated with these frauds. [Notification 04/2024-Central Tax](https://www.gstcouncil.gov.in/sites/default/files/2024-05/04-2024-ct-eng.pdf) requires pan masala and tobacco manufacturers to declare each packing machine's installation address, packing capacity, and electricity consumption in Form GST SRM-I. Declared capacity is already collected. Nothing reconciles it against observed physical premises.

Claim the composition. Do not claim the components.

---

## 5. Detector Architecture

Four independent detectors. Each produces a score, a confidence, and a human-readable finding. Fusion rules in Section 9.

### D1 — Price Closure

**Detects:** over-invoicing, including export and SEZ-supply overvaluation.
**Requires satellite data:** No.
**Inputs:** declared value and quantity per invoice line, HSN code, unit of measure.

**Method.** For HSN `h`, build a reference distribution of unit prices from third-party trade statistics. Because prices are multiplicative, work in log space and use a robust dispersion estimate:

```
p_i        = V_i / Q_i
z_i        = (ln p_i − median(ln p_h)) / (1.4826 × MAD(ln p_h))
```

Flag on `z_i` exceeding a calibrated threshold `[CALIBRATE]`. Report the finding as a plain multiple, not a z-score: *"declared at 30× the median export unit value for this HSN."*

**Notes.**
- Unit-of-measure normalisation is the main source of error. A kg/piece confusion produces spurious extreme outliers. UQC normalisation must be explicit and auditable.
- Minimum sample size per HSN before the benchmark is usable `[CALIBRATE]`. Sparse HSNs fall back to HS-4 aggregation with a recorded confidence penalty.
- Genuine premium products are legitimate outliers. D1 alone must never trigger adverse action.

**Why this detector matters most.** For the over-invoicing fraud mode — the mode in the largest documented SEZ export-refund cases — D1 is the binding constraint and requires no earth observation at all. It should be built first.

### D2 — Capacity Closure

**Detects:** volume inflation; declared throughput exceeding premises capability.
**Requires satellite data:** Yes (building footprint).

Two formulations. The empirical one is primary because it requires no invented physical constants.

**D2a — Empirical throughput density (primary).**

```
For premises footprint F with area A_F:
  E(F)          = { entities whose registered-premises geocode falls within F }
  V_agg(F, t)   = Σ declared outward value over period t, across E(F)
  density(F, t) = V_agg(F, t) / A_F            [₹ per m² per period]
```

Benchmark `density` against the empirical distribution of the same statistic across all footprints in the same **district × HSN-sector** stratum. Use the same robust log z-score as D1.

This is parameter-free. It cannot be attacked with "where did your constants come from," which is the primary vulnerability of D2b.

**Benchmark circularity — a known methodological hole.** The reference distribution is drawn from the same population being scored. On synthetic data this is partly circular: the benchmark comes from the corpus generator, so measured performance partly reflects generator assumptions rather than detector quality. Two mitigations, both required:

1. **Prevalence separation.** Generate the background population independently of fraud injection, hold fraud prevalence low and documented, and report threshold sensitivity across a prevalence sweep.
2. **Clean-cohort benchmarking.** On real data, construct strata from entities with established clean filing history rather than the full population, so the reference is not contaminated by the behaviour being detected.

Any accuracy figure produced from synthetic runs must carry this caveat explicitly. It is a limitation of the evaluation, not of the detector, but it bounds what can honestly be claimed.

**D2b — Physical capacity model (secondary, explanatory).**

Used *after* D2a flags, to express the finding in physical terms an officer or court can act on.

```
Storage:
  A_required = (M_period / turns_period) / (ρ_bulk × h_usable × η_floor)

Handling:
  N_loads    = M_period / C_truck
  H_required = N_loads × t_turnaround
  H_available = N_docks × h_operating × d_working

Road access:
  C_truck capped by maximum vehicle class admissible on the narrowest
  segment of the access route
```

All of `ρ_bulk`, `h_usable`, `η_floor`, `turns_period`, `C_truck`, `t_turnaround` are `[CALIBRATE]` per HSN sector and **must be sourced to a citable standard** before use in any adverse finding. Candidate sources: cost accounting standards on capacity determination, warehousing design norms, motor vehicle axle-load rules. Unsourced constants reduce a falsifiable inequality to hand-waving.

**Known limitation, stated explicitly.** D2 is weak for high-value-density goods. Worked example: ₹1,000 crore of tobacco declared at an inflated ₹9,000/kg implies roughly 1,100 tonnes. Distributed across 25 supplier entities, that is ~45 tonnes each — approximately three truckloads and a few tens of square metres of floor per entity per month. **Physically feasible.** D2 therefore does not catch the canonical over-invoicing case; D1 and D3 do. D2 binds on bulk commodities — scrap metal, coal, plastic granules, textiles, agricultural produce.

### D3 — Premises Aggregation and Existence

**Detects:** shell clusters; multiple "manufacturers" sharing one physically inadequate premises.
**Requires satellite data:** Yes (building footprint, land cover).

This is the detector that addresses the canonical ghost-supplier pattern, and it works **because** it aggregates, sidestepping the sub-pixel limit in Section 4.3.

**Signals.**

| Signal | Definition | Interpretation |
|---|---|---|
| Footprint occupancy | count of goods-supplying GSTINs geocoding into one footprint | many manufacturers, one small building |
| Entity density | `|E(F)| / A_F` per 100 m² | implausible concentration |
| Structure presence | any building polygon within radius `r` of geocode `[CALIBRATE]` | no structure at all |
| Land cover class | ESA WorldCover class at geocode | manufacturing declared on cropland or bare ground |
| Structure age | first-appearance year from settlement-evolution data or optical change detection | premises postdates the claimed activity |
| Access adequacy | road class and width at nearest access | no truck-capable access |

The decisive finding is not "this address is empty." It is: *"these 25 entities, collectively declaring ₹1,000 crore of manufactured supply, are registered to a single footprint of 80 m² classified as residential built-up."*

### D4 — Network Topology

**Detects:** syndicate structure; ITC chains with no tax-paying origin.
**Requires satellite data:** No.

Construct a directed multigraph: nodes = GSTINs, edges = invoice flows with value, quantity, HSN, date.

**Features.**

- **Upstream tax origin depth** — distance to the nearest node that has discharged tax in cash. Fabricated chains terminate quickly in nodes with negligible cash tax.
- **Cash-to-ITC ratio** — proportion of liability discharged in cash versus offset by credit.
- **Registration age versus billing velocity** — value billed per day since registration.
- **Cycle detection** — circular trading among a closed set.
- **Shared-identifier clustering** — common PAN, authorised signatory, bank account, mobile, email across nominally unrelated suppliers.
- **Address collision** — multiple GSTINs at one address (feeds D3).
- **Concentration** — proportion of a recipient's ITC originating from a single supplier cluster.

Interpretability requirement: every D4 finding must be expressible as a named pattern with a visualisable subgraph. An opaque score will be ignored by officers and cannot support a written reason.

---

## 6. Data Layer

### 6.1 Selection principles

1. **Open licence, no organisational gating.** Any component requiring institutional affiliation, a negotiated agreement, or non-commercial-only terms is excluded from the core path.
2. **Bulk-downloadable in preference to API-metered**, so the pipeline is reproducible offline.
3. **Every dataset carries a recorded licence and attribution string** in the output dossier.

### 6.2 Geospatial datasets

| Dataset | Provides | Resolution | Licence | Status | Access |
|---|---|---|---|---|---|
| Overture Maps — Buildings | Building footprint polygons | Vector | ODbL 1.0 | Verified | [docs](https://docs.overturemaps.org/guides/buildings/) · GeoParquet on AWS and Azure · [licence note](https://docs.overturemaps.org/blog/2024-01-17-alpha.0/) |
| ESA WorldCover | Land cover, 11 classes | 10 m | CC BY 4.0 | Verified | [data access](https://esa-worldcover.org/en/data-access) · [AWS Open Data](https://registry.opendata.aws/esa-worldcover-vito/) |
| Copernicus Sentinel-2 L2A | Optical, change detection | 10 m | Free, full and open | Verified | [Copernicus Data Space](https://dataspace.copernicus.eu/terms-and-conditions) |
| Copernicus Sentinel-1 GRD | SAR, cloud-independent structure | ~10 m | Free, full and open | Verified | Copernicus Data Space |
| OpenStreetMap | Road network, access width, land use | Vector | ODbL 1.0 | Verified | Geofabrik regional extracts |
| Landsat 8/9 Collection 2 L2 | Surface temperature, conditional use only | 100 m native | US public domain | Verified | USGS EarthExplorer |
| Google Open Buildings | Building footprints, alternative source | Vector | Stated as CC BY 4.0 / ODbL 1.0 | `[VERIFY]` | Confirm terms before adoption |
| Microsoft Building Footprints | Building footprints, alternative source | Vector | Stated as ODbL | `[VERIFY]` | Confirm terms before adoption |
| World Settlement Footprint / Evolution | Settlement extent and first-appearance year | 10–30 m | Stated as CC BY 4.0 | `[VERIFY]` | Confirm terms before adoption |

**Recommendation.** Use **Overture Buildings** as the primary footprint source. Its licence is confirmed, it is distributed as GeoParquet on public object storage with no gating, and it already fuses OSM, Esri, and ML-derived footprints from multiple providers — making it a superset of the alternatives listed as `[VERIFY]`.

**Deliberately excluded from the core path:** commercial sub-metre imagery (Planet, Maxar), proprietary basemap tile services, and any managed cloud analysis platform whose terms restrict redistribution or field of use. These may be referenced as production-upgrade options but must not be dependencies.

### 6.3 Tax, trade, and reference datasets

| Dataset | Provides | Licence | Notes |
|---|---|---|---|
| UN Comtrade | HS-level trade value and quantity → unit price benchmark | Free tier, open registration | 500 calls/day, 100k records/call at [Comtrade Plus](https://comtradeplus.un.org/TradeFlow). Registration is individual, not institutional. |
| India commerce ministry trade statistics | Indian export unit values at HS-8 | Government open data | Preferred for D1: matches Indian export context directly |
| data.gov.in catalogues | PIN centroids, administrative boundaries, sector statistics | [GODL-India](https://data.gov.in/sites/default/files/NDSAP_OpenDataLicense.pdf) | Attribution required |
| GST public GSTIN search | Legal name, address, status, filing history for a known GSTIN | Public service | Per-GSTIN lookup only. **No bulk or transaction-level access.** |
| Agricultural market price feeds | Commodity spot prices for agri HSNs | Government open data | Useful D1 benchmark where trade data is sparse |

**The binding data constraint.** Transaction-level GST data — GSTR-1, GSTR-2B, e-way bills, refund applications, electronic credit ledger — is confidential and will not be available. **All development and evaluation runs on synthetic data (Section 11).** This must be stated openly in any presentation, alongside a specific integration request describing exactly which fields would be required from GSTN in production.

### 6.4 Required derived artefacts

Three lookup tables that must be constructed and version-controlled. These are project deliverables, not incidental config.

**HSN Signature Map.** For each HSN sector: declared-role implication (manufacturer / trader / warehouse / job-worker / service), whether physical premises are implied at all, whether a thermal signature is expected, expected bulk density range, typical unit-price range. This table is what makes the system defensible rather than discriminatory — it is the mechanism by which a trading company is never penalised for having no factory.

**Capacity Parameter Table.** The `[CALIBRATE]` constants of D2b, each with a citable source. Unsourced entries must be marked and must block adverse findings for that sector.

**Geocode Confidence Schema.** Tiers with explicit definitions: rooftop / building-centroid / street / locality-centroid / unresolved. Section 8.2 depends on this.

### 6.5 Sensor capability reference

Include this table in any technical presentation. Volunteering the limits establishes credibility faster than any capability claim.

| Sensor | Native resolution | Revisit | Valid use here | Invalid use |
|---|---|---|---|---|
| Sentinel-5P TROPOMI | 5.5 × 3.5 km | Daily | Regional air-quality context only | Any premises-level inference |
| Sentinel-2 MSI | 10 m | ~5 days | Footprint of large structures, change detection | Sub-pixel structure presence |
| Sentinel-1 SAR | ~10 m | ~6–12 days `[VERIFY]` | Cloud-independent large-structure detection | Small premises discrimination |
| Landsat 8/9 TIRS | 100 m | 16 days | Hot-process operational status | Non-thermal sectors; small units |
| VIIRS DNB | 750 m | Nightly | Industrial-estate scale context | Premises-level anything |
| Building footprint vectors | Sub-metre derived | Static per release | Footprint area, occupancy, collision | Real-time activity |

---

## 7. Pipeline Stages

Linear stages with defined artefacts. Each stage's output is independently inspectable — a requirement, not a convenience, because the dossier in P7 must reconstruct the full chain.

### P0 — Trigger

**In:** refund application above a threshold `[CALIBRATE]`, or periodic sweep, or ITC-accumulation anomaly.
**Out:** case record with subject GSTIN, claim period, claimed amount, refund route.

### P1 — Role Classification and Applicability Gate

**In:** subject GSTIN registration data, declared HSNs, business constitution.
**Out:** declared role; per-detector applicability flags.

**Gate rule.** D2 and D3 apply only where the declared role implies physical handling of goods at the registered premises. Pure service providers, traders without warehousing, and job-work arrangements are exempted from physical tests by construction. **Skipping this gate produces a false-accusation machine.**

### P2 — Entity and Network Assembly

**In:** invoice records for the subject and its upstream suppliers to depth `k` `[CALIBRATE]`.
**Out:** directed multigraph; shared-identifier clusters; D4 feature vector.

### P3 — Site Resolution

**In:** declared principal and additional places of business.
**Out:** coordinates with confidence tier; matched footprint polygon identifier; land cover class; access-road attributes.

**Method.** Prefer coordinates already captured by GSTN geocoding where available. Otherwise self-hosted open geocoding — [Nominatim](https://github.com/osm-search/Nominatim) or equivalent. **Do not use the public OSM Nominatim endpoint for bulk work**; it is [expressly prohibited by usage policy](https://operations.osmfoundation.org/policies/nominatim/).

**Hard gate.** Below street-level confidence, no adverse physical finding may be produced. The case routes to *address unverifiable → field verification required*. This single rule is the primary control against false accusation and must not be made configurable.

### P4 — Physical Envelope Extraction

**In:** matched footprint, land cover, optional imagery.
**Out:** footprint area, estimated floor count, structure presence and confidence, first-appearance year, access adequacy, and — only where the HSN Signature Map expects it — thermal status.

### P5 — Declared Throughput Extraction

**In:** invoice lines and movement records for the claim period.
**Out:** value and normalised mass per HSN per period, per registered premises.

UQC normalisation happens here and must be logged, since it is the dominant error source for both D1 and D2.

### P6 — Detector Evaluation and Fusion

**In:** all prior artefacts.
**Out:** per-detector score, confidence, and finding text; fused risk tier per Section 9.

### P7 — Evidence Dossier

**Out:** a single officer-facing document containing: entity identification; the network subgraph as a figure; the price-outlier position against its benchmark distribution; the footprint map with occupancy overlay; the throughput-density computation shown step by step; every data source with product identifier, acquisition date, licence, and attribution; and the geocode confidence tier.

**The dossier is the product.** An unexplained score gets ignored. A one-page case file with independent, traceable evidence gets acted on.

### P8 — Feedback and Calibration

**In:** field verification outcomes; taxpayer contestation submissions.
**Out:** labelled examples; recalibrated thresholds; a published error-rate report.

Taxpayers must have a route to contest with ground evidence — lease deeds, electricity bills, dated photographs. Overrides are recorded and become training labels. A system that never reports its own false-positive rate will not be trusted by the officers who have to use it.

---

## 8. Scoring Model

### 8.1 Structure

Each detector emits a score in `[0, 1]` and a confidence in `[0, 1]`. Fusion is a transparent weighted combination with hard corroboration rules — not a learned black box, because P7 requires that every contribution be explainable and Rule 86A requires written reasons.

### 8.2 Corroboration rules

These are constraints on the fusion output, not weights.

1. **No adverse tier from a physical detector alone.** D2 or D3 must be corroborated by at least one of D1 or D4.
2. **No adverse tier below street-level geocode confidence.** Enforced at P3; restated here because it is the highest-consequence rule in the system.
3. **No adverse tier where the applicability gate excluded the physical detectors** unless D1 and D4 independently exceed their own thresholds.
4. **Unsourced capacity parameters block D2b findings** for the affected sector.

### 8.3 Decision tiers

| Tier | Condition | Action |
|---|---|---|
| Green | no detector above threshold | refund proceeds normally |
| Amber | single detector, or low confidence | refund proceeds; flagged for post-disbursement audit |
| Red | corroborated across detector families | physical verification of premises before disbursement |
| Red + cluster | Red plus syndicate cluster identified | escalate for credit-blocking consideration with drafted reasons |

---

## 9. Legal and Procedural Mapping

The system attaches to instruments that already exist. This is a feasibility argument, not a legal opinion — statutory positions must be confirmed with a practitioner before any pilot.

| System output | Existing instrument | Note |
|---|---|---|
| Red tier before disbursement | physical verification of premises | already a prescribed verification route |
| Refund held pending verification | refund withholding provisions under the refund rules | mechanism operational via DGARM risk flags since 2019 |
| Credit blocking recommendation | Rule 86A, CGST Rules | requires officer's *reasons to believe* recorded in writing |
| Registration-stage flag | registration verification guidelines | see [CBIC Instruction 03/2025-GST](https://cbic-gst.gov.in/pdf/ins-gst-no-03-2025.pdf) |
| Declared-capacity reconciliation | Form GST SRM-I, [Notification 04/2024-CT](https://www.gstcouncil.gov.in/sites/default/files/2024-05/04-2024-ct-eng.pdf) | pan masala and tobacco; declared machine capacity already collected |

**High-value integration point.** Rule 86A requires written reasons. The system should auto-draft that reasoning from the dossier, citing specific evidence with provenance. This is concrete, immediately useful to an officer, and directly addresses documented judicial concern about how the power is exercised. CBIC Instruction 03/2025-GST explicitly notes the twin objective of preventing fraudulent ITC-passing registrations *while not harassing genuine applicants* — the fairness controls in this document map onto the second half of that mandate.

---

## 10. Fairness and False-Positive Controls

Every control here exists because its absence produces a specific, foreseeable harm.

| Control | Prevents |
|---|---|
| Role applicability gate (P1) | penalising traders and job-workers for having no factory |
| Geocode confidence gate (P3) | adverse findings against the wrong premises |
| Sector-conditional sensor selection (6.4) | penalising non-thermal industries for absent heat |
| Empirical benchmarking within district × sector strata (D2a) | penalising rural or small operators against urban norms |
| Corroboration requirement (8.2) | single-signal accusations |
| Contestation route (P8) | unappealable automated determination |
| Stratified error reporting (Section 12) | invisible systematic bias |

**Mandatory fairness audit.** False-positive rate must be reported stratified by urban/rural classification, entity turnover band, and geographic region. An aggregate accuracy figure conceals exactly the bias this system is most at risk of exhibiting. If FPR is materially higher for rural or small entities, the system is not fit for use regardless of headline accuracy.

---

## 11. Synthetic Dataset Specification

Real transaction data is unavailable (6.3). The synthetic corpus is therefore a primary deliverable and its realism bounds every claim the project can make.

### 11.1 Required entities

| Table | Key fields |
|---|---|
| Registration | GSTIN, legal name, PAN, constitution, registration date, status, principal and additional premises addresses, declared HSNs, authorised signatory, bank account, contact |
| Invoice line | supplier, recipient, date, HSN, quantity, UQC, taxable value, tax amount, place of supply |
| Movement record | invoice reference, origin, destination, distance, vehicle identifier, declared gross weight, generation timestamp |
| Return summary | period, outward value, ITC availed, tax paid in cash, closing credit balance |
| Refund claim | period, route, amount, supporting documents |

### 11.2 Injected patterns

Positives:

- **P1 — Pure shell chain.** Newly registered suppliers, negligible cash tax, no genuine upstream origin, address collision at a small footprint.
- **P2 — Over-invoiced zero-rated supply.** Real but cheap goods declared at extreme unit price, refund claimed on accumulated credit.
- **P3 — Circular trading.** Closed cycle inflating turnover with no net outward supply.
- **P4 — Volume inflation.** Bulk-commodity mass declared far beyond premises capacity.
- **P5 — Footprint collision cluster.** Many nominal manufacturers on one inadequate footprint.

Hard negatives — as important as the positives, and the part most projects omit:

- **N1 — Legitimate trading company** with no manufacturing premises at all.
- **N2 — Legitimate small rural manufacturer**, low absolute values, no thermal signature, sparse imagery.
- **N3 — Legitimate job-work arrangement** where goods are processed at a third party's premises.
- **N4 — Legitimate premium-product exporter** with a genuinely high unit price.
- **N5 — Legitimate shared industrial estate** with many co-located registrations in an adequate footprint.
- **N6 — Legitimate entity with an unresolvable address**, to exercise the P3 gate.

N1, N2, N3, and N4 each defeat a naive version of one detector. A system that does not clear all four is not ready.

### 11.3 Grounding requirement

Synthetic premises must be placed on **real footprints** drawn from Overture, in real districts, with real land cover and real road access. Only the tax records are synthetic. This keeps the geospatial half of the pipeline honest and makes the demo verifiable against public basemaps.

---

## 12. Evaluation Methodology

### 12.1 Metrics

- **Precision@k** on a ranked case list, where `k` reflects realistic officer capacity. This is the operationally meaningful metric: officers work a queue, not a threshold.
- **Recall per injected pattern**, reported separately. Aggregate recall hides which fraud modes are uncovered.
- **False-positive rate on the hard-negative set**, reported per negative class.
- **Stratified FPR** per Section 10.
- **Detector marginal contribution** — ablation, to establish whether the earth-observation component earns its complexity over the paper-only detectors. This is the single most important scientific question the project can answer, and an honest negative result on some sectors is a legitimate finding.

### 12.2 Ablation matrix

Report performance for: D1 alone; D1+D4 (paper only); D1+D4+D3; all four. If the paper-only configuration performs comparably on the dominant fraud mode, say so. That finding is more credible than an overstated claim and is itself a contribution.

---

## 13. Spatial Semantics and Premises Clustering

Ambiguity here changes results silently. Every rule below is normative.

### 13.1 Unit of analysis: the premises cluster, not the raw polygon

**Do not use raw footprint polygons as the denominator in D2a.** Vector building datasets fragment large structures inconsistently — a single industrial shed may appear as one polygon in one district and six adjoining polygons in another.

The failure is asymmetric and the dangerous direction is fragmentation:

| Dataset artefact | Effect on area | Effect on density | Consequence |
|---|---|---|---|
| Fragmentation (one shed → many polygons) | understated | overstated | **false positive** |
| Over-merging (many sheds → one polygon) | overstated | understated | false negative |

False negatives are tolerable. False positives against a real manufacturer are not. Therefore:

> **Rule 13.1.** The unit of analysis is a **premises cluster**: the dissolved union of all footprint polygons whose boundaries lie within buffer distance `b` of one another. Compute cluster area from the dissolved geometry. `b = 5 m` as a Stage-1 anchor `[CALIBRATE]`.

Dissolve is computed once per district and cached with the dataset version recorded.

### 13.2 Coordinate reference and area computation

| Concern | Rule |
|---|---|
| Storage CRS | EPSG:4326 (WGS 84) for all geometry at rest |
| Area computation | Geodesic area on the WGS 84 ellipsoid |
| Distance computation | Geodesic |
| Rationale | Avoids UTM zone-boundary discontinuities; India spans zones 42N–46N and district-level analysis crosses them |

Record the area method in the dossier. An officer-facing figure of "96 m²" must be reproducible from the stated method.

### 13.3 Geocode-to-cluster join

Join semantics are conditioned on geocode confidence. This is the mechanism that implements the hard gate in P3.

| Geocode tier | Join rule | Tolerance `τ` | Result status |
|---|---|---|---|
| Rooftop | point-in-polygon against dissolved cluster | 0 m | `matched` |
| Building centroid | point-in-polygon, else nearest cluster | 10 m `[CALIBRATE]` | `matched` |
| Street | nearest cluster within `τ` | 30 m `[CALIBRATE]` | `candidate` |
| Locality centroid | no join attempted | — | `unresolved` |
| Unresolved | no join attempted | — | `unresolved` |

Additional rules:

- **`candidate` status cannot support an adverse finding.** It may contribute to case prioritisation for field verification only.
- **Ambiguous joins are not resolved arbitrarily.** If two clusters lie within `τ` and their distances differ by less than 20% `[CALIBRATE]`, mark `ambiguous` and treat as `unresolved`. Deterministic tie-breaking by identifier is forbidden — it manufactures false precision.
- **No containing cluster and no cluster within `τ`** yields `no_structure`, which is a positive D3 signal *only* at rooftop or building-centroid confidence.

### 13.4 Multi-storey capacity

Footprint area understates capacity in multi-storey premises. Open data does not reliably supply floor count in Indian contexts.

> **Rule 13.4.** Where floor count is unknown, apply a conservative floor-count bound `n_floors = 3` `[CALIBRATE]` when computing **D2b physical capacity**, so the system errs toward *understating* implausibility. Record that the bound was applied. Never assume single-storey.

This deliberately weakens the detector. That is the correct trade: a false negative costs revenue, a false positive costs a legitimate business.

**The bound does not apply to D2a.** D2a is a ratio against a benchmark computed over the same population with the same convention, so a uniformly applied multiplier cancels and changes nothing. D2a uses `area_m2` directly. Applying the bound in D2a would create a false impression of conservatism while having no effect — worse than not applying it, because it obscures where the real conservatism lives.

---

## 14. Throughput Attribution

The largest specification gap in Draft 1. D2a and D3 both aggregate declared throughput onto premises, and the aggregation is meaningless without a stated attribution rule.

### 14.1 The problem

An entity may hold one principal place of business and several additional places. Declared outward value for a period is a single figure at entity level. Attributing it to premises is a choice, and different choices invert results.

### 14.2 Attribution invariant

> **Invariant.** For every entity and period, the sum of value attributed across all its premises equals total declared outward value for that entity and period. Every rupee is attributed to exactly one premises. No duplication.

Violating this is the single most likely cause of spurious high-density findings, because duplicating an entity's full turnover onto each of four premises inflates aggregate density fourfold at each.

### 14.3 Attribution methods, in precedence order

| Rank | Method | Basis | When used | Confidence |
|---|---|---|---|---|
| 1 | Movement-derived | Dispatch-origin address on movement records | Movement records present for the period | High |
| 2 | Even split | Equal division across goods-capable premises | Movement records absent | Low |
| 3 | Principal-only | All value to principal place of business | Single registered premises only | High |
| — | Duplicate-to-all | — | **Forbidden** | — |
| — | Area-proportional | Split by observed footprint area | **Forbidden** | — |

Method 1 is preferred because the taxpayer has themselves declared which premises goods departed from. The system is then testing a declaration against physical reality rather than imposing an assumption.

Area-proportional attribution is forbidden as **circular**: it distributes throughput using the very quantity the detector tests against.

### 14.4 Confidence propagation

Attribution confidence propagates to detector output. Method 2 (even split) yields `low` attribution confidence, and:

> **Rule 14.4.** A D2a adverse finding requires attribution confidence `high`. Even-split attribution supports prioritisation only.

This is restrictive by design. It means D2a acts primarily where movement records exist — which is also where the declared throughput is most concrete.

### 14.5 Unattributable cases

Certain legitimate arrangements have no meaningful premises attribution. These are exempted from D2a and D3 by construction, not by threshold:

| Arrangement | Reason | Detection |
|---|---|---|
| Job-work | Goods processed at a third party's premises | Declared role from P1 |
| Pure trading, no warehousing | Goods never rest at registered premises | Declared role from P1 |
| Bill-to / ship-to with third-party dispatch | Dispatch origin is not the entity's premises | Movement record origin ≠ any registered premises |
| Merchant export | Goods move supplier → port directly | Movement record pattern |

Each of these maps to a hard negative in Section 11.2. A system that flags any of them is not ready for use.

---

## 15. Data Dictionary

Normative schema. Types are logical, not bound to any storage engine. `PK` = primary key, `FK` = foreign key. Nullability is significant: nullable fields must have defined handling in every detector that reads them.

### 15.1 `registration`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `gstin` | char(15) | no | PK. Checksum-valid format |
| `legal_name` | text | no | |
| `pan` | char(10) | no | Derivable from GSTIN positions 3–12; store for cluster joins |
| `constitution` | enum | no | proprietorship, partnership, LLP, private_ltd, public_ltd, HUF, trust, other |
| `registration_date` | date | no | |
| `status` | enum | no | active, suspended, cancelled, provisional |
| `cancellation_date` | date | yes | Non-null iff status = cancelled |
| `declared_role` | enum | yes | manufacturer, trader, warehouse, job_worker, service, mixed. Derived in P1 |
| `declared_hsn` | array\<char(8)\> | no | Min cardinality 1 |
| `authorised_signatory_id` | text | yes | Hashed identity token, not raw PII |
| `bank_account_hash` | array\<text\> | yes | Hashed. Used for D4 shared-identifier clustering |
| `contact_hash` | array\<text\> | yes | Hashed mobile and email |

### 15.2 `premises`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `premises_id` | uuid | no | PK |
| `gstin` | char(15) | no | FK → `registration` |
| `premises_type` | enum | no | principal, additional |
| `address_raw` | text | no | As declared |
| `geom` | point (EPSG:4326) | yes | Null when unresolved |
| `geocode_tier` | enum | no | rooftop, building_centroid, street, locality_centroid, unresolved |
| `geocode_source` | text | no | Provenance: gstn_geocode, nominatim_selfhost, etc. |
| `cluster_id` | uuid | yes | FK → `premises_cluster`. Null when join status ≠ matched |
| `join_status` | enum | no | matched, candidate, ambiguous, unresolved, no_structure |
| `goods_capable` | boolean | no | Whether this premises can receive throughput attribution (Section 14) |

An entity with zero rows having `goods_capable = true` is exempt from D2a and D3.

### 15.3 `premises_cluster`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `cluster_id` | uuid | no | PK |
| `geom` | multipolygon (EPSG:4326) | no | Dissolved per Rule 13.1 |
| `area_m2` | double | no | Geodesic, > 0 |
| `polygon_count` | integer | no | Number of source polygons dissolved. High values warrant review |
| `n_floors_bound` | integer | no | Default 3 per Rule 13.4 |
| `landcover_class` | enum | yes | ESA WorldCover class at centroid |
| `access_road_class` | text | yes | OSM highway tag of nearest routable way |
| `access_road_width_m` | double | yes | Where tagged; frequently null in India |
| `district_code` | text | no | Stratification key |
| `source_dataset_version` | text | no | Provenance. Required for reproducibility |

### 15.4 `invoice_line`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `line_id` | uuid | no | PK |
| `supplier_gstin` | char(15) | no | FK → `registration` |
| `recipient_gstin` | char(15) | yes | Null for B2C |
| `document_date` | date | no | |
| `hsn` | char(8) | no | |
| `quantity` | decimal | yes | Null permitted; blocks D1 and D2 for this line |
| `uqc` | enum | yes | Non-null iff quantity non-null |
| `quantity_kg` | decimal | yes | **Derived** in P5. Null when normalisation impossible |
| `uqc_conversion_status` | enum | no | exact, estimated, failed. Audit-critical |
| `taxable_value` | decimal | no | ≥ 0 |
| `tax_amount` | decimal | no | ≥ 0 |
| `place_of_supply` | text | no | |
| `supply_type` | enum | no | domestic, export, sez_supply, deemed_export |

`uqc_conversion_status` exists because unit-of-measure normalisation is the dominant error source for both D1 and D2. A line with status `estimated` must not produce a strong finding alone.

### 15.5 `movement_record`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `movement_id` | uuid | no | PK |
| `line_id` | uuid | yes | FK → `invoice_line` |
| `origin_premises_id` | uuid | yes | FK → `premises`. **Basis for Rank-1 attribution** |
| `origin_address_raw` | text | no | |
| `destination_address_raw` | text | no | |
| `distance_km` | double | yes | |
| `vehicle_id_hash` | text | yes | Hashed |
| `declared_gross_weight_kg` | decimal | yes | |
| `generated_at` | timestamp | no | |

### 15.6 `return_summary`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `gstin` | char(15) | no | PK part 1, FK → `registration` |
| `period` | char(7) | no | PK part 2, `YYYY-MM` |
| `outward_value` | decimal | no | ≥ 0 |
| `itc_availed` | decimal | no | ≥ 0 |
| `tax_paid_cash` | decimal | no | ≥ 0 |
| `closing_credit_balance` | decimal | no | ≥ 0 |
| `filing_status` | enum | no | filed, late, not_filed |

`cash_to_itc_ratio = tax_paid_cash / (tax_paid_cash + itc_availed)`, defined as null when the denominator is zero. D4 must handle the null case explicitly rather than treating it as zero.

### 15.7 `refund_claim`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `claim_id` | uuid | no | PK |
| `gstin` | char(15) | no | FK → `registration` |
| `period_from` | date | no | |
| `period_to` | date | no | `≥ period_from` |
| `route` | enum | no | zero_rated_export, sez_supply, inverted_duty, other |
| `amount_claimed` | decimal | no | > 0 |

### 15.8 `attribution`

Materialised output of Section 14. Exists as a table because the invariant in 14.2 must be checkable.

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `gstin` | char(15) | no | PK part 1 |
| `period` | char(7) | no | PK part 2 |
| `premises_id` | uuid | no | PK part 3 |
| `attributed_value` | decimal | no | ≥ 0 |
| `attributed_mass_kg` | decimal | yes | Null when UQC normalisation failed |
| `method` | enum | no | movement_derived, even_split, principal_only |
| `confidence` | enum | no | high, low |

Invariant check: for each `(gstin, period)`, `SUM(attributed_value)` equals `return_summary.outward_value`.

### 15.9 `finding`

| Field | Type | Null | Constraint / note |
|---|---|---|---|
| `finding_id` | uuid | no | PK |
| `claim_id` | uuid | no | FK → `refund_claim` |
| `detector` | enum | no | D1, D2a, D2b, D3, D4 |
| `score` | double | no | `[0, 1]` |
| `confidence` | double | no | `[0, 1]` |
| `finding_text` | text | no | Human-readable, officer-facing |
| `evidence_refs` | array\<text\> | no | Min cardinality 1. Pointers to source records and dataset versions |
| `blocked_reason` | enum | yes | Non-null when the finding was suppressed: low_geocode_confidence, role_gate, unsourced_parameter, low_attribution_confidence, ambiguous_join |

A suppressed finding is **recorded, not discarded**. The dossier must be able to show what the system considered and declined to act on. This matters for both audit and contestation.

---

## 16. Calibration Procedure

Draft 1 deferred every threshold to `[CALIBRATE]` without saying how calibration happens. That made the specification unbuildable past P6. This section resolves it.

### 16.1 The constraint

There are no labels. No public dataset of confirmed fraudulent GSTINs with matched premises exists, and there will not be one. Supervised threshold selection is unavailable at the outset.

### 16.2 Four-stage maturity model

Every threshold carries a stage marker. The stage determines what the threshold may be used for.

| Stage | Method | Permitted use |
|---|---|---|
| S1 | Capacity-anchored percentile | Ranking and prioritisation only |
| S2 | Synthetic-corpus validation | Ranking; internal accuracy reporting with caveats |
| S3 | Expert elicitation on borderline cases | Amber tier |
| S4 | Field-outcome supervised calibration | Red tier and adverse action |

> **Rule 16.2.** No threshold below S4 may support an adverse finding in production. S1–S3 thresholds support case prioritisation. This is the honest position: the system can tell an officer where to look long before it can tell them what to conclude.

### 16.3 Stage 1 — capacity anchoring

Do not pick thresholds to hit an accuracy target. Pick them so the flagged volume matches the number of cases the verification workforce can actually process.

```
Given verification capacity of k cases per period:
  threshold = the score at the (1 − k/N) percentile of the scored population
```

This inverts the usual framing and is the correct one operationally. Officers work a queue, not a threshold. It also makes the system's cost explicit from day one.

### 16.4 Stage-1 anchor values

**These are starting points, not empirical findings.** They exist so an implementation can run end to end. Every one is expected to move.

| Parameter | Anchor | Notes |
|---|---|---|
| P0 full-pipeline trigger | claims above ₹1 crore | Below: D1 + D4 only, for cost control |
| Upstream traversal depth `k` | 3 | Beyond 3, edge count grows faster than signal |
| D1 robust log z — flag | 3.5 | |
| D1 robust log z — strong | 5.0 | |
| D1 minimum HSN sample | 200 lines | Below: fall back to HS-4 with confidence penalty |
| D2a robust log z — flag | 3.0 | |
| D2a robust log z — strong | 4.5 | |
| D3 entity density | > 1 goods-supplying GSTIN per 50 m² of cluster area | |
| D3 structure absence radius | 50 m | Rooftop or building-centroid confidence only |
| D4 tax-origin depth | 0 or 1 with `cash_to_itc_ratio` < 0.02 | |
| D4 velocity | outward value per day since registration above the 99th percentile of the district × sector stratum | |
| Cluster dissolve buffer `b` | 5 m | Section 13.1 |
| Join tolerance — building centroid | 10 m | Section 13.3 |
| Join tolerance — street | 30 m | Section 13.3 |
| Ambiguity margin | 20% | Section 13.3 |
| `n_floors` bound | 3 | Section 13.4 |
| Assumed fraud prevalence for sweeps | 2% | Vary across 0.5–5% |

### 16.5 Stage 2 — synthetic validation protocol

1. Generate the background population **independently** of fraud injection.
2. Inject positives P1–P5 at the assumed prevalence.
3. Inject hard negatives N1–N6 at a rate high enough for meaningful per-class FPR.
4. Score with S1 anchors.
5. Report recall per positive pattern, FPR per negative class, and stratified FPR.
6. Sweep prevalence across the range in 16.4 and report threshold sensitivity.
7. Adjust anchors only where a hard-negative class fails. **Do not tune to maximise recall on injected positives** — the injection is your own construction and tuning against it is self-congratulation.

Step 7 is the discipline that keeps Stage 2 honest.

### 16.6 Stage 3 — expert elicitation

Sample cases from the score band immediately around each threshold. Present the dossier without the score. Record the expert's judgment and reasoning. Use agreement rate as a threshold-quality signal, and disagreement cases as the highest-value discussion material.

Elicitation on cases far from the threshold wastes expert time — those are easy in both directions.

### 16.7 Stage 4 — field feedback

Verification outcomes from P8 provide the first genuine labels. Requirements before promoting any threshold to S4:

- Minimum outcome count per stratum `[CALIBRATE]`, sufficient for a stable estimate.
- Outcomes recorded for **both** flagged and a random sample of unflagged cases. Without the random arm, recall cannot be estimated and the feedback loop only reinforces existing selection bias.

The random control arm is the part most easily dropped and the part that makes the whole loop valid.

---

## 17. Worked Example

A single synthetic case traced from trigger to decision, with every intermediate value shown. Purpose is disambiguation: where prose and this example disagree, the example is authoritative and the prose is defective.

All figures are synthetic.

### 17.1 P0 — Trigger

| Field | Value |
|---|---|
| `claim_id` | `RC-0001` |
| `gstin` | `EXP-0001` (merchant exporter) |
| Period | 2025-04 to 2025-06 |
| Route | `zero_rated_export` |
| `amount_claimed` | ₹42.0 crore |

₹42 crore exceeds the ₹1 crore anchor → full pipeline.

### 17.2 P1 — Role gate

`EXP-0001` declares `trader`, no warehousing. **D2a and D3 are not applicable to the claimant itself** — a merchant exporter legitimately has no manufacturing premises. Findings for `EXP-0001` on those detectors are recorded with `blocked_reason = role_gate`.

The pipeline proceeds upstream. This is the normal case: the claimant is the beneficiary, the suppliers are where physical implausibility lives.

### 17.3 P2 — Network assembly

Traversal to depth 3 yields 18 direct suppliers, all declaring `manufacturer`.

### 17.4 P3 — Site resolution

| Geocode tier | Count | Join status | Eligible for adverse finding |
|---|---|---|---|
| Rooftop | 7 | `matched` | yes |
| Building centroid | 4 | `matched` | yes |
| Street | 3 | `candidate` | no — prioritisation only |
| Locality centroid / unresolved | 4 | `unresolved` | no — routed to field verification |

All 11 `matched` premises join to **one** cluster: `PC-4471`.

### 17.5 P4 — Physical envelope

| Field | Value |
|---|---|
| `polygon_count` | 2 (dissolved at `b` = 5 m) |
| `area_m2` | 96.0 (geodesic, WGS 84) |
| `landcover_class` | built-up |
| `access_road_class` | `highway=residential` |
| `access_road_width_m` | null (untagged) |
| `n_floors_bound` | 3 |

### 17.6 P5 — Attribution

Movement records exist for the period and their `origin_premises_id` values resolve. Attribution method = `movement_derived`, confidence = `high`, satisfying Rule 14.4.

Aggregate attributed outward value to `PC-4471` across the 11 entities for the quarter: **₹380.0 crore**.

Invariant check passes: for each of the 11 entities, attributed value across its premises equals its `outward_value`.

### 17.7 P6 — Detector evaluation

**D2a — throughput density.** Note the denominator is `area_m2`, not floor-bounded area: the `n_floors` bound is applied uniformly across the benchmark population, so it cancels in the ratio. The bound matters for D2b only.

```
density          = 380.0 / 96.0        = 3.958  ₹cr per m² per quarter
stratum median   = 0.005               (district × sector)
stratum log disp = 0.62                (1.4826 × MAD of ln density)

ln(3.958 / 0.005) = ln(791.7)          = 6.674
z                 = 6.674 / 0.62       = 10.76
```

Against the strong threshold of 4.5 → **strong flag**. Reported to the officer as *"approximately 790× the district-and-sector median declared value per square metre."* The multiple communicates; the z-score does not.

**D3 — aggregation.**

```
entity density = 11 / 96 m²  = 1 per 8.7 m²   (threshold: 1 per 50 m²)
```

Flag. Land cover is built-up but consistent with residential rather than industrial use. Access is a residential lane with no truck-capable width tagged.

**D1 — price closure.** Two HSNs carry declared export unit values at 28× and 31× the median Indian export unit value for their HS-6 codes. With stratum log dispersion 0.45, `z` = 7.4 and 7.6 → both exceed the strong threshold of 5.0.

**D2b — physical capacity.** `blocked_reason = unsourced_parameter`. Bulk density for the relevant sector is not yet sourced to a citable standard, so no physical-capacity finding is emitted. Recorded, not silently skipped.

**D4 — network.**

| Feature | Value | Threshold | Result |
|---|---|---|---|
| Registration age at first invoice | all 11 under 90 days | — | flag |
| `cash_to_itc_ratio` | 0.004 | < 0.02 | flag |
| Upstream tax-origin depth | 0 for all 11 | 0 or 1 | flag |
| Shared `bank_account_hash` | 3 values across 11 entities | — | cluster |
| Velocity percentile | above 99th | 99th | flag |

### 17.8 Fusion and tier

Corroboration rule 8.2.1 requires a physical detector to be supported by D1 or D4. D3 is supported by **both**. Geocode confidence is satisfied for the 11 contributing entities. The role gate permits physical detectors for entities declaring `manufacturer`.

**Tier: Red + cluster.**

Suppressed findings carried into the dossier:

| Subject | Detector | `blocked_reason` |
|---|---|---|
| `EXP-0001` | D2a, D3 | `role_gate` |
| 3 street-tier suppliers | D3 | `low_geocode_confidence` |
| 4 unresolved suppliers | D2a, D3 | `low_geocode_confidence` |
| all 11 | D2b | `unsourced_parameter` |

### 17.9 Action

Refund held pending physical verification of `PC-4471`. Drafted reasoning cites: the cluster identifier and geodesic area; the 11 registrations resolving to it; aggregate attributed declared value; the two price multiples with their HSN benchmarks; the three shared bank account hashes; and dataset versions for every geospatial input.

The dossier states plainly that the 4 unresolved addresses **did not contribute** to the adverse finding. Recording what the system declined to rely on is what makes the finding defensible.

### 17.10 Counterfactual — the case that should clear

Same 11 entities, same ₹380 crore, but registered to a genuine 12,000 m² industrial cluster:

```
density = 380.0 / 12,000 = 0.0317
ln(0.0317 / 0.005) = ln(6.33) = 1.845
z = 1.845 / 0.62 = 2.98        → below the D2a flag threshold of 3.0
```

D2a clears. If D1 were also clean, no adverse tier results despite 11 co-located registrations — because co-location in adequate premises is a normal industrial estate, which is hard negative N5.

A design that cannot articulate what clears it is a rubber stamp. This subsection is the test.

---

## 18. System Invariants

Properties that must hold for every input. Stated here as specification; they are intended to become executable property-based tests during implementation, with generated inputs rather than fixed cases.

| ID | Invariant | Rationale |
|---|---|---|
| I1 | For every `(gstin, period)`, the sum of `attributed_value` across premises equals `return_summary.outward_value` | Prevents the duplication error that inflates density (Section 14.2) |
| I2 | No `finding` with `score` above an adverse threshold exists where the contributing premises has `geocode_tier` of `street`, `locality_centroid`, or `unresolved` | The primary false-accusation control |
| I3 | No adverse tier is assigned where the only above-threshold detectors are D2a, D2b, or D3 | Corroboration requirement |
| I4 | For entities whose `declared_role` implies no physical premises, no D2a or D2b or D3 finding is emitted without `blocked_reason = role_gate` | Protects traders, job-workers, service providers |
| I5 | Dissolving an already-dissolved cluster set produces an identical set | Idempotence; guards against area drift across re-runs |
| I6 | Holding attributed throughput constant, increasing `area_m2` cannot increase the D2a score | Monotonicity; a larger premises can never be more suspicious |
| I7 | Identical inputs and identical dataset versions produce identical outputs, including dossier text | Determinism; required for contestation and audit |
| I8 | Every numeric value in a dossier resolves to at least one entry in `evidence_refs` with a recorded dataset version | Provenance completeness |
| I9 | If any D2b parameter for the relevant sector is unsourced, no D2b finding is emitted for that sector | Prevents invented constants supporting adverse action |
| I10 | Suppressed findings are persisted with a non-null `blocked_reason`, never deleted | Audit trail of what was considered and declined |
| I11 | `SUM(attributed_value)` for a cluster never exceeds the sum of `outward_value` for entities joined to it | No cross-entity double counting |
| I12 | A finding referencing a `premises_cluster` never references a cluster whose `source_dataset_version` differs from the version recorded on the case | Prevents mixing footprint releases within one case |

I6 deserves emphasis. It is the formal statement that the system rewards having larger premises, which is the correct direction and worth being able to prove.

---

## 19. Build Phasing and Scale

### 19.1 Phase order

Phases are ordered by dependency and by evidence value per unit of effort. The order deliberately front-loads the detectors that need no earth-observation data, because they carry the flagship fraud mode.

| Phase | Deliverable | Depends on | Blocked by |
|---|---|---|---|
| 0 | Data model (Section 15) + synthetic corpus generator with positives P1–P5 and hard negatives N1–N6 | — | — |
| 1 | D1 + D4 + dossier skeleton + invariants I1, I7, I8 | 0 | — |
| 2 | Footprint ingest, cluster dissolve, geocoding, spatial join, D3 + invariants I2, I5, I12 | 0, 1 | — |
| 3 | Attribution engine (Section 14) + D2a + benchmark strata + invariants I6, I11 | 2 | — |
| 4 | Fusion, decision tiers, corroboration rules, drafted statutory reasoning + invariants I3, I4, I10 | 1, 2, 3 | — |
| 5 | D2b physical capacity model + invariant I9 | 3 | Open question 1 (parameter sourcing) |
| 6 | Evaluation harness, ablation matrix, stratified fairness audit, systematic prior-art search | 0, 4 | — |
| 7 | Optional imagery layer: Sentinel-1/2 change detection, conditional thermal | 2 | — |

### 19.2 MVP cut

**Phases 0, 1, 2, and 4 (partial).**

This delivers price closure plus premises aggregation, fused with drafted reasoning — the combination that catches the canonical over-invoicing-plus-ghost-supplier case. It defers both capacity detectors.

Deferring D2a to Phase 3 is a deliberate choice rather than a concession: D2a needs benchmark strata, and benchmark strata built on a thin synthetic corpus are the weakest part of the evaluation (Section 5, D2a circularity). D3 does not need strata and carries most of the same evidentiary weight.

**Do not attempt Phase 7 in an MVP.** Imagery processing consumes disproportionate time for marginal evidentiary gain over footprint vectors, and Section 4.3 already bounds what 10 m optical can contribute.

### 19.3 Critical path warning

Phase 0 is the whole project's dependency root, and the hard negatives are the part most likely to be skipped under time pressure. N1 through N4 each individually defeat a naive detector. A build that reaches Phase 4 without them will report excellent synthetic accuracy and be unfit for use.

### 19.4 Scale

Figures below are order-of-magnitude expectations to be measured at ingest, not verified counts. `[VERIFY]`

| Quantity | Expected order | Implication |
|---|---|---|
| Overture building polygons, India | 10⁸ | National load is not viable on commodity hardware |
| Polygons per district | 10⁵–10⁶ | District-scoped processing is tractable |
| Dissolved clusters per district | 10⁵ | Precompute once per dataset release, cache |
| Case-scoped invoice edges at depth 3 | 10³–10⁴ | Graph work stays in memory; no distributed engine needed |
| Premises per case | 10¹–10² | Spatial joins are trivially small at case scope |

**Strategy.** Never load nationally. Filter footprints by district bounding box for the active case set, using GeoParquet predicate pushdown and a spatial index over H3 or S2 cells. Precompute and cache the cluster dissolve per district per dataset release, keyed by `source_dataset_version` so I12 is enforceable.

The insight that keeps this tractable: **the geospatial workload is national, but the analytical workload is case-scoped.** Only the footprint layer is large, it is static per release, and it can be preprocessed once. The graph and detector work operates on a few thousand records per case.

### 19.5 Reproducibility requirements

Because I7 requires determinism and P8 requires contestability:

- Pin every dataset version; record it on the case, not globally.
- Treat the HSN Signature Map, Capacity Parameter Table, and threshold set as versioned artefacts under change control, not configuration.
- Record the threshold maturity stage (Section 16.2) alongside every finding, so a case decided under S1 thresholds is distinguishable later from one decided under S4.

---

## 20. Open Questions

Resolve these before or during implementation. Each is genuinely open, not rhetorical.

1. **Capacity parameters.** Which citable standard supplies bulk density, stacking height, and floor utilisation per sector? Until answered, D2b cannot support adverse findings.
2. **Footprint coverage quality in India.** What is Overture's completeness and area accuracy for small rural and peri-urban structures? D2a and D3 degrade with footprint recall, and this needs measuring, not assuming.
3. **Floor count.** Partly addressed by Rule 13.4, which applies a conservative bound of 3 for D2b. Still open: is height estimation from open data (SAR-derived height, shadow length, open DSM products) accurate enough to replace the bound, and does that accuracy hold for small Indian structures?
4. **Price benchmark for domestic supply.** Trade statistics cover exports. What open source establishes domestic unit-price distributions per HSN?
5. **Geocode accuracy in India.** What rooftop-match rate is achievable with open geocoding on real GST address strings? This bounds the fraction of cases the system can act on at all.
6. **Threshold calibration without labels.** Addressed by Section 16's four-stage maturity model. Remaining open items: the minimum field-outcome count per stratum for S4 promotion, and whether a random control arm is obtainable in practice — without it, recall cannot be estimated and the feedback loop reinforces selection bias.
7. **Legal admissibility of remote-sensing evidence** in GST adjudication and appellate proceedings. Requires practitioner input.
8. **Adversarial adaptation.** Once footprint reconciliation is known, syndicates can register against large genuine industrial footprints. What is the response — and does it collapse back to D1 and D4?
9. **Systematic prior-art search.** The novelty claim in 4.6 rests on a preliminary search only. A proper search must cover academic databases, patent filings, revenue authority technical publications, and OECD / IMF tax administration working papers. Tracked as Phase 6.
10. **Attribution when movement records are absent.** Rule 14.4 restricts D2a to high-confidence attribution, which means D2a is inactive wherever movement records are missing. What fraction of real cases does that exclude, and is there a defensible middle path between movement-derived and even-split?

Question 8 deserves emphasis. Any deployed detector changes fraudster behaviour. A design that has no answer for its own evasion is incomplete. Note that the adaptation it describes — registering against large genuine footprints — is *already* the counterfactual in Section 17.10 that the system correctly clears. The detector's failure mode and its fairness control are the same mechanism, which means D2a and D3 are inherently evadable by a well-resourced syndicate and cannot be the system's only line.

---

## 21. References

**Statutory and administrative**
- [Notification 04/2024-Central Tax — special procedure, pan masala and tobacco, Form SRM-I](https://www.gstcouncil.gov.in/sites/default/files/2024-05/04-2024-ct-eng.pdf)
- [CBIC Instruction 03/2025-GST — processing of registration applications](https://cbic-gst.gov.in/pdf/ins-gst-no-03-2025.pdf)
- [CBIC Circular 131/1/2020-GST — verification of risky exporters](https://cbic-gst.gov.in/pdf/Circular-131-1-2020-GST-Exporter.pdf)
- [Rule 86A, CGST Rules — overview of conditions and judicial position](https://cleartax.in/s/all-about-cgst-rule-86a-itc)
- [Reporting on proposed geotagging for GST registration verification](http://economictimes.indiatimes.com/news/economy/policy/geotagging-may-become-must-for-gst-registrations/articleshow/101438613.cms)
- [Reporting on DGARM supply-chain analysis and refund suspension](https://economictimes.indiatimes.com/news/economy/gst-analytics-wing-to-identify-risky-suppliers-to-exporters/articleshow/75865928.cms)
- [E-way bill integration with VAHAN](https://www.vjmglobal.com/blog/integration-of-e-way-bill-portal-with-vahan-portal)

**Remote sensing — capability and limits**
- [TROPOMI spatial resolution and detection limits, Copernicus AMT 2025](https://amt.copernicus.org/articles/18/4373/2025/index.html)
- [Sentinel-5P NO₂ retrieval v2.2 assessment, AMT 2022](https://amt.copernicus.org/articles/15/2037/2022/amt-15-2037-2022-metrics.html)
- [Thermal infrared monitoring of iron and steel production status, MDPI 2023](https://www.mdpi.com/2071-1050/15/11/8575)
- [TransitionZero — satellite estimation of steel facility utilisation](https://www.transitionzero.org/insights/steel-data-explainer)
- [Factory extraction from satellite imagery, Remote Sensing 2022](https://mdpi.com/2072-4292/14/22/5657)
- [Estimating industrial development from high-resolution panchromatic imagery, arXiv](https://arxiv.org/html/2301.09620v3)

**Prior art — tax and fraud analytics**
- [Machine learning to identify non-existent firms in Indian tax data, ACM JCSS 2024](https://dl.acm.org/doi/10.1145/3676188)
- [Geospatial analytics for detecting tax evasion, Johns Hopkins 2024](https://jscholarship.library.jhu.edu/items/1f4f8874-de6f-4211-85ed-8822d8e067a3)
- [Satellite and AI detection of unregistered properties for taxation](https://ongeo-intelligence.com/blog/hidden-buildings-lost-taxes-how-satellite-imagery-and-ai-help-detect-unregistered-properties)
- [Capacity taxation — the Pakistan experiment](https://link.springer.com/article/10.2307/3866694)

**Data sources and licences**
- [Overture Maps buildings theme](https://docs.overturemaps.org/guides/buildings/) · [licence](https://docs.overturemaps.org/blog/2024-01-17-alpha.0/)
- [ESA WorldCover data access](https://esa-worldcover.org/en/data-access) · [AWS Open Data registry](https://registry.opendata.aws/esa-worldcover-vito/)
- [Copernicus Data Space Ecosystem terms](https://dataspace.copernicus.eu/terms-and-conditions)
- [Nominatim source](https://github.com/osm-search/Nominatim) · [usage policy](https://operations.osmfoundation.org/policies/nominatim/)
- [Government Open Data Licence — India](https://data.gov.in/sites/default/files/NDSAP_OpenDataLicense.pdf)
- [UN Comtrade](https://comtradeplus.un.org/TradeFlow)

*Reference summaries above are paraphrased from the linked sources. Content was rephrased for compliance with licensing restrictions.*

---

## 22. Glossary

| Term | Meaning |
|---|---|
| ITC | Input Tax Credit — credit for tax paid on inputs, offsettable against output liability |
| GSTIN | GST Identification Number, per-registration identifier |
| HSN | Harmonised System of Nomenclature — commodity classification code |
| UQC | Unit Quantity Code — declared unit of measure |
| Zero-rated supply | Supply taxed at nil rate with input credit preserved, enabling cash refund of accumulated credit |
| Footprint | Building outline polygon derived from earth observation |
| Throughput density | Declared value per square metre of registered premises per period |
| Hard negative | Legitimate case constructed to defeat a naive detector |
| Premises cluster | Dissolved union of footprint polygons within buffer `b`; the unit of analysis for D2a and D3 (Rule 13.1) |
| Attribution | Assignment of an entity's declared throughput to specific premises (Section 14) |
| Attribution invariant | Every rupee of declared value attributes to exactly one premises; no duplication (Section 14.2) |
| Join status | Outcome of geocode-to-cluster matching: `matched`, `candidate`, `ambiguous`, `unresolved`, `no_structure` |
| Suppressed finding | A detector result recorded with a `blocked_reason` rather than acted on; retained for audit |
| S1–S4 | Threshold maturity stages; only S4 may support adverse action (Section 16.2) |
| Capacity anchoring | Setting thresholds so flagged volume matches verification workforce capacity (Section 16.3) |
| `[CALIBRATE]` | Parameter requiring empirical sourcing before adverse use |
| `[VERIFY]` | Claim requiring confirmation at implementation time |
