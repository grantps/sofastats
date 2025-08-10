from pathlib import Path
from webbrowser import open_new_tab

from sofastats.conf.main import VAR_LABELS
from sofastats.output.charts.bar import SimpleBarChartSpec
from sofastats.output.charts.scatterplot import MultiChartSeriesScatterChartSpec
from sofastats.output.stats.anova import AnovaSpec
from sofastats.output.tables.freq import FreqTblSpec
from sofastats.output.tables.interfaces import DimSpec, Sort
from sofastats.stats_calc.interfaces import SortOrder

def simple_bar_chart():
    chart = SimpleBarChartSpec(
        style_name='horrific',
        category_fld_name='browser',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        category_sort_order=SortOrder.VALUE,
        legend_lbl=None,
        rotate_x_lbls=False,
        show_borders=False,
        show_n_records=True,
        x_axis_font_size=12,
        y_axis_title='Freq',
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/test_simple_bar_chart_with_horrific_custom_styling.html')
    html_item_spec.to_file(fpath, 'Simple Bar Chart - Horrific Styling')
    open_new_tab(url=f"file://{fpath}")

def run_anova():
    stats = AnovaSpec(
        style_name='horrific',
        tbl_name='demo_tbl',
        grouping_field_name='country',
        group_values=[1, 2, 3],
        measure_field_name='age',
        tbl_filt_clause=None,
        cur=None,
        high_precision_required=False,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/anova_age_by_country_prestige_screen_with_horrific_custom_styling.html')
    html_item_spec.to_file(fpath, 'ANOVA')
    open_new_tab(url=f"file://{fpath}")

def run_simple_freq_tbl():
    row_spec_0 = DimSpec(var='country', has_total=True,
        child=DimSpec(var='gender', has_total=True, sort_order=Sort.LBL))
    row_spec_1 = DimSpec(var='agegroup', has_total=True)

    tbl = FreqTblSpec(
        style_name='horrific',
        src_tbl_name='demo_cross_tab',
        row_specs=[row_spec_0, row_spec_1, ],
        var_labels=VAR_LABELS,
        cur=None,
        tbl_filt_clause="WHERE browser NOT IN ('Internet Explorer', 'Opera', 'Safari') AND car IN (2, 3, 11)",
        inc_col_pct=True,
        dp=3,
        debug=False,
        verbose=False,
    )
    html_item_spec = tbl.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/freq_table_no_col_pct_with_horrific_custom_styling.html')
    html_item_spec.to_file(fpath, 'Frequency Table')
    open_new_tab(url=f"file://{fpath}")

def multi_chart_series_scatterplot():
    chart = MultiChartSeriesScatterChartSpec(
        style_name='horrific',
        chart_fld_name='gender',
        series_fld_name='country',
        x_fld_name='age',
        y_fld_name='weight',
        tbl_name='demo_tbl',
        tbl_filt_clause=None,
        cur=None,
        show_dot_borders=True,
        show_n_records=True,
        show_regression_line=True,
        x_axis_font_size=10,
    )
    html_item_spec = chart.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/test_multi_chart_series_scatterplot_with_horrific_custom_styling.html')
    html_item_spec.to_file(fpath, 'Multi-Chart Multi-Series Scatterplot')
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    simple_bar_chart()
    run_anova()
    run_simple_freq_tbl()
    multi_chart_series_scatterplot()
