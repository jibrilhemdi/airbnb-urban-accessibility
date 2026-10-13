# V4 housing access requirements — unsent requests

11 October 2026; Step 5 only. **No email/contact form/application was sent, no
account created, no terms accepted and no purchase authorized.** These drafts
are reviewable preparation, not provider approval or an access grant. Attempt
public, openly licensed historical exports before restricted research access.

## Exact requested deliverable

Calendar **2025-01-01 to 2025-12-31**, completed **apartment residential sales**,
one native statistical row per area and chosen nonoverlapping geographic level.
Preserve native DKK/NOK/SEK and price-per-square-metre values. Request:

- Native stable area ID/name, municipality code, geographic level, version and
  authoritative polygon source or complete official crosswalk.
- Apartment category/tenure definition, completed-trade inclusion/exclusion rules,
  floor-area denominator, statistic and unadjusted/adjusted-price definition.
- Annual price/m² and known annual sale count in the **same sample**; or quarterly
  price-ratio sums and matching denominators with correction/revision information
  sufficient to compute an annual arithmetic mean. Rounded/corrected published
  means plus differently filtered totals do not suffice. Never average medians.
- Missing/suppression indicators and minimum-count rules, retaining all native
  areas rather than silently deleting suppressed cells.
- Provenance, period, revision/release date, licence/academic research-use rights,
  attribution and specific publication/redistribution restrictions.

Preferred CSV (UTF-8, explicit delimiter/decimal convention):
`source_area_id,area_name,municipality_code,geography_level,period_start,period_end,
property_category,price_statistic,price_m2_native,currency,area_definition,
sale_count,suppression_flag,source_version`.
JSON-stat2/official XLSX is acceptable with a full dimension dictionary and
documented units. Geometry: GeoPackage/GeoJSON plus native CRS, native IDs,
validity/topology documentation, vintage and change history. Source geometry is
not automatically identical to the municipal study mask. Do not request or
publish transaction addresses, private individual records or owner information.

## Denmark — Finans Danmark, then official custom alternative

Primary contact route: [Boligmarkedsstatistik methodology](https://finansdanmark.dk/tal-og-data/boligstatistik/boligmarkedsstatistikken/datagrundlaget-for-statistikken/)
and provider contact on its official site. Candidate tables **BM011/BM021**;
study municipalities **0101 Copenhagen and 0147 Frederiksberg**, retaining both.
Do not guess contact addresses. [DST property-sales access](https://www.dst.dk/da/TilSalg/produkter/erhvervsliv-og-handel/ejendomssalg)
is an unresolved alternative if the open provider cannot supply suitable data;
commercial/research access needs approval before application or payment.

Unsent draft:

> I am preparing a university thesis comparing accessibility representations for
> Airbnb asking prices, conditional on external residential housing context.
> Could you identify a freely downloadable/reusable calendar-2025 apartment
> sale-price/m² dataset for native neighbourhood/postal groups covering both
> Copenhagen and Frederiksberg? We have preserved BM011/BM021 quarterly exports.
> Please confirm whether BM021 sale counts exactly match the filtered and revised
> BM011 price denominators, or provide annual means/counts or quarterly sums and
> exact denominators. Please also provide native area definitions/crosswalks,
> revision information and academic use/redistribution conditions. We seek
> aggregates only and are not requesting an account, purchase or contract here.

Geography dependency: both documented anonymous DAWA municipality-postcode
queries returned HTTP410. Identify the official replacement postcode geometry/
crosswalk, native grouping compatibility and 2025 vintage. No postcode-to-city
or housing-to-district mapping may be fabricated.

## Oslo — geographic clarification, no new boundary amendment here

Provider: Oslo Municipality, [Statistikkbanken](https://statistikkbanken.oslo.kommune.no/),
published contact **oslostatistikken@byr.oslo.kommune.no**. BOL018 annual2025
apartment means/counts are already acquired; do not request/retrieve them again
unnecessarily. SSB14545 municipal annual alternative is also preserved.

Unsent draft:

> We have acquired BOL018's revised calendar-2025 Blokkleilighet means/counts,
> using BRA/BRA-i, and the official geographic hierarchy. Please identify the
> source-matching 2025 polygons for grunnkretsområder/delbydeler, their native IDs,
> CRS, vintage and changes through June2026. Please clarify native table code
> 100000 and reaffirm the current BOL018 research-use/attribution conditions in
> relation to the government catalogue's NLOD2.0 platform entry. The separate
> municipal mask's reference vintage is unresolved; we are not asking to treat a
> present-day boundary as certified2025/2026 geometry. Please describe unavailable
> cell symbols, any suppression rules and price-count sample alignment.

A separately authorized municipal-boundary amendment must resolve the Step4
vintage issue before final dependent coverage qualification. This draft and
Step5 source acquisition do not approve that geography.

## Stockholm — open historical source first

First routes: [SCB statistics](https://www.scb.se/), Stockholm City's
[official statistics](https://start.stockholm/om-stockholms-stad/utredningar-statistik-och-fakta/statistik/)
and [SökHem open data](https://sokhem.se/sv/statistik/oppna-data).
SökHem's publicly listed contact is **support@sokhem.se**; no message sent.

Unsent open-source draft:

> Is there a freely downloadable/licensed historical calendar-2025 dataset of
> completed apartment/bostadsrätt price per m² and annual sale counts for multiple
> native areas within Stockholm municipality0180? Please supply the precise
> apartment scope, statistic, native area IDs/versions, missingness/count rules,
> polygons or official crosswalk and reuse licence. Your current rolling or
> municipality-wide summaries cannot meet our preceding-year neighbourhood
> measurement requirement. We do not want extrapolated prices, reconstructed
> medians or a city mean spread over polygons. An explicitly licensed historical
> area export would be preferred to restricted access.

If those fail, [Svensk Mäklarstatistik university access](https://www.maklarstatistik.se/om-statistiken/forskning/)
is the documented next option. Its public [download terms](https://www.maklarstatistik.se/wp-content/uploads/Svensk-Maklarstatistik-Allmanna-Villkor.pdf)
require separate review. No institutional eligibility, affiliation, fee, delivery,
redistribution permission or supervisor approval is invented.

Unsent research-access draft:

> Please explain university access requirements for annual2025 completed apartment
> sale-price/m² statistics and counts at identifiable Stockholm subareas within
> municipality0180. We require the exact native geography, polygons/crosswalk,
> apartment/tenure and transaction definitions, numerator/denominator/statistic,
> reference period, suppression and revision rules. Please specify affiliation
> evidence, application/contact procedure, any fee, licence/academic publication
> and redistribution terms before we seek authorization. We have not accepted
> your download terms and are not placing an order or requesting a contract.

The resolved SCB municipal mask does not imply price data exist at its 127
RegSO units. If a delivered source actually uses RegSO, independently verify
IDs, version, coverage and period; otherwise retain its native geography.

## Manual import specification and approval boundary

This is a **specification for a future authorized delivery**, not a claim that
an institutional importer or access grant exists. Do not use the anonymous
public downloader to access restricted files or fabricate credentials.

1. Obtain separate approval for any provider terms/application and confirm the
   actual delivery rights. Do not send the drafts automatically.
2. Preserve received bytes under a new ignored V4 housing source identity;
   never replace existing raw files/receipts. Record provider URL/contact route,
   acquisition date, delivery/reference period, geographic extent, licence and
   restrictions, format/schema, file SHA256 and local location. Do not include
   email bodies, credentials or restrictive agreements in public Git evidence.
3. Validate against the fields/units/categories above with explicit locale and
   missing/suppression conventions. Reject duplicate keys, impossible dates,
   nonpositive qualified prices and unverifiable geography/weights. Keep failed
   input intact with a truthful blocker report.
4. Add a source-specific parser/import extension to the existing housing adapter
   and synthetic/disposable tests in a separately requested recovery step;
   freeze a new policy/manifest and append a new housing audit ingestion. The
   currently implemented CLI supports the pinned anonymous sources, not an
   unverified institutional CSV schema.
5. Keep all deliveries/private rows ignored. Share only reviewed source hashes,
   aggregate audit and permitted metadata. Final reference-frame selection,
   spatial assignments and joined coverage await their authorized steps.
