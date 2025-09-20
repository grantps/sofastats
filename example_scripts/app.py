"""
TODO: scrollbar for wide CSV tables
TODO: warning that only CSVs in same folder can be used
TODO: show messages only in other tabs if data CSV not selected
TODO: close open forms if data CSV changed

Longer-term:
TODO (for UX testing): ANOVA complete; maybe another layout
TODO: generate Forms from dataclass requirements; add all other buttons;

panel serve app.py --dev

Program logic of panel apps:

Script runs once and once only - not rerun each time there is an event or a parameter change.
So top to bottom at the beginning only like all Python scripts. Nothing funky. Phew!
Variables defined earlier are not changed by events or widget changes UNLESS they are parameterised.
The script defines initial variables, parameterised variables, and functions.
Functions defined to be called when:
* events occur (button clicks usually).
  These will do something e.g. run some calculations, interact with a database etc.
  Usually they will return a value.
  Typically, this value will be set in a parameterised variable and trigger change in a bound UI item
  e.g. markdown will display a result or feedback
* state changes (typically the state connected to UI widgets - e.g. a slider slides).
  These changes will typically change other UI items e.g. display a number matching the position of a slider.

Three tabs: Data, Tables & Charts, Statistical Tests
Data: a button for finding and then loading a DF (first dozen rows only)
Tables & Charts: a button for a Freq Table and for a simple Bar Chart
Statistical Tests: ANOVA

For "Tables & Charts" and "Statistical Tests" we want a form to pop open with a "Run Analysis" button
which reads the values entered in the form. A close button should make a form disappear.

Opening or closing a form should set a parameterised variable that is bound to the show_form function.
Bound functions should return a widget OR None. Bound functions should be about UI.
Sometimes we need to bind to something to change the value of a parameterised variable and thus a UI item.
Note - a binding is a function which will only be triggered if the function is made servable
e.g. by being supplied to a template.
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

STATS_CONFIGURE_LABEL = 'Configure'

class Output(StrEnum):
    """
    Make sure the value can double as a label when managed by a button (vs Radio Group)
    """
    FREQ_TABLE = 'Frequency Table'
    BAR_CHART = 'Bar Chart'
    STATS = 'Stats'

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

class DC(param.Parameterized):
    value = param.DataFrame(default=None)

class Int(param.Parameterized):
    value = param.Integer(default=0)

class Text(param.Parameterized):
    value = param.String(default=None)

## trigger variables (other things are bound to these)
got_data_var = Bool(value=False)
output_type_var = Text(value=None)
stats_test_var = Text(value=StatsOptions.ANOVA)

show_form_var = Bool(value=False)
show_df_var = Bool(value=False)
html_var = Text(value='')
give_output_tab_focus_var = Bool(value=False)


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
            got_data_var.value = True
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


def close_form(event):
    print(f"Closing form ...")
    show_form_var.value = False

def get_unlabelled(possibly_labelled: str) -> str:
    """
    e.g. 'Country (country)' => 'country'
    'NZ (1)' => '1'
    """
    if '(' in possibly_labelled:
        start_idx = possibly_labelled.rindex('(')
        unlabelled = possibly_labelled[start_idx:].lstrip('(').rstrip(')')
    else:
        unlabelled = possibly_labelled
    return unlabelled


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
        self.btn_close_analysis.on_click(close_form)  ## watch out - don't close form (setting form_or_none to None) without also setting un_analysis_var.value to False

    def run_analysis(self, event):
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
        html_design = anova.AnovaDesign(
            measure_field_name=get_unlabelled(self.measure.value),
            grouping_field_name=get_unlabelled(self.select_grouping_variable.value),
            group_values=group_vals,
            csv_file_path=csv_fpath,
            data_label_mappings=data_label_mappings,
            show_in_web_browser=False,
        ).to_html_design()
        ## store HTML
        html_var.value = html_design.html_item_str
        give_output_tab_focus_var.value = True

    @staticmethod
    def set_user_msg(msg: str):
        if msg:
            alert = pn.pane.Alert(msg, alert_type='warning')
        else:
            alert = None
        return alert

    def ui(self):
        if show_form_var.value:
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


data = Data()
data_col = data.ui()

btn_freq_table = pn.widgets.Button(name=Output.FREQ_TABLE, description=f"Click to design your {Output.FREQ_TABLE}")
btn_bar_chart = pn.widgets.Button(name=Output.BAR_CHART, description=f"Click to design your {Output.BAR_CHART}")
stats_test_radio_group = pn.widgets.RadioBoxGroup(
    name='Statistical Test',
    options=[
        StatsOptions.ANOVA,
        StatsOptions.CHI_SQUARE,
        StatsOptions.KRUSKAL_WALLIS,
        StatsOptions.MANN_WHITNEY,
        StatsOptions.PEARSONS,
        StatsOptions.SPEARMANS,
        StatsOptions.TTEST_INDEP,
        StatsOptions.TTEST_PAIRED,
        StatsOptions.WILCOXON,
    ],
    inline=False)

btn_stats_test = pn.widgets.Button(
    name=f"{STATS_CONFIGURE_LABEL} {stats_test_var.value}", description=f"Click to design your {stats_test_var.value}")

def respond_to_output_selection(event):
    """
    E.g. the user has clicked the Freq Table button
    """
    # print('respond_to_output_selection', event.obj.name)
    if event.obj.name.startswith(STATS_CONFIGURE_LABEL):
        output_type_var.value = stats_test_var.value
    else:
        # print(f"event.obj.name doesn't start with '{STATS_CONFIGURE_LABEL}'")
        output_type_var.value = event.obj.name  ## doubles as output type indicator e.g. Frequency Table or Bar Chart
    show_form_var.value = True

btn_freq_table.on_click(respond_to_output_selection)
btn_bar_chart.on_click(respond_to_output_selection)
btn_stats_test.on_click(respond_to_output_selection)

table_chart_col = pn.Column(btn_freq_table, btn_bar_chart)

def give_output_tab_focus(do_give_output_tab_focus: bool):
    if do_give_output_tab_focus:
        tabs.active = 3

## need to set stats test so we can dynamically change the button description - not enough to wait till a button click function checks our value - we need to do things before the button is clicked
def respond_to_stats_select(stats_test_str):
    stats_test_var.value = stats_test_str
    # print(f"Setting stats_test_var to {stats_test_str}")
    btn_stats_test.name = f"{STATS_CONFIGURE_LABEL} {stats_test_var.value}"
    btn_stats_test.description = f"Click to design your {stats_test_var.value}"
    show_form_var.value = False  ## hide any form that is already open

stats_setting = pn.bind(respond_to_stats_select, stats_test_radio_group.param.value)

## form
def show_form(do_show_form: bool, stats_test_str: str):
    # print('show_form', do_show_form, output_type_var.value, stats_test_str)
    if not do_show_form:
        form = None
    elif not output_type_var.value:
        form = None
    elif stats_test_var.value == StatsOptions.ANOVA:
        anova_form = ANOVAForm()
        form = anova_form.ui()
    else:
        form = None
    return form

def show_output(raw_html_to_display: str):
    if raw_html_to_display:
        escaped_html = html.escape(raw_html_to_display)
        iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'
        html_output_widget = pn.pane.HTML(iframe_html, sizing_mode='stretch_both')
    else:
        html_output_widget = pn.pane.HTML('Waiting for some output to be generated ...',
            sizing_mode="stretch_both")
    return html_output_widget

form_or_none = pn.bind(show_form,show_form_var.param.value, stats_test_radio_group.param.value)

stats_col = pn.Column(stats_test_radio_group, btn_stats_test, form_or_none)

html_output = pn.bind(show_output, html_var.param.value)

tabs = pn.Tabs(
    ('Data', Data().ui()),
    ('Tables & Charts', table_chart_col),
    ('Statistics', stats_col),
    ('Output', html_output),
    sizing_mode='stretch_both',
    active=0,
)

output_focus = pn.bind(give_output_tab_focus, give_output_tab_focus_var.param.value)

def allow_user_to_set_tab_focus(current_active: int):
    give_output_tab_focus_var.value = False

user_tab_focus = pn.bind(allow_user_to_set_tab_focus, tabs.param.active)

pn.template.MaterialTemplate(
    title="SOFA Stats",
    main=[tabs,
        output_focus, user_tab_focus, stats_setting, ],
).servable()
