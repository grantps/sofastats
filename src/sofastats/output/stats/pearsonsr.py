import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

import jinja2

from sofastats.conf.main import VAR_LABELS
from sofastats.data_extraction.utils import get_paired_data
from sofastats.output.stats.common import get_optimal_min_max
from sofastats.output.charts.mpl_pngs import get_scatterplot_fig
from sofastats.output.charts.scatterplot import ScatterplotConf, ScatterplotSeries
from sofastats.output.interfaces import HTMLItemSpec, OutputItemType, Source
from sofastats.output.stats.interfaces import Coord, CorrelationResult
from sofastats.output.stats.msgs import ONE_TAILED_EXPLANATION
from sofastats.output.styles.interfaces import StyleSpec
from sofastats.output.styles.utils import get_style_spec
from sofastats.output.utils import get_p_explain
from sofastats.stats_calc.engine import get_regression_result, pearsonr as pearsonsr_stats_calc
from sofastats.utils.misc import todict
from sofastats.utils.stats import get_p_str

@dataclass(frozen=True)
class Result(CorrelationResult):
    scatterplot_html: str

def get_html(result: Result, style_spec: StyleSpec, *, dp: int) -> str:
    tpl = """\
    <h2>{{ title }}</h2>

    <p>Two-tailed p value: {{ p_str }} <a href='#ft1'><sup>1</sup></a></p>

    <p>Pearson's R statistic: {{ pearsons_r_rounded }}</p>

    <p>{{ degrees_of_freedom_msg }}</p>

    <p>Linear Regression Details: <a href='#ft2'><sup>2</sup></a></p>

    <ul>
        <li>Slope: {{ slope_rounded }}</li>
        <li>Intercept: {{ intercept_rounded }}</li>
    </ul>

    {{ scatterplot_html }}

    <p>No worked example available for this test</p>

    {% for footnote in footnotes %}
      <p><a id='ft{{ loop.index }}'></a><sup>{{ loop.index }}</sup>{{ footnote }}</p>
    {% endfor %}
    """
    title = ('''Results of Pearson's Test of Linear Correlation for '''
        f'''"{result.variable_a_label}" vs "{result.variable_b_label}"''')
    p_str = get_p_str(result.stats_result.p)
    p_explain = get_p_explain(result.variable_a_label, result.variable_b_label)
    p_full_explanation = f"{p_explain}</br></br>{ONE_TAILED_EXPLANATION}"
    pearsons_r_rounded = round(result.stats_result.r, dp)
    degrees_of_freedom_msg = f"Degrees of Freedom (df): {result.stats_result.degrees_of_freedom}"
    look_at_scatterplot_msg = "Always look at the scatter plot when interpreting the linear regression line."
    slope_rounded = round(result.regression_result.slope, dp)
    intercept_rounded = round(result.regression_result.intercept, dp)

    context = {
        'degrees_of_freedom_msg': degrees_of_freedom_msg,
        'footnotes': [p_full_explanation, look_at_scatterplot_msg],
        'intercept_rounded': intercept_rounded,
        'p_str': p_str,
        'pearsons_r_rounded': pearsons_r_rounded,
        'scatterplot_html': result.scatterplot_html,
        'slope_rounded': slope_rounded,
        'title': title,
    }
    environment = jinja2.Environment()
    template = environment.from_string(tpl)
    html = template.render(context)
    return html

@dataclass(frozen=False)
class PearsonsRSpec(Source):
    style_name: str
    variable_a_name: str
    variable_b_name: str
    dp: int = 3

    ## do not try to DRY this repeated code ;-) - see doc string for Source
    csv_file_path: Path | str | None = None
    csv_separator: str = ','
    overwrite_csv_derived_table_if_there: bool = False
    cur: Any | None = None
    dbe_name: str | None = None  ## database engine name
    src_tbl_name: str | None = None
    tbl_filt_clause: str | None = None

    def to_html_spec(self) -> HTMLItemSpec:
        ## style
        style_spec = get_style_spec(style_name=self.style_name)
        ## lbls
        variable_a_label = VAR_LABELS.var2var_lbl.get(self.variable_a_name, self.variable_a_name)
        variable_b_label = VAR_LABELS.var2var_lbl.get(self.variable_b_name, self.variable_b_name)
        ## data
        paired_data = get_paired_data(cur=self.cur, dbe_spec=self.dbe_spec, src_tbl_name=self.src_tbl_name,
            variable_a_name=self.variable_a_name, variable_a_label=variable_a_label,
            variable_b_name=self.variable_b_name, variable_b_label=variable_b_label,
            tbl_filt_clause=self.tbl_filt_clause)
        coords = [Coord(x=x, y=y) for x, y in zip(paired_data.sample_a.vals, paired_data.sample_b.vals, strict=True)]
        pearsonsr_calc_result = pearsonsr_stats_calc(paired_data.sample_a.vals, paired_data.sample_b.vals)
        regression_result = get_regression_result(xs=paired_data.sample_a.vals,ys=paired_data.sample_b.vals)

        correlation_result = CorrelationResult(
            variable_a_label=variable_a_label,
            variable_b_label=variable_b_label,
            coords=coords,
            stats_result=pearsonsr_calc_result,
            regression_result=regression_result,
        )

        scatterplot_series = ScatterplotSeries(
            coords=correlation_result.coords,
            dot_colour=style_spec.chart.colour_mappings[0].main,
            dot_line_colour=style_spec.chart.major_grid_line_colour,
            show_regression_details=True,
        )
        vars_series = [scatterplot_series, ]
        xs = correlation_result.xs
        x_min, x_max = get_optimal_min_max(axis_min=min(xs), axis_max=max(xs))
        chart_conf = ScatterplotConf(
            width_inches=7.5,
            height_inches=4.0,
            inner_background_colour=style_spec.chart.plot_bg_colour,
            x_axis_label=correlation_result.variable_a_label,
            y_axis_label=correlation_result.variable_b_label,
            show_dot_lines=True,
            x_min=x_min,
            x_max=x_max,
        )
        fig = get_scatterplot_fig(vars_series, chart_conf)
        b_io = BytesIO()
        fig.savefig(b_io, bbox_inches='tight')  ## save to a fake file
        chart_base64 = base64.b64encode(b_io.getvalue()).decode('utf-8')
        scatterplot_html = f'<img src="data:image/png;base64,{chart_base64}"/>'

        result = Result(**todict(correlation_result),
            scatterplot_html=scatterplot_html,
        )
        html = get_html(result, style_spec, dp=self.dp)
        return HTMLItemSpec(
            html_item_str=html,
            style_name=self.style_name,
            output_item_type=OutputItemType.STATS,
        )
