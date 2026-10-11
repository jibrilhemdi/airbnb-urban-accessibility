-- V3-only cleanup. Historical schemas and applied migration bytes stay intact.
-- Provider coverage is source QA; official analysis_area controls validation.
ALTER TABLE v3_spatial.provider_neighbourhoods DROP COLUMN municipality_proxy;
ALTER TABLE v3_features.listing_spatial_base DROP COLUMN municipality_proxy;
ALTER TABLE v3_features.listing_spatial_base RENAME COLUMN cv_area_id TO provider_area_id;
ALTER INDEX v3_features.listing_spatial_base_cv_area_idx RENAME TO listing_spatial_base_provider_area_idx;
