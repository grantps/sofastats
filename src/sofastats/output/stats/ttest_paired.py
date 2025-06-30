from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2

from sofastats.conf.main import VAR_LABELS
from sofastats.data_extraction.utils import get_paired_data
from sofastats.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofastats.output.styles.interfaces import StyleSpec
from sofastats.output.styles.utils import get_generic_unstyled_css, get_style_spec, get_styled_stats_tbl_css
from sofastats.stats_calc.engine import ttest_rel as ttest_paired_stats_calc
from sofastats.stats_calc.interfaces import TTestPairedResult
from sofastats.utils.misc import todict

@dataclass(frozen=True)
class Result(TTestPairedResult):
    pass

def get_html(result: Result, style_spec: StyleSpec, *, dp: int) -> str:
    tpl = """\
    <style>
        {{ generic_unstyled_css }}
        {{ styled_stats_tbl_css }}
    </style>

    <div class='default'>
    <h2>{{ title }}</h2>

    {% if worked_example %}
      {{ worked_example }}
    {% endif %}

    </div>
    """
    generic_unstyled_css = get_generic_unstyled_css()
    styled_stats_tbl_css = get_styled_stats_tbl_css(style_spec)

    title = 'sausage'

    context = {
        'generic_unstyled_css': generic_unstyled_css,
        'style_name_hyphens': style_spec.style_name_hyphens,
        'styled_stats_tbl_css': styled_stats_tbl_css,
        'title': title,
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
        var_a_label = VAR_LABELS.var2var_lbl.get(self.variable_a_name, self.variable_a_name)
        var_b_label = VAR_LABELS.var2var_lbl.get(self.variable_b_name, self.variable_b_name)
        paired_data = get_paired_data(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            variable_a_name=self.variable_a_name, variable_b_name=self.variable_b_name,
            tbl_filt_clause=self.tbl_filt_clause)
        stats_result = ttest_paired_stats_calc(
            sample_a=paired_data.sample_a, sample_b=paired_data.sample_b,
            label_a=var_a_label, label_b=var_b_label)
        result = Result(**todict(stats_result),

        )
        html = get_html(result, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
