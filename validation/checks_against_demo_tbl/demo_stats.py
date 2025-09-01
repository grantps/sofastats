from pathlib import Path
from webbrowser import open_new_tab

from sofastats.output.stats.anova import AnovaDesign
from sofastats.output.stats.chi_square import ChiSquareSpec
from sofastats.output.stats.kruskal_wallis_h import KruskalWallisHSpec
from sofastats.output.stats.mann_whitney_u import MannWhitneyUSpec
from sofastats.output.stats.normality import NormalitySpec
from sofastats.output.stats.pearsons_r import PearsonsRSpec
from sofastats.output.stats.spearmans_r import SpearmansRSpec
from sofastats.output.stats.ttest_indep import TTestIndepSpec
from sofastats.output.stats.ttest_paired import TTestPairedSpec
from sofastats.output.stats.wilcoxon_signed_ranks import WilcoxonSignedRanksSpec

def run_anova():
    stats = AnovaDesign(
        style_name='default', #'prestige_screen',
        grouping_field_name='country',
        group_values=[1, 2, 3],
        measure_field_name='age',
        src_tbl_name='demo_tbl',
        table_filter_clause=None,
        high_precision_required=False,
        decimal_points=3,
    )
    html_item_spec = stats.to_html_design()
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
        grouping_field_name='country',
        group_values=[1, 2, 3],
        measure_field_name='weight',
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
        grouping_field_name='country',
        group_a_value=1,
        group_b_value=3,
        measure_field_name='weight',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
        show_workings=True,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/mann_whitney_u_age_by_country_from_item.html')
    html_item_spec.to_file(fpath, 'Mann-Whitney U')
    open_new_tab(url=f"file://{fpath}")

def run_normality():
    stats = NormalitySpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        variable_a_name='age',
        variable_b_name='weight',
        tbl_filt_clause=None,
        dp=3,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/normality_age_vs_weight.html')
    html_item_spec.to_file(fpath, 'Normality Test')
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
        grouping_field_name='country',
        group_a_value=1,
        group_b_value=3,
        measure_field_name='age',
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

def run_wilcoxon_signed_ranks():
    stats = WilcoxonSignedRanksSpec(
        style_name='default',
        src_tbl_name='demo_tbl',
        variable_a_name='weight',
        variable_b_name='weight2',
        tbl_filt_clause=None,
        cur=None,
        dp=3,
        show_workings=True,
    )
    html_item_spec = stats.to_html_spec()
    fpath = Path('/home/g/Documents/sofastats/reports/wilcoxon_signed_ranks.html')
    html_item_spec.to_file(fpath, "Wilcoxon Signed Ranks")
    open_new_tab(url=f"file://{fpath}")

if __name__ == '__main__':
    pass
    run_anova()
    run_chi_square()
    run_kruskal_wallis_h()
    run_mann_whitney_u()
    run_normality()
    run_pearsonsr()
    run_spearmansr()
    run_ttest_indep()
    run_t_test_paired()
    run_wilcoxon_signed_ranks()
