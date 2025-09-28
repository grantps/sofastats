"""
c && cd ~/projects/sofastats/example_scripts/ && panel serve --dev flex.py

Flexible design inspired by Charlotte's figma layout - particularly the collapsible data sidebar.

https://discourse.holoviz.org/t/how-to-remove-sidebar-and-update-the-webpage-after-template-is-served/8261/3

To keep ability to open and close sidebar without showing hamburger bars
    <span onclick="{{ 'openNav()' if collapsed_sidebar else 'closeNav()' }}" id="sidebar-button">
<!--      <div class="pn-bar"></div>-->
<!--      <div class="pn-bar"></div>-->
<!--      <div class="pn-bar"></div>-->
    </span>
"""
from collections.abc import Collection
from enum import StrEnum
from pathlib import Path

import pandas as pd
import panel as pn
import param
from ruamel.yaml import YAML

pn.extension()
pn.extension('modal')
pn.extension('tabulator')

## look in main css for template used to see what controls sidebar
## https://community.retool.com/t/how-to-open-a-modal-component-in-full-screen/18720/4
css = """
#main {
    border-left: solid grey 3px;
}
.full-screen-modal {
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}
"""
pn.extension(raw_css=[css])

yaml = YAML(typ='safe')  ## default, if not specified, is 'rt' (round-trip)
try:
    data_label_mappings = yaml.load(Path.cwd() / 'data_labels.yaml')  ## might be a str or Path so make sure
except FileNotFoundError:
    data_label_mappings = {}

class Alternative(StrEnum):
    NONE = 'None'
    TRUE = 'True'
    FALSE = 'False'

class DiffVsRel(StrEnum):
    DIFFERENCE = 'Difference'
    RELATIONSHIP = 'Relationship'
    UNKNOWN = 'Not Sure'

class IndepVsPaired(StrEnum):
    INDEPENDENT = 'Independent'
    PAIRED = 'Paired'
    UNKNOWN = 'Not Sure'

class Normal(StrEnum):
    NORMAL = 'Normal'
    NOT_NORMAL = 'Not Normal'
    UNKNOWN = 'Not Sure'

class NumGroups(StrEnum):
    TWO = '2 Groups'
    THREE_PLUS = '3+ Groups'
    UNKNOWN = 'Not Sure'

class OrdinalVsCategorical(StrEnum):
    ORDINAL = 'Ordinal'
    CATEGORICAL = 'Categorical'
    UNKNOWN = 'Not Sure'

class StatsOptions(StrEnum):
    ANOVA = 'ANOVA'
    CHI_SQUARE = 'Chi Square'
    KRUSKAL_WALLIS = 'Kruskal-Wallis H'
    MANN_WHITNEY = 'Mann-Whitney U'
    PEARSONS = "Pearson's R Correlation"
    SPEARMANS = "Spearman's R Correlation"
    TTEST_INDEP = 'Independent Samples T-Test'
    TTEST_PAIRED = 'Paired Samples T-Test'
    WILCOXON = 'Wilcoxon Signed Ranks'

class Bool(param.Parameterized):
    value = param.Boolean(default=False)

class Choice(param.Parameterized):
    value = param.String(default=Alternative.NONE)

## PARAMS
## stats helper
difference_not_relationship_param = Choice(value=DiffVsRel.UNKNOWN)

two_not_three_plus_groups_for_diff_param = Choice(value=NumGroups.UNKNOWN)
normal_not_abnormal_for_diff_param = Choice(value=Normal.UNKNOWN)
independent_not_paired_for_diff_param = Choice(value=IndepVsPaired.UNKNOWN)

ordinal_at_least_for_rel_param = Choice(value=OrdinalVsCategorical.UNKNOWN)
normal_not_abnormal_for_rel_param = Choice(value=Normal.UNKNOWN)

got_data_param = Bool(value=False)

class SidebarToggle(pn.custom.JSComponent):
    value = param.Boolean(doc="If True the sidebar is visible, if False it is hidden")

    _esm = """
export function render({ model }) {
    model.on('value', () => {
        if (model.value) {
            document.getElementById('sidebar-button').style.display = 'none';
            document.getElementById('sidebar').style.display = 'block';
        } else {
            document.getElementById('sidebar-button').style.display = 'none';
            document.getElementById('sidebar').style.display = 'none';
        }
    });
}
"""

data_toggle = SidebarToggle(value=True)

btn_data_toggle = pn.widgets.Button(
    name="🞀 Close Data Window",
    description="Close uploaded data window",
    button_type="light", button_style='solid',
    styles={
        'margin-left': '-20px', 'margin-bottom': '20px',
        'border': '2px solid grey',
        'border-radius': '5px',
    })


class Data:

    @staticmethod
    def next_step(selected_csv_fpath: Path):
        if selected_csv_fpath:
            next_step_msg = "Click on the Tables & Charts tab or the Statistics tab and get some output results ..."
        else:
            next_step_msg = "Select a CSV file containing the data you want to understand ..."
        return pn.pane.Alert(next_step_msg, alert_type='info')

    @staticmethod
    def display_csv(selected_csv_fpath: Path):
        if selected_csv_fpath:
            got_data_param.value = True
            df = pd.read_csv(selected_csv_fpath)
            global df_csv  ## so can decide what options to display
            df_csv = df.copy()
            global csv_fpath
            csv_fpath = selected_csv_fpath
            ## apply any labels
            col_name_vals = []
            for i, col in enumerate(df.columns):
                col_name_vals.append((col, df[col]))
                if col in data_label_mappings.keys():
                    val_mapping = data_label_mappings.get(col, {}).get('value_labels', {})
                    if val_mapping:
                        col_name_vals.append((f"{col}<br>(labelled)", df[col].apply(lambda num_val: val_mapping.get(num_val, num_val))))
            df_labelled = pd.DataFrame(dict(col_name_vals))
            table_df = pn.widgets.Tabulator(df_labelled, page_size=10, disabled=True)
            table_df.value = df_labelled
            return table_df
        else:
            return None

    def __init__(self):
        self.data_title = pn.pane.Markdown(f"## Start here - select a CSV", styles={'color': "#0072b5"})
        self.file_input = pn.widgets.FileInput(accept='.csv')
        self.next_step_or_none = pn.bind(Data.next_step, self.file_input.param.filename)
        self.data_table_or_none = pn.bind(Data.display_csv, self.file_input.param.filename)

    def ui(self):
        data_column = pn.Column(
            self.data_title, self.next_step_or_none, self.file_input, self.data_table_or_none,
            data_toggle,
        )
        return data_column

data_col = Data().ui()

@pn.depends(btn_data_toggle, watch=True)
def _update_main(_):
    data_toggle.value = not data_toggle.value

    if not data_toggle.value:
        btn_data_toggle.name = "Open Data Window 🞂"
        btn_data_toggle.description = "See your uploaded data again"
    else:
        btn_data_toggle.name = "🞀 Close Data Window"
        btn_data_toggle.description = "Close uploaded data window"

charts_and_tables_text = pn.pane.Markdown("Charts & Tables")

difference_vs_relationship_radio = pn.widgets.RadioButtonGroup(
    name='Difference vs Relationship',
    options=[
        DiffVsRel.DIFFERENCE,
        DiffVsRel.RELATIONSHIP,
        DiffVsRel.UNKNOWN,
    ],
    button_type='primary', button_style='outline',
    description=("Are you trying to see if there are differences between groups "
        "(e.g. different mean height between players of different sports) "
        "or relationships (e.g. between education level and income)?"),
    value=DiffVsRel.UNKNOWN,
)

## https://panel.holoviz.org/how_to/styling/apply_css.html
progress_stylesheet = """
progress {
  height: 5px;
}
"""
chooser_progress = pn.indicators.Progress(name='Progress', value=0, width=400, height=5, height_policy='fixed', stylesheets=[progress_stylesheet])
chooser_progress.css_classes = ['custom-progress']

def set_chooser_progress(items: Collection[StatsOptions]):
    """
    We start with all items being in contention and end up with 1 and only 1.
    So we go from 9 to 1 which is 8 steps.
    In contention  9   8   7   6   5   4   3   2   1
    Progress       0   1   2   3   4   5   6   7   8
    So 9-9, 9-8, ... 9-1
    So len(all options) - len(in contention)
    """
    n_all_options = len(StatsOptions)
    n_in_contention = len(items)
    score = n_all_options - n_in_contention
    total = n_all_options - 1
    progress_fraction = score / total
    progress_value = round(progress_fraction * 100)
    chooser_progress.value = progress_value

## https://panel.holoviz.org/how_to/styling/apply_css.html
btn_return_stylesheet = """
:host(.solid) .bk-btn.bk-btn-primary {
  font-size: 14px;
}
"""
btn_return_to_stats_selection = pn.widgets.Button(name="Configure Test", button_type='primary', stylesheets=[btn_return_stylesheet])


class SubChooser:

    @staticmethod
    def respond_to_choices(difference_not_relationship_value, two_not_three_plus_groups_for_diff_value,
            normal_not_abnormal_for_diff_value, independent_not_paired_for_diff_value,
            ordinal_at_least_for_rel_value,
            normal_not_abnormal_for_rel_value):
        if difference_not_relationship_value == DiffVsRel.UNKNOWN:
            items = sorted(StatsOptions)
        elif difference_not_relationship_value == DiffVsRel.DIFFERENCE:
            if two_not_three_plus_groups_for_diff_value == NumGroups.UNKNOWN:
                if normal_not_abnormal_for_diff_value == Normal.UNKNOWN:
                    items = [StatsOptions.ANOVA, StatsOptions.TTEST_INDEP, StatsOptions.TTEST_PAIRED,
                             StatsOptions.KRUSKAL_WALLIS, StatsOptions.MANN_WHITNEY, StatsOptions.WILCOXON]
                elif normal_not_abnormal_for_diff_value == Normal.NORMAL:
                    items = [StatsOptions.ANOVA, StatsOptions.TTEST_INDEP, StatsOptions.TTEST_PAIRED]
                elif normal_not_abnormal_for_diff_value == Normal.NOT_NORMAL:
                    items = [StatsOptions.KRUSKAL_WALLIS, StatsOptions.MANN_WHITNEY, StatsOptions.WILCOXON]
                else:
                    raise Exception(F"Unexpected {normal_not_abnormal_for_diff_value=}")
            elif two_not_three_plus_groups_for_diff_value == NumGroups.TWO:
                if normal_not_abnormal_for_diff_value == Normal.UNKNOWN:
                    if independent_not_paired_for_diff_value == IndepVsPaired.UNKNOWN:
                        items = [StatsOptions.TTEST_INDEP, StatsOptions.MANN_WHITNEY,
                                 StatsOptions.TTEST_PAIRED, StatsOptions.WILCOXON]
                    elif independent_not_paired_for_diff_value == IndepVsPaired.INDEPENDENT:
                        items = [StatsOptions.TTEST_INDEP, StatsOptions.MANN_WHITNEY]
                    elif independent_not_paired_for_diff_value == IndepVsPaired.PAIRED:
                        items = [StatsOptions.TTEST_PAIRED, StatsOptions.WILCOXON]
                    else:
                        raise Exception(F"Unexpected {independent_not_paired_for_diff_value=}")
                elif normal_not_abnormal_for_diff_value == Normal.NORMAL:
                    if independent_not_paired_for_diff_value == IndepVsPaired.UNKNOWN:
                        items = [StatsOptions.TTEST_INDEP, StatsOptions.TTEST_PAIRED]
                    elif independent_not_paired_for_diff_value == IndepVsPaired.INDEPENDENT:
                        items = [StatsOptions.TTEST_INDEP, ]
                    elif independent_not_paired_for_diff_value == IndepVsPaired.PAIRED:
                        items = [StatsOptions.TTEST_PAIRED, ]
                    else:
                        raise Exception(F"Unexpected {independent_not_paired_for_diff_value=}")
                elif normal_not_abnormal_for_diff_value == Normal.NOT_NORMAL:
                    if independent_not_paired_for_diff_value == IndepVsPaired.UNKNOWN:
                        items = [StatsOptions.MANN_WHITNEY, StatsOptions.WILCOXON]
                    elif independent_not_paired_for_diff_value == IndepVsPaired.INDEPENDENT:
                        items = [StatsOptions.MANN_WHITNEY]
                    elif independent_not_paired_for_diff_value == IndepVsPaired.PAIRED:
                        items = [StatsOptions.WILCOXON, ]
                    else:
                        raise Exception(F"Unexpected {independent_not_paired_for_diff_value=}")
                else:
                    raise Exception(F"Unexpected {normal_not_abnormal_for_diff_value=}")
            elif two_not_three_plus_groups_for_diff_value == NumGroups.THREE_PLUS:
                if normal_not_abnormal_for_diff_value == Normal.UNKNOWN:
                    items = [StatsOptions.ANOVA, StatsOptions.KRUSKAL_WALLIS]
                elif normal_not_abnormal_for_diff_value == Normal.NORMAL:
                    items = [StatsOptions.ANOVA, ]
                elif normal_not_abnormal_for_diff_value == Normal.NOT_NORMAL:
                    items = [StatsOptions.KRUSKAL_WALLIS, ]
                else:
                    raise Exception(F"Unexpected {normal_not_abnormal_for_diff_value=}")
            else:
                raise Exception(F"Unexpected {two_not_three_plus_groups_for_diff_value=}")
        elif difference_not_relationship_value == DiffVsRel.RELATIONSHIP:
            if ordinal_at_least_for_rel_value == OrdinalVsCategorical.UNKNOWN:
                items = [StatsOptions.CHI_SQUARE, StatsOptions.SPEARMANS, StatsOptions.PEARSONS]
            elif ordinal_at_least_for_rel_value == OrdinalVsCategorical.ORDINAL:
                if normal_not_abnormal_for_rel_value == Normal.UNKNOWN:
                    items = [StatsOptions.SPEARMANS, StatsOptions.PEARSONS]
                elif normal_not_abnormal_for_rel_value == Normal.NORMAL:
                    items = [StatsOptions.PEARSONS, ]
                elif normal_not_abnormal_for_rel_value == Normal.NOT_NORMAL:
                    items = [StatsOptions.SPEARMANS, ]
                else:
                    raise Exception(F"Unexpected {normal_not_abnormal_for_rel_value=}")
            elif ordinal_at_least_for_rel_value == OrdinalVsCategorical.CATEGORICAL:
                items = [StatsOptions.CHI_SQUARE, ]
            else:
                raise Exception(F"Unexpected {ordinal_at_least_for_rel_value=}")
        else:
            raise Exception(F"Unexpected {difference_not_relationship_value=}")
        div_styles = {
            'margin-top': '-30px',
            'margin-bottom': '0',
            'padding': '0 5px 5px 5px',
        }
        internal_css = """
        <style>
            h1 {
              color: #0072b5;
              font-size: 14px;
            }
        </style>
        """
        if len(items) == 1:
            recommendation_html = pn.pane.HTML(styles=div_styles, max_width=500)
            stats_test = items[0]
            if stats_test == StatsOptions.ANOVA:
                content = f"""\
                {internal_css}
                <h1>ANOVA (Analysis Of Variance)</h1>
                <p>The ANOVA (Analysis Of Variance) is good for seeing if there is a difference in means between multiple groups
                when the data is numerical and adequately normal. Generally the ANOVA is robust to non-normality.</p>
                <p>You can evaluate normality by clicking on the "Check Normality" button (under construction).</p>
                <p>The Kruskal-Wallis H may be preferable if your data is not adequately normal.</p>
                """
            elif stats_test == StatsOptions.CHI_SQUARE:
                content = f"""\
                {internal_css}
                <h1>Chi Square Test</h1>
                <p>The Chi Square test is one of the most widely used tests in social science.
                It is good for seeing if the results for two variables are independent or related.
                Is there a relationship between gender and income group for example?</p>
                """
            elif stats_test == StatsOptions.KRUSKAL_WALLIS:
                content = f"""\
                {internal_css}
                <h1>Kruskal-Wallis H Test</h1>
                <p>The Kruskal-Wallis H is good for seeing if there is a difference in values between multiple groups
                when the data is at least ordered (ordinal).</p>
                <p>You can evaluate normality by clicking on the "Check Normality" button (under construction).</p>
                <p>The ANOVA (Analysis Of Variance) may still be preferable if your data is numerical and adequately normal.</p>
                """
            else:
                content = f"""\
                {internal_css}
                <p>Under Construction</p>
                """
            recommendation_html.object = content
            btn_return_to_stats_selection.name = f"Configure {stats_test} ⮕"
            col_recommendation_styles = {
                'background-color': '#F6F6F6',
                'border': '2px solid black',
                'border-radius': '5px',
                'padding': '0 5px 5px 5px',
            }
            col_recommendation = pn.Column(recommendation_html, btn_return_to_stats_selection,
                styles=col_recommendation_styles)
        else:
            col_recommendation = None
        set_chooser_progress(items)
        return col_recommendation

    ## DIFFERENCE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @staticmethod
    def _set_indep_vs_paired_param(indep_vs_paired_value):
        independent_not_paired_for_diff_param.value = indep_vs_paired_value

    @staticmethod
    def get_indep_vs_paired_chooser(two_not_three_plus_groups_for_diff_param_val):
        indep_vs_paired_chooser_or_none = None
        if two_not_three_plus_groups_for_diff_param_val == NumGroups.TWO:
            independent_groups_radio = pn.widgets.RadioButtonGroup(
                name='Independent Groups',
                options=[
                    IndepVsPaired.INDEPENDENT,
                    IndepVsPaired.PAIRED,
                    IndepVsPaired.UNKNOWN,
                ],
                button_type='success', button_style='outline',
                description=("Are the groups independent e.g. 'NZ' and 'USA', or paired "
                    "(e.g. 'Student score before tutoring' and 'Student score after tutoring')?"),
                value=IndepVsPaired.UNKNOWN,
            )
            indep_vs_paired_param_setter = pn.bind(SubChooser._set_indep_vs_paired_param, independent_groups_radio)
            indep_vs_paired_chooser_or_none = pn.Column(
                pn.pane.Markdown("Are the Groups Independent or Paired?"), independent_groups_radio,
                indep_vs_paired_param_setter,
            )
        return indep_vs_paired_chooser_or_none

    @staticmethod
    def _set_norm_for_diff_param(norm_vs_abnormal_value):
        normal_not_abnormal_for_diff_param.value = norm_vs_abnormal_value

    @staticmethod
    def _set_num_of_groups_param(num_of_groups_value):
        two_not_three_plus_groups_for_diff_param.value = num_of_groups_value

    @staticmethod
    def difference_sub_chooser():  ## <====================== DIFFERENCE Main Act!
        normal_for_diff_radio = pn.widgets.RadioButtonGroup(
            name='Normality',
            options=[
                Normal.NORMAL,
                Normal.NOT_NORMAL,
                Normal.UNKNOWN,
            ],
            button_type='success', button_style='outline',
            description=("Is your data normal "
                "i.e. are the values numbers that at least roughly follow a normal distribution curve (bell curve)?"),
            value=Normal.UNKNOWN,
        )
        norm_for_diff_param_setter = pn.bind(SubChooser._set_norm_for_diff_param, normal_for_diff_radio)
        number_of_groups_radio = pn.widgets.RadioButtonGroup(
            name='Number of Groups',
            options=[
                NumGroups.TWO,
                NumGroups.THREE_PLUS,
                NumGroups.UNKNOWN,
            ],
            button_type='success', button_style='outline',
            description=("Are you looking at the difference between two groups "
                "e.g. 'Male' vs 'Female' or between three or more groups e.g. 'Archery' vs 'Badminton' vs 'Basketball'?"),
            value=NumGroups.UNKNOWN,
        )
        indep_vs_paired_chooser = pn.bind(SubChooser.get_indep_vs_paired_chooser, number_of_groups_radio)
        num_of_groups_param_setter = pn.bind(SubChooser._set_num_of_groups_param, number_of_groups_radio)
        col_items = [
            pn.pane.Markdown("Data Values are Normal?"), normal_for_diff_radio,
            pn.pane.Markdown("How Many Groups?"), number_of_groups_radio,
            indep_vs_paired_chooser,
            norm_for_diff_param_setter, num_of_groups_param_setter,
        ]
        sub_chooser = pn.Column(*col_items)
        return sub_chooser

    ## RELATIONSHIP ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @staticmethod
    def _set_norm_for_rel(normal_not_abnormal_for_rel_value):
        normal_not_abnormal_for_rel_param.value = normal_not_abnormal_for_rel_value

    @staticmethod
    def get_normal_chooser_or_none(ordinal_vs_categorical_val):
        normal_chooser_or_none = None
        if ordinal_vs_categorical_val == OrdinalVsCategorical.ORDINAL:
            normal_for_rel_radio = pn.widgets.RadioButtonGroup(
                name='Normality',
                options=[
                    Normal.NORMAL,
                    Normal.NOT_NORMAL,
                    Normal.UNKNOWN,
                ],
                button_type='success', button_style='outline',
                description=("Is your data normal "
                    "i.e. are the values numbers that at least roughly follow a normal distribution curve (bell curve)?"),
                value=Normal.UNKNOWN,
            )
            norm_for_rel_param_setter = pn.bind(SubChooser._set_norm_for_rel, normal_for_rel_radio)
            normal_chooser_or_none = pn.Column(pn.pane.Markdown("Data Values are Normal?"), normal_for_rel_radio,
                norm_for_rel_param_setter)
        return normal_chooser_or_none

    @staticmethod
    def _set_ordinal_vs_categorical(ordinal_vs_categorical_value):
        # print(f"ordinal_at_least_for_rel_param is now '{ordinal_vs_categorical_value}'")
        ordinal_at_least_for_rel_param.value = ordinal_vs_categorical_value

    @staticmethod
    def relationship_sub_chooser():  ## <====================== RELATIONSHIP Main Act!
        ordinal_vs_categorical_radio = pn.widgets.RadioButtonGroup(
            name='Ordinal vs Categorical',
            options=[
                OrdinalVsCategorical.ORDINAL,
                OrdinalVsCategorical.CATEGORICAL,
                OrdinalVsCategorical.UNKNOWN,
            ],
            button_type='success', button_style='outline',
            description=("Do the values have a true sort order (ordinal data) e.g. 1, 2, 3? "
                "Or are they just names e.g. 'NZ', 'Denmark', 'Sri Lanka' (categorical data)?"),
            value=Normal.UNKNOWN,
        )
        normal_chooser_or_none = pn.bind(SubChooser.get_normal_chooser_or_none, ordinal_vs_categorical_radio)
        ordinal_vs_categorical_param_setter = pn.bind(SubChooser._set_ordinal_vs_categorical, ordinal_vs_categorical_radio)
        sub_chooser = pn.Column(
            pn.pane.Markdown("Ordinal or Categorical?"), ordinal_vs_categorical_radio,
            normal_chooser_or_none, ordinal_vs_categorical_param_setter,
        )
        return sub_chooser

    @staticmethod
    def get_ui(diff_not_rel: DiffVsRel) -> pn.Column | None:
        recommendation = pn.bind(SubChooser.respond_to_choices,
            difference_not_relationship_param.param.value,
            two_not_three_plus_groups_for_diff_param.param.value,
            normal_not_abnormal_for_diff_param.param.value,
            independent_not_paired_for_diff_param.param.value,
            ordinal_at_least_for_rel_param.param.value,
            normal_not_abnormal_for_rel_param.param.value)
        if diff_not_rel == DiffVsRel.UNKNOWN:
            sub_chooser = None
        elif diff_not_rel == DiffVsRel.DIFFERENCE:
            sub_chooser = SubChooser.difference_sub_chooser()
        elif diff_not_rel == DiffVsRel.RELATIONSHIP:
            sub_chooser = SubChooser.relationship_sub_chooser()
        else:
            raise ValueError(f"Unexpected {diff_not_rel=}")
        col_chooser = pn.Column(sub_chooser, recommendation)
        return col_chooser

def set_diff_vs_rel_param(difference_vs_relationship_value):
    difference_not_relationship_param.value = difference_vs_relationship_value

sub_chooser_or_none = pn.bind(SubChooser.get_ui, difference_vs_relationship_radio)
diff_vs_rel_param_setter = pn.bind(set_diff_vs_rel_param, difference_vs_relationship_radio)

chooser_col = pn.Column(
    pn.pane.Markdown("# Test Selection"),
    chooser_progress,
    pn.pane.Markdown("### Answer the questions below to find the best statistical test to use"),
    pn.pane.Markdown("Finding differences or relationships?"),
    difference_vs_relationship_radio,
    sub_chooser_or_none,
    diff_vs_rel_param_setter,
)
modal_stats_chooser = pn.layout.Modal(
    chooser_col,
    name='Modal',
)
modal_stats_chooser.show_close_button = True
def close_stats_chooser(_event):
    modal_stats_chooser.hide()
btn_return_to_stats_selection.on_click(close_stats_chooser)
modal_stats_chooser.css_classes = ['full-screen-modal', ]
btn_stats_chooser_stylesheet = """
.bk-btn-primary {
    font-size: 14px;
}
"""
btn_open_stats_chooser = pn.widgets.Button(name="Test Selector", button_type='primary', stylesheets=[btn_stats_chooser_stylesheet])
def open_stats_chooser(_event):
    modal_stats_chooser.show()
btn_open_stats_chooser.on_click(open_stats_chooser)
stats_need_help_style = {
    'margin-top': '20px',
    'background-color': '#F6F6F6',
    'border': '2px solid black',
    'border-radius': '5px',
    'padding': '0 5px 5px 5px',
}
stats_text = pn.pane.Markdown("### Need help choosing a test?", width_policy='max')
stats_btn_kwargs = {
    'button_type': 'primary',
    'width': 350,
}
btn_anova = pn.widgets.Button(name='ANOVA', description="ANOVA", **stats_btn_kwargs)
btn_chi_square = pn.widgets.Button(name='Chi Square', description='Chi Square', **stats_btn_kwargs)
btn_indep_ttest = pn.widgets.Button(name='Independent Samples T-Test', description='Independent Samples T-Test', **stats_btn_kwargs)
btn_kruskal_wallis = pn.widgets.Button(name='Kruskal-Wallis H', description='Kruskal-Wallis H', **stats_btn_kwargs)
btn_mann_whitney = pn.widgets.Button(name='Mann-Whitney U', description='Mann-Whitney U', **stats_btn_kwargs)
btn_normality = pn.widgets.Button(name='Normality', description='Normality', **stats_btn_kwargs)
btn_paired_ttest = pn.widgets.Button(name='Paired Samples T-Test', description='Paired Samples T-Test', **stats_btn_kwargs)
btn_pearsons = pn.widgets.Button(name="Pearson's R Correlation", description="Pearson's R Correlation", **stats_btn_kwargs)
btn_spearmans = pn.widgets.Button(name="Spearman's R Correlation", description="Spearman's R Correlation", **stats_btn_kwargs)
btn_wilcoxon = pn.widgets.Button(name='Wilcoxon Signed Ranks', description='Wilcoxon Signed Ranks', **stats_btn_kwargs)
stats_col = pn.Column(
    pn.Row(stats_text, btn_open_stats_chooser, styles=stats_need_help_style, width=800),
    pn.pane.Markdown("Select the type of test you want to run"),
    pn.Row(
        pn.Column(btn_anova, btn_chi_square, btn_indep_ttest, btn_kruskal_wallis, btn_mann_whitney),
        pn.Column(btn_normality, btn_paired_ttest, btn_pearsons, btn_spearmans, btn_wilcoxon),
    )
)
output_tabs = pn.layout.Tabs(("Charts & Tables", charts_and_tables_text), ("Stats Test", stats_col))
template = pn.template.VanillaTemplate(
    title='SOFA Stats',
    sidebar_width=750,
    sidebar=[data_col, ],
    main=[btn_data_toggle, pn.Column(output_tabs), modal_stats_chooser, ],
)
template.servable()
