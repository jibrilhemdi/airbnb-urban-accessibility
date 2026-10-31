# Canonical manuscript and cartographic water — 31 October 2026

All accepted prose remains in `thesis_report/main.tex`. All unique literature,
data, governance and Methods entries are now in `thesis_report/references.bib`.
The 16 repeated literature keys were reconciled by preserving their first
active definition, matching the earlier Biber resolution. No unique entry from
the three working bibliographies was dropped. The two auxiliary bibliographies
were removed after merging. Historical source-check notes retain their original
filenames and claims about the files as they existed on their dates.

`.latexmkrc` selects XeLaTeX, keeps auxiliaries under `build/`, and produces
only `thesis_report/main.pdf`. The retired `data_and_methods.pdf`,
`study_areas_and_data.pdf` and stale `build/main.pdf` are preserved in the local
checksum archive, alongside the pre-edit manuscript/bibliographies/map/scripts.
Original supplied template files and completed scientific artifacts are intact.

## Figure 4.1 diagnosis and correction

The previous renderer filled complete administrative study polygons. It had
no separate hydrographic layer, so water included within administrative areas
received the city's land colour. This made Oslofjord and Stockholm's waterways
hard to recognise. The accepted analytical masks and operational neighbourhoods
remain exactly as selected; the correction changes display only.

[Kartverket's boundary documentation](https://www.kartverket.no/api-og-data/grensedata)
confirms that municipal boundaries can include maritime areas. A boundary polygon
is therefore not a substitute for a shoreline. The three panels now overlay sea,
transitional waters, lakes and wide rivers from the official
[EU-Hydro River Network Database](https://land.copernicus.eu/en/products/eu-hydro/eu-hydro-river-network-database).
The source's 2006–2012 reference period is disclosed in the caption and image;
this is contextual hydrography, not a claim of contemporaneous 2026 coastlines.
The [EEA catalogue](https://www.eea.europa.eu/en/datahub/datahubitem-view/2e782ca5-c7b2-4b48-8928-03031b642176)
gives the initial publication date as 19 November 2019. The live product page
identifies the release as V1 and reports a 1 ha minimum mapping unit, manual
interpretation at 1:30,000, and not-yet-validated status. It is suitable here
as map context, not as an additional analytical measurement.

Source: EEA's Copernicus ArcGIS service
`EUHydro/EU_Hydro_RiverNetworkDatabase/MapServer`, layers 0 (Coastal_polygon),
1 (Transit_polygon), 2 (InlandWater) and 19 (River_Net_polygon). Each city's
envelope comes from the unchanged frozen mask and panel extent, with a 0.01°
retrieval margin. The service is EPSG:3857; queries explicitly request
GeoJSON in EPSG:4326, seven decimal places and a 0.00002° generalisation
tolerance. Polygon clipping/union takes place in EPSG:4326. Rendering transforms
to EPSG:25832, EPSG:25833 and EPSG:3006 respectively. No invalid geometry is
silently repaired. A transfer-limit response stops acquisition.

`scripts/thesis_water_context.py --prepare` acquired write-once public responses,
layer metadata, product/policy pages and per-file SHA-256 receipts. It appended
three immutable rows to the isolated `cartography.manuscript_water` PostGIS
table using `sql/cartography/002_manuscript_water.sql`. The frozen selector
`config/reporting/manuscript_water.json` pins raw bytes, geometry records,
spatial extent/CRSs, acquisition times, licence and migration. Normal asset
generation checks these pins and reads PostGIS in a read-only transaction;
it does not reacquire data. No CSV is an alternative geometry authority.

The water polygons overlay city/context fill below the original group and mask
outlines. Civic points, map extents, scales and group counts are unchanged.
No listing positions appear in Figure 4.1. The other listing-based figures
retain their 500 m / at least five observations display rule.

The [Copernicus data policy](https://land.copernicus.eu/en/data-policy) permits
full, free and open access with source acknowledgement and an adaptation
statement. Both are included in the image; the main bibliography adds
`data_euhydro` with the dataset DOI. Product, policy, service and national
boundary documentation were checked on 31 October 2026.

No analytical mask, population area, selected source, sample, feature, fold,
scientific checkpoint, fitted artifact, saved prediction or completed result
export was changed. The original completed study-area image remains preserved
under its checksum-aware archive identity. Validation and the final approximate
length check are recorded in the execution log.
