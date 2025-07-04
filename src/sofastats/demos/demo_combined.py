from webbrowser import open_new_tab

from sofastats.conf.main import INTERNAL_REPORT_FOLDER, VAR_LABELS
from sofastats.output.charts.bar import SimpleBarChartSpec
from sofastats.output.charts.boxplot import MultiSeriesBoxplotChartSpec
from sofastats.output.stats.anova import AnovaSpec
from sofastats.output.tables.cross_tab import CrossTabTblSpec
from sofastats.output.tables.freq import FreqTblSpec
from sofastats.output.tables.interfaces import DimSpec, Metric, Sort
from sofastats.output.utils import get_report
from sofastats.stats_calc.interfaces import BoxplotType, SortOrder

def get_simple_bar_chart_lots_of_x_vals():
    chart = SimpleBarChartSpec(
        style_name='prestige_screen',
        category_fld_name='car',
        src_tbl_name='demo_tbl',
        tbl_filt_clause=None,
        category_sort_order=SortOrder.VALUE,
        legend_lbl=None,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    return chart

def get_main_poc_cross_tab() -> CrossTabTblSpec:
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
        src_tbl_name='demo_cross_tab',
        row_specs=[row_spec_0, row_spec_1, row_spec_2],
        col_specs=[col_spec_0, col_spec_1, col_spec_2],
        var_labels=VAR_LABELS,
        tbl_filt_clause="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        dp=2,
        debug=False,
        verbose=False,
    )
    return tbl

def get_simple_freq_tbl() -> FreqTblSpec:
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
    return tbl

def get_multi_series_boxplot() -> MultiSeriesBoxplotChartSpec:
    chart = MultiSeriesBoxplotChartSpec(
        style_name='default',
        series_fld_name='gender',
        category_fld_name='country',
        fld_name='age',
        src_tbl_name='demo_tbl',
        tbl_filt_clause=None,
        category_sort_order=SortOrder.LABEL,
        boxplot_type=BoxplotType.INSIDE_1_POINT_5_TIMES_IQR,
        show_n_records=True,
        x_axis_font_size=12,
        dp=3,
    )
    return chart

def get_anova() -> AnovaSpec:
    stats = AnovaSpec(
        style_name='two_degrees',  # 'prestige_screen',
        src_tbl_name='demo_tbl',
        grouping_fld_name='country',
        group_vals=[1, 2, 3],
        measure_fld_name='age',
        tbl_filt_clause=None,
        high_precision_required=False,
        dp=3,
    )
    return stats

def run_report():
    bar_chart_lots_of_x_vals = get_simple_bar_chart_lots_of_x_vals()
    cross_tab_tbl = get_main_poc_cross_tab()
    multi_series_boxplot = get_multi_series_boxplot()
    freq_tbl = get_simple_freq_tbl()
    anova = get_anova()
    html_items = [
        bar_chart_lots_of_x_vals,
        cross_tab_tbl,
        multi_series_boxplot,
        freq_tbl,
        anova,
    ]
    report = get_report(html_items, 'First ever combined report')
    fpath = INTERNAL_REPORT_FOLDER / 'first_ever_combined_report.html'
    report.to_file(fpath)
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    # run_report()
