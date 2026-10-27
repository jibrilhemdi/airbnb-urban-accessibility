-- Manuscript description only: original source rows before all sample filters.
-- Parameters identify the checksum-approved, immutable listing ingestion.
-- Missing means an absent/blank source field; zero and nonpositive prices are
-- not silently reclassified as missing. No outcome or bedroom is filled.
SELECT
    NULLIF(BTRIM(record #>> '{raw,room_type}'), '') AS room_type,
    NULLIF(BTRIM(record #>> '{raw,property_type}'), '') AS property_type,
    COUNT(*) AS n,
    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(record #>> '{raw,price}'), '') IS NULL
    ) AS missing_price,
    COUNT(*) FILTER (
        WHERE NULLIF(BTRIM(record #>> '{raw,bedrooms}'), '') IS NULL
    ) AS missing_bedrooms
FROM v4_raw.listing_audit
WHERE version = :version AND run_id = :run_id
  AND city = :city AND snapshot = :snapshot
GROUP BY 1, 2
ORDER BY 1 NULLS FIRST, 2 NULLS FIRST;
