from pathlib import Path
from webbrowser import open_new_tab

from sofastats.output.stats.anova import AnovaSpec
from sofastats.output.stats.chi_square import ChiSquareSpec
from sofastats.output.stats.kruskal_wallis_h import KruskalWallisHSpec
from sofastats.output.stats.mann_whitney_u import MannWhitneyUSpec
from sofastats.output.stats.pearsonsr import PearsonsRSpec
from sofastats.output.stats.spearmansr import SpearmansRSpec
from sofastats.output.stats.ttest_indep import TTestIndepSpec
from sofastats.output.stats.ttest_paired import TTestPairedSpec

def run_anova():
    stats = AnovaSpec(
        style_name='default', #'prestige_screen',
        grouping_fld_name='country',
        group_vals=[1, 2, 3],
        measure_fld_name='age',
        src_tbl_name='demo_tbl',
        tbl_filt_clause=None,
        high_precision_required=False,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/anova_age_by_country_prestige_screen_from_item.html')
    html_item_spec.to_file(fpath, 'ANOVA')
    open_new_tab(url=f"file://{fpath}")

def run_chi_square():
    stats = ChiSquareSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        variable_a_name='agegroup',
        variable_b_name='country',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
        show_workings=True,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/chi_square_stats.html')
    html_item_spec.to_file(fpath, 'Chi Square Test')
    open_new_tab(url=f"file://{fpath}")

def run_kruskal_wallis_h():
    stats = KruskalWallisHSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        grouping_fld_name='country',
        group_vals=[1, 2, 3],
        measure_fld_name='weight',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
        show_workings=True,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/kruskal_wallis_h.html')
    html_item_spec.to_file(fpath, "Kruskal-Wallis H Test")
    open_new_tab(url=f"file://{fpath}")

def run_mann_whitney_u():
    stats = MannWhitneyUSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        grouping_fld_name='country',
        group_a_val=1,
        group_b_val=3,
        measure_fld_name='weight',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
        show_workings=True,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/mann_whitney_u_age_by_country_from_item.html')
    html_item_spec.to_file(fpath, 'Mann-Whitney U')
    open_new_tab(url=f"file://{fpath}")

def run_pearsonsr():
    stats = PearsonsRSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        variable_a_name='age',
        variable_b_name='weight',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/pearsonsr.html')
    html_item_spec.to_file(fpath, "Pearson's R Test")
    open_new_tab(url=f"file://{fpath}")

def run_spearmansr():
    stats = SpearmansRSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        variable_a_name='age',
        variable_b_name='weight',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
        show_workings=True,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/spearmansr.html')
    html_item_spec.to_file(fpath, "Spearman's R Test")
    open_new_tab(url=f"file://{fpath}")

def run_ttest_indep():
    stats = TTestIndepSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        grouping_fld_name='country',
        group_a_val=1,
        group_b_val=3,
        measure_fld_name='age',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/ttest_indep_age_by_country_from_item.html')
    html_item_spec.to_file(fpath, 'Independent t-test')
    open_new_tab(url=f"file://{fpath}")

def run_t_test_paired():
    stats = TTestPairedSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        variable_a_name='weight',
        variable_b_name='weight2',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/t_test_paired.html')
    html_item_spec.to_file(fpath, "Paired T-Test")
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    # run_anova()
    # run_chi_square()
    # run_kruskal_wallis_h()
    # run_mann_whitney_u()
    # run_pearsonsr()
    # run_spearmansr()
    # run_ttest_indep()
    # run_t_test_paired()
