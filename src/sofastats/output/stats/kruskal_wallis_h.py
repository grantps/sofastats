from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2

from sofastats.conf.main import ONE_TAILED_EXPLANATION, P_EXPLANATION_WHEN_MULTIPLE_GROUPS, VAR_LABELS
from sofastats.data_extraction.interfaces import ValSpec
from sofastats.data_extraction.utils import get_sample
from sofastats.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofastats.output.styles.interfaces import StyleSpec
from sofastats.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofastats.output.utils import get_p_explain
from sofastats.stats_calc.engine import kruskalwallish as kruskal_wallis_h_stats_calc
from sofastats.stats_calc.interfaces import KruskalWallisHResult
from sofastats.utils.stats import get_p_str

def make_kruskal_wallis_h_html(results: KruskalWallisHResult, style_spec: StyleSpec, *, dp: int) -> str:
    tpl = """\
    
    
    
    TODO: kruskal_wallis_h this ;-) <=====================================================================================================================================
    
    
    
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
          <th class='firstcolvar-{{ style_name_hyphens }}'>CI 95%<a class='tbl-heading-footnote' href='#ft3'><sup>3</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Standard Deviation<a class='tbl-heading-footnote' href='#ft4'><sup>4</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Min</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Max</th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Kurtosis<a class='tbl-heading-footnote' href='#ft5'><sup>5</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>Skew<a class='tbl-heading-footnote' href='#ft6'><sup>6</sup></a></th>
          <th class='firstcolvar-{{ style_name_hyphens }}'>p abnormal<a class='tbl-heading-footnote' href='#ft7'><sup>7</sup></a></th>
        </tr>
      </thead>
      <tbody>
        {% for group_spec in group_specs %}
          <tr>
            <td class='lbl-{{ style_name_hyphens }}'>{{group_spec.lbl}}</td>
            <td class='right'>{{ group_spec.n }}</td>
            <td class='right'>{{ group_spec.mean }}</td>
            <td class='right'>{{ group_spec.ci95 }}</td>
            <td class='right'>{{ group_spec.stdev }}</td>
            <td class='right'>{{ group_spec.sample_min }}</td>
            <td class='right'>{{ group_spec.sample_max }}</td>
            <td class='right'>{{ group_spec.kurtosis }}</td>
            <td class='right'>{{ group_spec.skew }}</td>
            <td class='right'>{{ group_spec.p }}</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>

    <p><a id='ft1'></a><sup>1</sup>{{ p_explain_multiple_groups }}<br><br>{{one_tail_explain}}</p>
    <p><a id='ft2'></a><sup>2</sup>{{ obrien_explain }}</p>
    <p><a id='ft3'></a><sup>3</sup>{{ ci_explain }}</p>
    <p><a id='ft4'></a><sup>4</sup>{{ std_dev_explain }}</p>
    <p><a id='ft5'></a><sup>5</sup>{{ kurtosis_explain }}</p>
    <p><a id='ft6'></a><sup>6</sup>{{ skew_explain }}</p>
    <p><a id='ft7'></a><sup>7</sup>{{ normality_measure_explain }}</p>

    <p>{{ workings_msg }}</p>

    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)
    title = (f"Results of Kruskal-Wallis H test of average {results.measure_fld_lbl} "
        f'for "{results.group_lbl}" groups from "{results.group_a_spec.lbl}" to "{results.group_b_spec.lbl}"')
    p_str = get_p_str(results.stats_result.p)
    p_explain = get_p_explain(results.variable_a_label, results.variable_b_label)
    p_full_explanation = f"{p_explain}</br></br>{ONE_TAILED_EXPLANATION}"

        # html.append('\n<p>' + _('Kruskal-Wallis H statistic') + f': {round(h, dp)}</p>')
        # html.append(f'\n<p>{mg.DF}: {df}</p>')
        # html.append(f"\n\n{mg.REPORT_TABLE_START}<table cellspacing='0'>\n<thead>")
        # html.append('\n<tr>'
        #             + f"<th class='{CSS_FIRST_COL_VAR}'>" + _('Group') + '</th>'
        #             + f"\n<th class='{CSS_FIRST_COL_VAR}'>" + _('N') + '</th>'
        #             + f"\n<th class='{CSS_FIRST_COL_VAR}'>" + _('Median') + '</th>'
        #             + f"\n<th class='{CSS_FIRST_COL_VAR}'>" + _('Min') + '</th>'
        #             + f"\n<th class='{CSS_FIRST_COL_VAR}'>" + _('Max') + '</th></tr>')
        # html.append('\n</thead>\n<tbody>')
        # row_tpl = (f"\n<tr><td class='{CSS_LBL}'>" + '%s</td><td>%s</td>'
        #            + '<td>%s</td><td>%s</td><td>%s</td></tr>')
        # for dic in dics:
        #     html.append(row_tpl % (dic[mg.STATS_DIC_LBL],
        #                            lib.formatnum(dic[mg.STATS_DIC_N]),
        #                            round(dic[mg.STATS_DIC_MEDIAN], dp), dic[mg.STATS_DIC_MIN],
        #                            dic[mg.STATS_DIC_MAX]))
        # html.append(f'\n</tbody></table>{mg.REPORT_TABLE_END}')
        # add_footnotes(footnotes, html)
        # ## details
        # if details:
        #     html.append('<p>No worked example available for this test</p>')
        # if page_break_after:
        #     html.append(f"<br><hr><br><div class='{CSS_PAGE_BREAK_BEFORE}'></div>")
        # output.append_divider(html, title, indiv_title='')
        # return ''.join(html)







    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'style_name_hyphens': style_spec.style_name_hyphens,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,

        'footnotes': [p_full_explanation, P_EXPLANATION_WHEN_MULTIPLE_GROUPS, ],
        'workings_msg': "No worked example available for this test",

        # 'ci_explain': ci_explain,
        # 'degrees_of_freedom': result.degrees_of_freedom,
        # 'group_specs': formatted_group_specs,
        # 'histograms2show': histograms2show,
        # 'kurtosis_explain': kurtosis_explain,
        # 'normality_measure_explain': normality_measure_explain,
        # 'obrien_explain': obrien_explain,
        # 'obriens_msg': result.obriens_msg,
        # 'one_tail_explain': one_tail_explain,
        # 'p_explain_multiple_groups': p_explain_multiple_groups,
        # 'p': get_p_str(result.p),
        # 'skew_explain': skew_explain,
        # 'std_dev_explain': std_dev_explain,
        # 't': round(result.t, dp),
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class KruskalWallisHSpec(Source):
    style_name: str
    grouping_fld_name: str
    group_a_val: Any
    group_b_val: Any
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
        val2lbl = VAR_LABELS.var2val2lbl.get(self.grouping_fld_name)
        group_a_val_spec = ValSpec(val=self.group_a_val, lbl=val2lbl.get(self.group_a_val, str(self.group_a_val)))
        group_b_val_spec = ValSpec(val=self.group_b_val, lbl=val2lbl.get(self.group_b_val, str(self.group_b_val)))
        ## data
        sample_a = get_sample(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            grouping_filt_fld_name=self.grouping_fld_name,
            grouping_filt_val_spec=group_a_val_spec,
            grouping_filt_val_is_numeric=True,
            measure_fld_name=self.measure_fld_name, tbl_filt_clause=self.tbl_filt_clause)
        sample_b = get_sample(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            grouping_filt_fld_name=self.grouping_fld_name,
            grouping_filt_val_spec=group_b_val_spec,
            grouping_filt_val_is_numeric=True,
            measure_fld_name=self.measure_fld_name, tbl_filt_clause=self.tbl_filt_clause)
        samples = [sample_a, sample_b]
        labels = [sample_a.lbl, sample_b.lbl]
        results = kruskal_wallis_h_stats_calc(samples, labels)
        html = make_kruskal_wallis_h_html(results, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
