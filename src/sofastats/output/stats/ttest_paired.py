from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2

from sofastats.conf.main import VAR_LABELS
from sofastats.data_extraction.utils import get_paired_data
from sofastats.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofastats.output.stats.common import get_embedded_histogram_html
from sofastats.output.stats.msgs import CI_EXPLAIN, STD_DEV_EXPLAIN
from sofastats.output.styles.interfaces import StyleSpec
from sofastats.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofastats.output.utils import get_p_explain
from sofastats.stats_calc.engine import ttest_rel as ttest_paired_stats_calc
from sofastats.stats_calc.interfaces import NumericParametricSampleSpecFormatted, TTestPairedResult
from sofastats.utils.maths import format_num
from sofastats.utils.misc import todict
from sofastats.utils.stats import get_p_str

@dataclass(frozen=True)
class Result(TTestPairedResult):
    html_or_msg: str

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
          </tr>
        {% endfor %}
      </tbody>
    </table>

    {% for footnote in footnotes %}
      <p><a id='ft{{ loop.index }}'></a><sup>{{ loop.index }}</sup>{{ footnote }}</p>
    {% endfor %}

    {{ html_or_msg }}

    <p>No worked example available for this test</p>

    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    title = f'Results of Paired Samples t-test of "{result.group_a_spec.lbl}" vs "{result.group_b_spec.lbl}"'
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
        formatted_group_spec = NumericParametricSampleSpecFormatted(
            lbl=orig_group_spec.lbl,
            n=n,
            mean=sample_mean,
            ci95=ci95,
            std_dev=std_dev,
            sample_min=str(orig_group_spec.sample_min),
            sample_max=str(orig_group_spec.sample_max),
        )
        formatted_group_specs.append(formatted_group_spec)
    lbl_a = result.group_a_spec.lbl
    lbl_b = result.group_b_spec.lbl
    p_explain = get_p_explain(lbl_a, lbl_b)
    two_tailed_explanation = (
        "This is a two-tailed result i.e. based on the likelihood of a difference "
        f'where the direction ("{lbl_a}" higher than "{lbl_b}" or "{lbl_b}" higher than "{lbl_a}") '
        "doesn't matter.")
    p_full_explanation = f"{p_explain}</br></br>{two_tailed_explanation}"

    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'style_name_hyphens': style_spec.style_name_hyphens,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,

        'degrees_of_freedom': result.degrees_of_freedom,
        'footnotes': [p_full_explanation, CI_EXPLAIN, STD_DEV_EXPLAIN, ],
        'group_specs': formatted_group_specs,
        'html_or_msg': result.html_or_msg,
        'p': get_p_str(result.p),
        't': round(result.t, dp),
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class TTestPairedSpec(Source):
    style_name: str
    variable_a_name: str
    variable_b_name: str
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
        var_a_label = VAR_LABELS.var2var_lbl.get(self.variable_a_name, self.variable_a_name)
        var_b_label = VAR_LABELS.var2var_lbl.get(self.variable_b_name, self.variable_b_name)
        paired_data = get_paired_data(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            variable_a_name=self.variable_a_name, variable_b_name=self.variable_b_name,
            tbl_filt_clause=self.tbl_filt_clause)
        stats_result = ttest_paired_stats_calc(
            sample_a=paired_data.sample_a, sample_b=paired_data.sample_b,
            label_a=var_a_label, label_b=var_b_label)
        measure_fld_lbl = f'Differences between "{var_a_label}" and "{var_b_label}"'
        try:
            histogram_html = get_embedded_histogram_html(
                'Differences', style_spec.chart, measure_fld_lbl, stats_result.diffs, width_scalar=1.5)
        except Exception as e:
            html_or_msg = (f"<b>{measure_fld_lbl}</b> - unable to display histogram. Reason: {e}")
        else:
            html_or_msg = histogram_html

        result = Result(**todict(stats_result),
            html_or_msg=html_or_msg,
        )
        html = get_html(result, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
