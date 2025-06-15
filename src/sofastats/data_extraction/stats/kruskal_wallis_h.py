from sofastats.conf.main import DbeSpec
from sofastats.data_extraction.db import ExtendedCursor
from sofastats.data_extraction.interfaces import ValSpec
from sofastats.data_extraction.utils import get_sample
from sofastats.stats_calc import interfaces as stats_interfaces, engine

def get_results(*, cur: ExtendedCursor, dbe_spec: DbeSpec, src_tbl_name: str,
        grouping_fld_name: str, group_a_val_spec: ValSpec, group_b_val_spec: ValSpec, grouping_val_is_numeric,
        measure_fld_name: str, tbl_filt_clause: str | None = None) -> stats_interfaces.KruskalWallisHResult:
    sample_a = get_sample(cur=cur, dbe_spec=dbe_spec, src_tbl_name=src_tbl_name,
        grouping_filt_fld_name=grouping_fld_name,
        grouping_filt_val_spec=group_a_val_spec,
        grouping_filt_val_is_numeric=grouping_val_is_numeric,
        measure_fld_name=measure_fld_name, tbl_filt_clause=tbl_filt_clause)
    sample_b = get_sample(cur=cur, dbe_spec=dbe_spec, src_tbl_name=src_tbl_name,
        grouping_filt_fld_name=grouping_fld_name,
        grouping_filt_val_spec=group_b_val_spec,
        grouping_filt_val_is_numeric=grouping_val_is_numeric,
        measure_fld_name=measure_fld_name, tbl_filt_clause=tbl_filt_clause)
    samples = [sample_a, sample_b]
    labels = [sample_a.lbl, sample_b.lbl]
    return engine.kruskalwallish(samples, labels)
