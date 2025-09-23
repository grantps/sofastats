"""
Two UI areas: chooser, and selector
Within chooser, there is the big choice, and the sub-choosers.
Everything works through params which are driven by radio selections.
"""
from enum import StrEnum
import html
from pathlib import Path
from typing import Any

import pandas as pd
import panel as pn
import param
from ruamel.yaml import YAML

from sofastats.output.stats import anova

yaml = YAML(typ='safe')  ## default, if not specified, is 'rt' (round-trip)
try:
    data_label_mappings = yaml.load(Path.cwd() / 'data_labels.yaml')  ## might be a str or Path so make sure
except FileNotFoundError:
    data_label_mappings = {}

pn.extension('floatpanel')
pn.extension('tabulator')

csv_fpath = None
df_csv = pd.DataFrame()
current_output_file_path = 'current_output_file_path not set - no output open'

class Alternative(StrEnum):
    NONE = 'None'
    TRUE = 'True'
    FALSE = 'False'

class DiffVsRel(StrEnum):
    DIFFERENCE = 'Difference'
    RELATIONSHIP = 'Relationship'
    UNKNOWN = 'Not Sure'

class NumGroups(StrEnum):
    TWO = '2 Groups'
    THREE_PLUS = '3+ Groups'
    UNKNOWN = 'Not Sure'

class Normal(StrEnum):
    NORMAL = 'Normal'
    NOT_NORMAL = 'Not Normal'
    UNKNOWN = 'Not Sure'

class IndepVsPaired(StrEnum):
    INDEPENDENT = 'Independent'
    PAIRED = 'Paired'
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

STATS_CONFIGURE_LABEL = 'Configure'
OK_TICK = '✅'

class Output(StrEnum):
    """
    Make sure the value can double as a label when managed by a button (vs Radio Group)
    """
    FREQ_TABLE = 'Frequency Table'
    BAR_CHART = 'Bar Chart'
    STATS = 'Stats'

class Bool(param.Parameterized):
    value = param.Boolean(default=False)

class Choice(param.Parameterized):
    value = param.String(default=Alternative.NONE)

class Text(param.Parameterized):
    value = param.String(default=None)

## PARAMS
## stats helper
difference_not_relationship_param = Choice(value=DiffVsRel.UNKNOWN)

two_not_three_plus_groups_for_diff_param = Choice(value=NumGroups.UNKNOWN)
normal_not_abnormal_for_diff_param = Choice(value=Normal.UNKNOWN)
independent_not_paired_for_diff_param = Choice(value=IndepVsPaired.UNKNOWN)

ordinal_at_least_for_rel_param = Choice(value=OrdinalVsCategorical.UNKNOWN)
normal_not_abnormal_for_rel_param = Choice(value=Normal.UNKNOWN)

## stats selector
stats_test_param = Text(value=StatsOptions.ANOVA)

## other
give_output_tab_focus_param = Bool(value=False)
got_data_param = Bool(value=False)
html_param = Text(value='')
output_type_param = Text(value=None)
show_output_saved_msg_param = Bool(value=False)
show_stats_form_param = Bool(value=False)
show_tab_chart_form_param = Bool(value=False)

## OTHER

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
        self.data_title = pn.pane.Markdown(f"## Start here - select a CSV")
        self.file_input = pn.widgets.FileInput(accept='.csv')
        self.next_step_or_none = pn.bind(Data.next_step, self.file_input.param.filename)
        self.data_table_or_none = pn.bind(Data.display_csv, self.file_input.param.filename)

    def ui(self):
        data_column = pn.Column(
            self.data_title, self.next_step_or_none, self.file_input, self.data_table_or_none)
        return data_column

def respond_to_output_selection(event):
    """
    E.g. the user has clicked the Freq Table button
    """
    # print('respond_to_output_selection', event.obj.name)
    if event.obj.name.startswith(STATS_CONFIGURE_LABEL):
        output_type_param.value = stats_test_param.value
        show_stats_form_param.value = True
    else:
        # print(f"event.obj.name doesn't start with '{STATS_CONFIGURE_LABEL}'")
        output_type_param.value = event.obj.name  ## doubles as output type indicator e.g. Frequency Table or Bar Chart
        show_tab_chart_form_param.value = True

btn_freq_table = pn.widgets.Button(name=Output.FREQ_TABLE, description=f"Click to design your {Output.FREQ_TABLE}")
btn_bar_chart = pn.widgets.Button(name=Output.BAR_CHART, description=f"Click to design your {Output.BAR_CHART}")
btn_freq_table.on_click(respond_to_output_selection)
btn_bar_chart.on_click(respond_to_output_selection)

table_chart_col = pn.Column(btn_freq_table, btn_bar_chart)

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


class SubChooser:

    ## DIFFERENCE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @staticmethod
    def _set_indep_vs_paired_param(indep_vs_paired_value):
        # print(f"independent_not_paired_for_diff_param is now '{indep_vs_paired_value}'")
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
        # print(f"normal_not_abnormal_for_diff_param is now '{norm_vs_abnormal_value}'")
        normal_not_abnormal_for_diff_param.value = norm_vs_abnormal_value

    @staticmethod
    def _set_num_of_groups_param(num_of_groups_value):
        # print(f"two_not_three_plus_groups_for_diff_param is now '{num_of_groups_value}'")
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
        # print(f"normal_not_abnormal_for_rel_param is now '{normal_not_abnormal_for_rel_value}'")
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
        if diff_not_rel == DiffVsRel.UNKNOWN:
            sub_chooser = None
        elif diff_not_rel == DiffVsRel.DIFFERENCE:
            sub_chooser = SubChooser.difference_sub_chooser()
        elif diff_not_rel == DiffVsRel.RELATIONSHIP:
            sub_chooser = SubChooser.relationship_sub_chooser()
        else:
            raise ValueError(f"Unexpected {diff_not_rel=}")
        return sub_chooser

def set_diff_vs_rel_param(difference_vs_relationship_value):
    # print(f"difference_not_relationship_param is now '{difference_vs_relationship_value}'")
    difference_not_relationship_param.value = difference_vs_relationship_value

sub_chooser_or_none = pn.bind(SubChooser.get_ui, difference_vs_relationship_radio)
diff_vs_rel_param_setter = pn.bind(set_diff_vs_rel_param, difference_vs_relationship_radio)

chooser_col = pn.Column(
    pn.pane.Markdown("## Help Me Choose"),
    pn.pane.Markdown("### Answer the Questions Below"),
    pn.pane.Markdown("Finding differences or relationships?"),
    difference_vs_relationship_radio,
    sub_chooser_or_none,
    diff_vs_rel_param_setter,
    width=400,
)

btn_stats_test = pn.widgets.Button(name=f"{STATS_CONFIGURE_LABEL} {stats_test_param.value}",
    description=f"Click to design your {stats_test_param.value}")

btn_stats_test.on_click(respond_to_output_selection)

def get_unlabelled(possibly_labelled: Any) -> str:
    """
    e.g. 'Country (country)' => 'country'
    'NZ (1)' => '1'
    """
    try:
        if '(' in possibly_labelled:
            start_idx = possibly_labelled.rindex('(')
            unlabelled = possibly_labelled[start_idx:].lstrip('(').rstrip(')')
        else:
            unlabelled = possibly_labelled
    except TypeError as e:  ## e.g. a number
        unlabelled = possibly_labelled
    return unlabelled

def close_stats_form(_event):
    # print(f"Closing form ...")
    show_stats_form_param.value = False


class ANOVAForm:

    @staticmethod
    def var_restoration_fn_from_var_from_option(var: Any) -> Any:
        """
        E.g. If variable is country, and we extract '1' from option 'nz (1)' then we want int() to restore to 1
        If variable is name, and we extract 'Grant' from 'Grant' then str('Grant') will return (what would already have been) the correct result
        """
        dtype = dict(df_csv.dtypes.items())[var]
        if dtype in ('int64', ):
            return int
        elif dtype in ('float64', ):
            return float
        else:
            return str

    @staticmethod
    def get_measure_options() -> list[str]:
        measure_cols = []
        for name, dtype in df_csv.dtypes.items():
            has_val_labels = bool(data_label_mappings.get(name, {}).get('value_labels'))
            if dtype in ('int64', 'float64') and not has_val_labels:
                measure_cols.append(name)
        measure_options = []
        for measure_col in measure_cols:
            measure_var_lbl = data_label_mappings.get(measure_col, {}).get('variable_label')
            measure_option = f"{measure_var_lbl} ({measure_col})" if measure_var_lbl else measure_col  ## e.g. 'Height (height)'
            measure_options.append(measure_option)
        return sorted(measure_options)

    @staticmethod
    def get_grouping_options() -> list[str]:
        grouping_options = []
        for grouping_col in df_csv.columns:
            grouping_var_lbl = data_label_mappings.get(grouping_col, {}).get('variable_label')
            grouping_option = f"{grouping_var_lbl} ({grouping_col})" if grouping_var_lbl else grouping_col  ## e.g. ['Sport (sport)', ]
            grouping_options.append(grouping_option)
        return sorted(grouping_options)

    @staticmethod
    def get_value_options(grouping_variable: str) -> list[str]:
        vals = df_csv[grouping_variable].unique()
        value_label_mappings = data_label_mappings.get(grouping_variable, {}).get('value_labels', {})
        value_options = []
        for val in vals:
            val_lbl = value_label_mappings.get(val)
            val_option = f"{val_lbl} ({val})" if val_lbl else val  ## e.g. ['Archery (1)', 'Badminton (2)', 'Basketball (3)']
            value_options.append(val_option)
        return value_options

    def get_values_multiselect_or_none(self, grouping_variable_str: str):
        if not grouping_variable_str:
            return None
        value_options = ANOVAForm.get_value_options(grouping_variable_str)
        group_value_selector = pn.widgets.MultiSelect(name='Group Values',
            description='Hold down Ctrl key so you can make multiple selections',
            options=value_options,
        )
        self.group_value_selector = group_value_selector
        return group_value_selector

    def set_grouping_variable(self, grouping_variable_option: str):
        grouping_variable = get_unlabelled(grouping_variable_option)
        self.grouping_variable_var.value = grouping_variable

    def __init__(self):
        # if not df_csv.empty: print(f"I have the df LOL:\n{df_csv.head()}")
        self.user_msg_var = Text(value=None)
        self.grouping_variable_var = Text(value=None)
        self.group_value_selector = None
        self.user_msg_or_none = pn.bind(self.set_user_msg, self.user_msg_var.param.value)
        ## Measure Variable
        measure_options = ANOVAForm.get_measure_options()
        self.measure = pn.widgets.Select(name='Measure',
            description='Measure which varies between different groups ...',
            options=measure_options,
        )
        ## Grouping Variable
        grouping_options = ANOVAForm.get_grouping_options()
        self.select_grouping_variable = pn.widgets.Select(name='Grouping Variable',
            description='Variable containing the groups ...',
            options=grouping_options,
        )
        self.set_grouping_var = pn.bind(self.set_grouping_variable, self.select_grouping_variable.param.value)  ## set to a variable I can access when returning the item which goes in the template (thus making the param work)
        ## Group Values
        self.values_multiselect_or_none = pn.bind(
            self.get_values_multiselect_or_none, self.grouping_variable_var.param.value)
        ## Buttons
        self.btn_run_analysis = pn.widgets.Button(name="Get ANOVA Results")
        self.btn_run_analysis.on_click(self.run_analysis)
        self.btn_close_analysis = pn.widgets.Button(name='Close')
        self.btn_close_analysis.on_click(close_stats_form)  ## watch out - don't close form (setting form_or_none to None) without also setting un_analysis_var.value to False

    def run_analysis(self, _event):
        show_output_saved_msg_param.value = False  ## have to wait for Save Output button to be clicked again now
        ## validate
        selected_values = self.group_value_selector.value
        if len(selected_values) < 2:
            self.user_msg_var.value = ("Please select at least two grouping values "
                "so the ANOVA has enough groups to compare average values by group. "
                "Hold down the Ctrl key while making selections.")
            return
        self.user_msg_var.value = None
        grouping_variable_name = get_unlabelled(self.select_grouping_variable.value)
        var_restoration_fn = ANOVAForm.var_restoration_fn_from_var_from_option(grouping_variable_name)
        group_vals = [var_restoration_fn(get_unlabelled(val)) for val in selected_values]
        ## get HTML
        anova_design = anova.AnovaDesign(
            measure_field_name=get_unlabelled(self.measure.value),
            grouping_field_name=get_unlabelled(self.select_grouping_variable.value),
            group_values=group_vals,
            csv_file_path=csv_fpath,
            data_label_mappings=data_label_mappings,
            show_in_web_browser=False,
        )
        ## store HTML
        html_design = anova_design.to_html_design()
        html_param.value = html_design.html_item_str
        give_output_tab_focus_param.value = True
        ## store location to save output (if user wants to)
        global current_output_file_path
        current_output_file_path = anova_design.output_file_path  ## can access later if they want to save the result

    @staticmethod
    def set_user_msg(msg: str):
        if msg:
            alert = pn.pane.Alert(msg, alert_type='warning')
        else:
            alert = None
        return alert

    def ui(self):
        if show_stats_form_param.value:
            form = pn.layout.WidgetBox(
                self.user_msg_or_none,
                self.measure,
                self.select_grouping_variable, self.values_multiselect_or_none,
                self.btn_run_analysis, self.btn_close_analysis,
                self.set_grouping_var, self.group_value_selector,
                name=f"ANOVA Design", margin=20,
            )
        else:
            form = None
        return form


## form
def show_form(show_form_value: bool, stats_test_radio_value: str):
    # print('show_form', do_show_form, output_type_var.value, stats_test_str)
    if not show_form_value:
        form = None
    elif not output_type_param.value:
        form = None
    elif stats_test_param.value == StatsOptions.ANOVA:
        anova_form = ANOVAForm()
        form = anova_form.ui()
    else:
        form = None
    return form

## need to set stats test so we can dynamically change the button description - not enough to wait till a button click function checks our value - we need to do things before the button is clicked
def respond_to_stats_select(stats_test_value):
    stats_test_param.value = stats_test_value.rstrip(OK_TICK).rstrip()
    # print(f"Setting stats_test_var to {stats_test_str}")
    btn_stats_test.name = f"{STATS_CONFIGURE_LABEL} {stats_test_param.value}"
    btn_stats_test.description = f"Click to design your {stats_test_param.value}"
    show_stats_form_param.value = False  ## hide any form that is already open

def get_stats_selector(difference_not_relationship_value, two_not_three_plus_groups_for_diff_value,
        normal_not_abnormal_for_diff_value, independent_not_paired_for_diff_value, ordinal_at_least_for_rel_value,
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
            items  = [StatsOptions.CHI_SQUARE, ]
        else:
            raise Exception(F"Unexpected {ordinal_at_least_for_rel_value=}")
    else:
        raise Exception(F"Unexpected {difference_not_relationship_value=}")
    options = [f"{option} {OK_TICK}" if option in items else option for option in StatsOptions]
    stats_test_radio = pn.widgets.RadioBoxGroup(
        name='Statistical Test',
        options=options,
        inline=False)
    form_or_none = pn.bind(show_form,show_stats_form_param.param.value, stats_test_radio.param.value)
    stats_select_responder = pn.bind(respond_to_stats_select, stats_test_radio.param.value)
    return pn.Column(stats_test_radio, btn_stats_test, form_or_none, stats_select_responder)

stats_selector = pn.bind(get_stats_selector,
    difference_not_relationship_param.param.value,
    two_not_three_plus_groups_for_diff_param.param.value,
    normal_not_abnormal_for_diff_param.param.value,
    independent_not_paired_for_diff_param.param.value,
    ordinal_at_least_for_rel_param.param.value,
    normal_not_abnormal_for_rel_param.param.value,
)

selector_col = pn.Column(
    pn.pane.Markdown("## Choose a Test"),
    stats_selector,
)

stats_row = pn.Row(chooser_col, selector_col)

def save_output(_event):
    html_text = html_param.value
    with open(current_output_file_path, 'w') as f:
        f.write(html_text)
    show_output_saved_msg_param.value = True

def show_output(html_value: str, show_output_saved_msg_value):
    if html_value:
        btn_save_output = pn.widgets.Button(
            name="Save Results", description="Dave results so you can share them e.g. email as an attachment")
        btn_save_output.on_click(save_output)
        escaped_html = html.escape(html_value)
        iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'
        html_output_widget = pn.pane.HTML(iframe_html, sizing_mode='stretch_both')
        if show_output_saved_msg_value:
            saved_msg = f"Saved output to '{current_output_file_path}'"
            saved_alert = pn.pane.Alert(saved_msg, alert_type='info')
            html_col = pn.Column(btn_save_output, saved_alert, html_output_widget)
        else:
            html_col = pn.Column(btn_save_output, html_output_widget)
    else:
        html_output_widget = pn.pane.HTML('Waiting for some output to be generated ...',
            sizing_mode="stretch_both")
        html_col = pn.Column(html_output_widget)
    return html_col

html_output = pn.bind(show_output, html_param.param.value, show_output_saved_msg_param.param.value)

tabs = pn.Tabs(
    ('Data', Data().ui()),
    ('Tables & Charts', table_chart_col),
    ('Statistics', stats_row),
    ('Output', html_output),
    sizing_mode='stretch_both',
    active=0,
)

def give_output_tab_focus(give_output_tab_focus_value: bool):
    if give_output_tab_focus_value:
        tabs.active = 3

output_focus = pn.bind(give_output_tab_focus, give_output_tab_focus_param.param.value)

def allow_user_to_set_tab_focus(current_active: int):
    give_output_tab_focus_param.value = False

user_tab_focus = pn.bind(allow_user_to_set_tab_focus, tabs.param.active)

pn.template.MaterialTemplate(
    title="SOFA Stats",
    main=[tabs,
        output_focus, user_tab_focus, ],
).servable()
