"""Outcome-blind provider grouping and strict assignment, preserving source labels."""
from __future__ import annotations
from collections import Counter
import json

from pyproj import CRS, Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform, unary_union
from shapely.strtree import STRtree

from src.study.sources import verify_source
from src.study.specification import load_design


def metric_transform(crs):
    value = CRS.from_user_input(crs)
    if not value.is_projected or any(a.unit_conversion_factor != 1 for a in value.axis_info):
        raise ValueError('Recorded projected metre CRS required')
    return Transformer.from_crs('OGC:CRS84', value, always_xy=True).transform


def provider_areas(document, config):
    if document.get('type') != 'FeatureCollection':
        raise ValueError('Provider polygon FeatureCollection required')
    declared = document.get('crs', {}).get('properties', {}).get('name')
    if declared and CRS.from_user_input(declared) != CRS.from_epsg(4326):
        raise ValueError('Provider CRS conflicts with declared geographic longitude/latitude')
    result = []
    labels = []
    for feature in document['features']:
        label = feature['properties'].get('neighbourhood')
        if label not in config['operational_mapping']:
            raise ValueError('Unknown raw polygon label: '+str(label))
        geom = shape(feature['geometry'])
        if geom.geom_type not in {'Polygon', 'MultiPolygon'} or geom.is_empty or not geom.is_valid:
            raise ValueError('Invalid provider polygon: '+label+'; no repair')
        labels.append(label)
        result.append({'raw_label': label, 'group': config['operational_mapping'][label], 'geom': geom})
    if len(labels) != len(set(labels)) or set(labels) != set(config['operational_mapping']):
        raise ValueError('Provider labels missing/duplicated; no invented mapping')
    grouped = [{'group': label, 'raw_components': sorted(r['raw_label'] for r in result if r['group'] == label),
                'geom': unary_union([r['geom'] for r in result if r['group'] == label])}
               for label in sorted(set(config['operational_mapping'].values()))]
    return result, grouped


def audit(rows, mask, raw_areas, grouped, config):
    project = metric_transform(config['metric_crs'])
    metric_mask = transform(project, mask)
    metrics = {a['group']: transform(project, a['geom']) for a in grouped}
    raw_tree = STRtree([a['geom'] for a in raw_areas])
    group_tree = STRtree([a['geom'] for a in grouped])
    assignments = []
    support = Counter()
    eligible_status = Counter()
    mismatch = Counter()
    seen = set()
    for row in rows:
        key = row['listing_id']
        if key in seen:
            raise ValueError('Duplicate listing ID')
        seen.add(key)
        label = row['provider_neighbourhood']
        raw_group = config['operational_mapping'].get(label)
        point = Point(row['longitude'], row['latitude']) if row['longitude'] is not None else None
        inside = point is not None and mask.covers(point)
        raw_hits = sorted(raw_areas[i]['raw_label'] for i in raw_tree.query(point) if raw_areas[i]['geom'].covers(point)) if inside else []
        hits = sorted(grouped[i]['group'] for i in group_tree.query(point) if grouped[i]['geom'].covers(point)) if inside else []
        status = 'invalid_coordinates' if point is None else 'outside_mask' if not inside else 'unmatched' if not hits else 'ambiguous' if len(hits) != 1 else 'unique'
        group = hits[0] if status == 'unique' else None
        eligible = row['dwelling_eligible'] and row['positive_price'] and inside
        agrees = group == raw_group if group is not None and raw_group is not None else None
        if eligible:
            eligible_status[status] += 1
            if group is not None:
                support[group] += 1
            mismatch['raw_label_not_polygon_hit'] += label not in raw_hits
            mismatch['operational_label_mismatch'] += agrees is False
            mismatch['unknown_listing_label'] += raw_group is None
        assignments.append({'listing_id': key, 'raw_label': label, 'raw_polygon_hits': raw_hits,
                            'source_label_group': raw_group, 'operational_group': group,
                            'group_hits': hits, 'assignment_status': status, 'inside_mask': inside,
                            'eligible_positive': eligible, 'operational_agreement': agrees})
    overlaps = []
    for i, a in enumerate(grouped):
        for b in grouped[i+1:]:
            area = metrics[a['group']].intersection(metrics[b['group']]).area
            if area > 0:
                overlaps.append({'groups': [a['group'], b['group']], 'area_m2': area})
    total = sum(support.values())
    summary = {'metric_crs': config['metric_crs'], 'source_crs': 'OGC:CRS84 (RFC7946 default unless explicitly declared)',
               'covers_crs': 'EPSG:4326', 'raw_polygon_count': len(raw_areas),
               'operational_count': len(grouped), 'eligible_positive_status': dict(eligible_status),
               'source_vs_polygon': dict(mismatch), 'overlaps': overlaps,
               'uncovered_mask_m2': metric_mask.difference(unary_union(list(metrics.values()))).area,
               'provider_outside_mask_m2': unary_union(list(metrics.values())).difference(metric_mask).area,
               'groups': [{'name': a['group'], 'raw_components': a['raw_components'],
                           'area_km2': metrics[a['group']].area/1e6, 'eligible_positive_n': support[a['group']],
                           'pre_feature_support_15': support[a['group']] >= 15 and total-support[a['group']] >= 500,
                           'former_support_30': support[a['group']] >= 30 and total-support[a['group']] >= 500}
                          for a in grouped], 'final_sample_frozen': False, 'folds_frozen': False}
    blockers = []
    if any(status != 'unique' and n for status, n in eligible_status.items()):
        blockers.append('Eligible positive inside-mask listings do not all have exactly one operational polygon assignment')
    if mismatch['operational_label_mismatch'] or mismatch['unknown_listing_label']:
        blockers.append('Source operational labels disagree with polygons or are unmapped; assignment policy requires qualification')
    summary.update(status='BLOCKED' if blockers else 'QUALIFIED_OPERATIONAL_WITH_RECORDED_GEOMETRY_LIMITS', blockers=blockers)
    return summary, assignments


def prepare(rows, mask, city, record):
    _, cities = load_design()
    raw, grouped = provider_areas(json.loads(verify_source(record).read_text()), cities[city])
    summary, assignments = audit(rows, mask, raw, grouped, cities[city])
    summary.update(city=city, source=record)
    return summary, assignments, raw, grouped
