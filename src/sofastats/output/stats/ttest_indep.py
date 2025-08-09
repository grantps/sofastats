from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import jinja2

from sofastats.conf.main import VAR_LABELS
from sofastats.data_extraction.interfaces import ValFilterSpec, ValSpec
from sofastats.data_extraction.utils import get_sample
from sofastats.output.charts import mpl_pngs
from sofastats.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofastats.output.stats.common import get_embedded_histogram_html
from sofastats.output.stats.msgs import (
    CI_EXPLAIN, KURTOSIS_EXPLAIN,
    NORMALITY_MEASURE_EXPLAIN, OBRIEN_EXPLAIN, P_EXPLAIN_TWO_GROUPS,
    SKEW_EXPLAIN, STD_DEV_EXPLAIN,
)
from sofastats.output.styles.interfaces import StyleSpec
from sofastats.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofastats.stats_calc.engine import ttest_ind as ttest_indep_stats_calc
from sofastats.stats_calc.interfaces import NumericParametricSampleSpecFormatted, TTestIndepResult
from sofastats.utils.maths import format_num
from sofastats.utils.misc import todict
from sofastats.utils.stats import get_p_str

@dataclass(frozen=True)
class Result(TTestIndepResult):
    group_lbl: str
    measure_fld_lbl: str
    histograms2show: Sequence[str]

def get_html(result: Result, style_spec: StyleSpec, *, dp: int) -> str:
    tpl = """\
    <style>
        {{ generic_unstyled_css }}
        {{ styled_stats_tbl_css }}
    </style>

    <div class='default'>
    <h2>{{ title }}</h2>

    <p>p value: {{ p }}<a class='tbl-heading-footnote' href='#ft1'><sup>1</sup></a></p>
    <p>t statistic: {{ t }}</p>
    <p>Degrees of Freedom (df): {{ degrees_of_freedom }}</p>
    <p>O'Brien's test for homogeneity of variance: {{ obriens_msg }}<a href='#ft2'><sup>2</sup></a></p>

    <h3>Group summary details</h3>
    <table cellspacing='0'>
      <thead>
        <tr>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Group</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>N</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Mean</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>CI 95%<a class='tbl-heading-footnote-{{ style_name_hyphens }}' href='#ft3'><sup>3</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Standard Deviation<a class='tbl-heading-footnote-{{ style_name_hyphens }}' href='#ft4'><sup>4</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Min</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Max</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Kurtosis<a class='tbl-heading-footnote-{{ style_name_hyphens }}' href='#ft5'><sup>5</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Skew<a class='tbl-heading-footnote-{{ style_name_hyphens }}' href='#ft6'><sup>6</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>p abnormal<a class='tbl-heading-footnote-{{ style_name_hyphens }}' href='#ft7'><sup>7</sup></a></th>
        </tr>
      </thead>
      <tbody>
        {% for group_spec in group_specs %}
          <tr>
            <td class='lbl-{{ style_name_hyphens }}'>{{group_spec.lbl}}</td>
            <td class='right'>{{ group_spec.n }}</td>
            <td class='right'>{{ group_spec.mean }}</td>
            <td class='right'>{{ group_spec.ci95 }}</td>
            <td class='right'>{{ group_spec.std_dev }}</td>
            <td class='right'>{{ group_spec.sample_min }}</td>
            <td class='right'>{{ group_spec.sample_max }}</td>
            <td class='right'>{{ group_spec.kurtosis }}</td>
            <td class='right'>{{ group_spec.skew }}</td>
            <td class='right'>{{ group_spec.p }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    {% for footnote in footnotes %}
      <p><a id='ft{{ loop.index }}'></a><sup>{{ loop.index }}</sup>{{ footnote }}</p>
    {% endfor %}

    {% for histogram2show in histograms2show %}
      {{histogram2show}}  <!-- either an <img> or an error message <p> -->
    {% endfor %}

    <p>No worked example available for this test</p>

    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    title = (f"Results of independent samples t-test of average {result.measure_fld_lbl} "
        f'''for "{result.group_lbl}" groups "{result.group_a_spec.lbl}" and "{result.group_b_spec.lbl}"''')
    num_tpl = f"{{:,.{dp}f}}"  ## use comma as thousands separator, and display specified decimal places
    ## format group details needed by second table
    formatted_group_specs = []
    for orig_group_spec in [result.group_a_spec, result.group_b_spec]:
        n = format_num(orig_group_spec.n)
        ci95_left = num_tpl.format(round(orig_group_spec.ci95[0], dp))
        ci95_right = num_tpl.format(round(orig_group_spec.ci95[1], dp))
        ci95 = f"{ci95_left} - {ci95_right}"
        std_dev = num_tpl.format(round(orig_group_spec.std_dev, dp))
        sample_mean = num_tpl.format(round(orig_group_spec.mean, dp))
        kurt = num_tpl.format(round(orig_group_spec.kurtosis, dp))
        skew_val = num_tpl.format(round(orig_group_spec.skew, dp))
        formatted_group_spec = NumericParametricSampleSpecFormatted(
            lbl=orig_group_spec.lbl,
            n=n,
            mean=sample_mean,
            ci95=ci95,
            std_dev=std_dev,
            sample_min=str(orig_group_spec.sample_min),
            sample_max=str(orig_group_spec.sample_max),
            kurtosis=kurt,
            skew=skew_val,
            p=orig_group_spec.p,
        )
        formatted_group_specs.append(formatted_group_spec)
    lbl_a = result.group_a_spec.lbl
    lbl_b = result.group_b_spec.lbl
    two_tailed_explanation = (
        "This is a two-tailed result i.e. based on the likelihood of a difference "
        f'where the direction ("{lbl_a}" higher than "{lbl_b}" or "{lbl_b}" higher than "{lbl_a}") '
        "doesn't matter.")
    p_full_explanation = f"{P_EXPLAIN_TWO_GROUPS}<br><br>{two_tailed_explanation}"

    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'style_name_hyphens': style_spec.style_name_hyphens,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,

        'degrees_of_freedom': result.degrees_of_freedom,
        'footnotes': [p_full_explanation,
            OBRIEN_EXPLAIN, CI_EXPLAIN, STD_DEV_EXPLAIN, KURTOSIS_EXPLAIN, SKEW_EXPLAIN, NORMALITY_MEASURE_EXPLAIN],
        'group_specs': formatted_group_specs,
        'histograms2show': result.histograms2show,
        'obriens_msg': result.obriens_msg,
        'p': get_p_str(result.p),
        't': round(result.t, dp),
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class TTestIndepSpec(Source):
    style_name: str
    grouping_fld_name: str
    group_a_val: Any
    group_b_val: Any
    measure_fld_name: str
    dp: int = 3

    ## do not try to DRY this repeated code ;-) - see doc string for Source
    csv_fpath: Path | None = None
    csv_separator: str = ','
    overwrite_csv_derived_tbl_if_there: bool = False
    cur: Any | None = None
    dbe_name: str | None = None  ## database engine name
    src_tbl_name: str | None = None
    tbl_filt_clause: str | None = None

    def to_html_spec(self) -> HTMLItemSpec:
        ## style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        grouping_fld_lbl = VAR_LABELS.var2var_lbl.get(self.grouping_fld_name, self.grouping_fld_name)
        measure_fld_lbl = VAR_LABELS.var2var_lbl.get(self.measure_fld_name, {})
        val2lbl = VAR_LABELS.var2val2lbl.get(self.grouping_fld_name, {})
        group_a_val_spec = ValSpec(val=self.group_a_val, lbl=val2lbl.get(self.group_a_val, str(self.group_a_val)))
        group_b_val_spec = ValSpec(val=self.group_b_val, lbl=val2lbl.get(self.group_b_val, str(self.group_b_val)))
        ## data
        ## build samples ready for ttest_indep function
        grouping_filt_a = ValFilterSpec(
            variable_name=self.grouping_fld_name, val_spec=group_a_val_spec, val_is_numeric=True)
        sample_a = get_sample(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            grouping_filt=grouping_filt_a, measure_fld_name=self.measure_fld_name,
            tbl_filt_clause=self.tbl_filt_clause)
        grouping_filt_b = ValFilterSpec(
            variable_name=self.grouping_fld_name, val_spec=group_b_val_spec, val_is_numeric=True)
        sample_b = get_sample(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            grouping_filt=grouping_filt_b, measure_fld_name=self.measure_fld_name,
            tbl_filt_clause=self.tbl_filt_clause)
        ## get result
        stats_result = ttest_indep_stats_calc(sample_a, sample_b)

        mpl_pngs.set_gen_mpl_settings(axes_lbl_size=10, xtick_lbl_size=8, ytick_lbl_size=8)
        histograms2show = []
        for group_spec in [stats_result.group_a_spec, stats_result.group_b_spec]:
            try:
                histogram_html = get_embedded_histogram_html(
                    measure_fld_lbl, style_spec.chart, group_spec.vals, group_spec.lbl)
            except Exception as e:
                html_or_msg = (f"<b>{group_spec.lbl}</b> - unable to display histogram. Reason: {e}")
            else:
                html_or_msg = histogram_html
            histograms2show.append(html_or_msg)

        result = Result(**todict(stats_result),
            group_lbl=grouping_fld_lbl,
            measure_fld_lbl=measure_fld_lbl,
            histograms2show=histograms2show,
        )
        html = get_html(result, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
