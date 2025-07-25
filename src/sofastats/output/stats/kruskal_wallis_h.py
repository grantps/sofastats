from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2

from sofastats.conf.main import VAR_LABELS
from sofastats.data_extraction.interfaces import ValFilterSpec, ValSpec
from sofastats.data_extraction.utils import get_sample
from sofastats.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofastats.output.stats.msgs import (
    ONE_TAIL_EXPLAIN, ONE_TAILED_EXPLANATION, P_EXPLAIN_MULTIPLE_GROUPS, P_EXPLANATION_WHEN_MULTIPLE_GROUPS)
from sofastats.output.styles.interfaces import StyleSpec
from sofastats.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofastats.output.utils import get_p_explain
from sofastats.stats_calc.engine import kruskalwallish as kruskal_wallis_h_stats_calc
from sofastats.stats_calc.interfaces import KruskalWallisHResult, NumericNonParametricSampleSpecFormatted
from sofastats.utils.maths import format_num, is_numeric
from sofastats.utils.misc import todict
from sofastats.utils.stats import get_p_str

@dataclass(frozen=True)
class Result(KruskalWallisHResult):
    group_lbl: str
    measure_fld_lbl: str

def get_html(result: Result, style_spec: StyleSpec, *, dp: int) -> str:
    tpl = """\
    <style>
        {{ generic_unstyled_css }}
        {{ styled_stats_tbl_css }}
    </style>

    <div class='default'>
    <h2>{{ title }}</h2>

    <p>p value: {{ p }}<a class='tbl-heading-footnote-{{ style_name_hyphens }}' href='#ft1'><sup>1</sup></a></p>
    <p>Kruskal-Wallis H statistic: {{ h }}</p>
    <p>Degrees of Freedom (df): {{ degrees_of_freedom }}</p>
    <table cellspacing='0'>
      <thead>
        <tr>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Group</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>N</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Median</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Min</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Max</th>
        </tr>
      </thead>
      <tbody>
        {% for group_spec in group_specs %}
          <tr>
            <td class='lbl-{{ style_name_hyphens }}'>{{group_spec.lbl}}</td>
            <td class='right'>{{ group_spec.n }}</td>
            <td class='right'>{{ group_spec.median }}</td>
            <td class='right'>{{ group_spec.sample_min }}</td>
            <td class='right'>{{ group_spec.sample_max }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <p><a id='ft1'></a><sup>1</sup>{{ p_explain_multiple_groups }}<br><br>{{one_tail_explain}}</p>

    <p>No worked example available for this test</p>

    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    group_val_lbls = [group_spec.lbl for group_spec in result.group_specs]
    if len(group_val_lbls) < 2:
        raise Exception(f"Expected multiple groups in Kruskal-Wallis analysis. Details:\n{result}")
    group_a_lbl = group_val_lbls[0]
    group_b_lbl = group_val_lbls[-1]
    title = (f"Results of Kruskal-Wallis H test of average {result.measure_fld_lbl} "
        f'for "{result.group_lbl}" groups from "{group_a_lbl}" to "{group_b_lbl}"')
    p_explain = get_p_explain(group_a_lbl, group_b_lbl)
    p_full_explanation = f"{p_explain}</br></br>{ONE_TAILED_EXPLANATION}"
    formatted_group_specs = []
    num_tpl = f"{{:,.{dp}f}}"  ## use comma as thousands separator, and display specified decimal places
    for orig_group_spec in result.group_specs:
        n = format_num(orig_group_spec.n)
        formatted_group_spec = NumericNonParametricSampleSpecFormatted(
            lbl=orig_group_spec.lbl,
            n=n,
            median=num_tpl.format(round(orig_group_spec.median, dp)),
            sample_min=num_tpl.format(round(orig_group_spec.sample_min, dp)),
            sample_max=num_tpl.format(round(orig_group_spec.sample_max, dp)),
        )
        formatted_group_specs.append(formatted_group_spec)
    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'style_name_hyphens': style_spec.style_name_hyphens,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,

        'degrees_of_freedom': result.degrees_of_freedom,
        'footnotes': [p_full_explanation, P_EXPLANATION_WHEN_MULTIPLE_GROUPS, ],
        'group_specs': formatted_group_specs,
        'h': round(result.h, dp),
        'one_tail_explain': ONE_TAIL_EXPLAIN,
        'p': get_p_str(result.p),
        'p_explain_multiple_groups': P_EXPLAIN_MULTIPLE_GROUPS,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class KruskalWallisHSpec(Source):
    style_name: str
    grouping_fld_name: str
    group_vals: Sequence[Any]
    measure_fld_name: str
    dp: int = 3
    show_workings: bool = False

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
        group_lbl = VAR_LABELS.var2var_lbl.get(self.grouping_fld_name, self.grouping_fld_name)
        measure_fld_lbl = VAR_LABELS.var2var_lbl.get(self.measure_fld_name, self.measure_fld_name)
        val2lbl = VAR_LABELS.var2val2lbl.get(self.grouping_fld_name)
        grouping_fld_val_specs = list({
            ValSpec(val=group_val, lbl=val2lbl.get(group_val, str(group_val))) for group_val in self.group_vals})
        grouping_fld_val_specs.sort(key=lambda vs: vs.lbl)
        ## data
        grouping_val_is_numeric = all(is_numeric(x) for x in self.group_vals)
        samples = []
        labels = []
        for grouping_fld_val_spec in grouping_fld_val_specs:
            grouping_filt = ValFilterSpec(variable_name=self.grouping_fld_name, val_spec=grouping_fld_val_spec,
                val_is_numeric=grouping_val_is_numeric)
            sample = get_sample(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
                grouping_filt=grouping_filt, measure_fld_name=self.measure_fld_name,
                tbl_filt_clause=self.tbl_filt_clause)
            samples.append(sample)
            labels.append(grouping_fld_val_spec.lbl)
        stats_result = kruskal_wallis_h_stats_calc(samples, labels)
        result = Result(**todict(stats_result),
            group_lbl=group_lbl,
            measure_fld_lbl=measure_fld_lbl,
        )
        html = get_html(result, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
