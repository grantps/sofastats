from pathlib import Path
from webbrowser import open_new_tab

from sofastats.conf.main import VAR_LABELS
from sofastats.output.tables.cross_tab import CrossTabTblSpec
from sofastats.output.tables.freq import FreqTblSpec
from sofastats.output.tables.interfaces import DimSpec, Metric, Sort

def run_main_poc_cross_tab():
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='home_country', has_total=True, sort_order=Sort.LBL)
    row_spec_2 = DimSpec(var='car')

    col_spec_0 = DimSpec(var='agegroup', has_total=True, is_col=True)
    col_spec_1 = DimSpec(var='browser', has_total=True, is_col=True, sort_order=Sort.LBL,
         child=DimSpec(var='agegroup', has_total=True, is_col=True,
              pct_metrics=[Metric.ROW_PCT, Metric.COL_PCT]))
    col_spec_2 = DimSpec(var='std_agegroup', has_total=True, is_col=True)

    tbl = CrossTabTblSpec(
        style_name='default',  #'default', 'two_degrees', 'grey_spirals'
        row_specs=[row_spec_0, row_spec_1, row_spec_2],
        col_specs=[col_spec_0, col_spec_1, col_spec_2],
        var_labels=VAR_LABELS,
        src_tbl_name='demo_cross_tab',
        tbl_filt_clause="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        dp=2,
        debug=False,
        verbose=False,
    )
    html_item_spec = tbl.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/main_cross_tab_from_item.html')
    html_item_spec.to_file(fpath, 'Cross Tab')
    open_new_tab(url=f"file://{fpath}")

def run_repeat_level_two_row_var_cross_tab():
    """
    Repeated row level 2 was no issue BUT a bug in the col ordering
    """
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='agegroup', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))

    col_spec_0 = DimSpec(var='browser', has_total=True, is_col=True,
        pct_metrics=[Metric.ROW_PCT, Metric.COL_PCT])

    tbl = CrossTabTblSpec(
        style_name='grey_spirals',  #'default', 'two_degrees', 'grey_spirals'
        row_specs=[row_spec_0, row_spec_1, ],
        col_specs=[col_spec_0, ],
        var_labels=VAR_LABELS,
        src_tbl_name='demo_cross_tab',
        tbl_filt_clause="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        dp=2,
        debug=False,
        verbose=False,
    )
    html_item_spec = tbl.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/cross_tab_repeat_level_two_row_var_from_item.html')
    html_item_spec.to_file(fpath, 'Cross Tab Repeat Level Two Row Var')
    open_new_tab(url=f"file://{fpath}")

def run_simple_freq_tbl():
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='agegroup', has_total=True)

    tbl = FreqTblSpec(
        style_name='grey_spirals',  # 'default', 'two_degrees', 'grey_spirals'
        src_tbl_name='demo_cross_tab',
        row_specs=[row_spec_0, row_spec_1, ],
        var_labels=VAR_LABELS,
        tbl_filt_clause="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        inc_col_pct=True,
        dp=3,
        debug=False,
        verbose=False,
    )
    html_item_spec = tbl.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/freq_table_no_col_pct_from_item.html')
    html_item_spec.to_file(fpath, 'Frequency Table')
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    # run_main_poc_cross_tab()
    # run_repeat_level_two_row_var_cross_tab()
    # run_simple_freq_tbl()
