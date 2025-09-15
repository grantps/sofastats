"""
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

import pandas as pd
import panel as pn
import param

from sofastats.output.stats import anova

pn.extension('floatpanel')
pn.extension('tabulator')

df_csv = pd.DataFrame()

class Output(StrEnum):
    """
    Make sure the value can double as a label
    """
    FREQ_TABLE = 'Frequency Table'
    BAR_CHART = 'Bar Chart'
    ANOVA = 'ANOVA'
    CHI_SQUARE = 'Chi Square'

class Bool(param.Parameterized):
    value = param.Boolean(default=False)

class Text(param.Parameterized):
    value = param.String(default=None)

class DC(param.Parameterized):
    value = param.DataFrame(default=None)

class Int(param.Parameterized):
    value = param.Integer(default=0)

## trigger variables (other things are bound to these)
output_type_var = Text(value=None)
stats_test_var = Text(value='ANOVA')
show_form_var = Bool(value=False)
show_df_var = Bool(value=False)
html_var = Text(value='')
give_output_tab_focus_var = Bool(value=False)


class Data:

    def __init__(self):
        self.data_title = pn.pane.Markdown(f"## Start here - select a CSV")
        self.file_input = pn.widgets.FileInput(accept='.csv')
        self.next_step_or_none = pn.bind(self.next_step, self.file_input.param.filename)
        self.data_table_or_none = pn.bind(self.display_csv, self.file_input.param.filename)

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
            df = pd.read_csv(selected_csv_fpath)
            global df_csv
            df_csv = df.copy()
            table_df = pn.widgets.Tabulator(df, page_size=10, disabled=True)
            table_df.value = df
            return table_df
        else:
            return None

    def ui(self):
        data_column = pn.Column(
            self.data_title, self.next_step_or_none, self.file_input, self.data_table_or_none)
        return data_column


def close_form(event):
    print(f"Closing form ...")
    show_form_var.value = False


class ANOVAForm:

    def __init__(self):
        self.user_msg_var = Text(value=None)
        self.user_msg_or_none = pn.bind(self.set_user_msg, self.user_msg_var.param.value)
        self.measure = pn.widgets.Select(name='Measure',
            description='Measure which varies between different groups ...',
            options=['Height (height)'],
        )
        # if not df_csv.empty: print(f"I have the df LOL:\n{df_csv.head()}")

        self.grouping_variable = pn.widgets.Select(name='Grouping Variable',
            description='Variable containing the groups ...',
            options=['Sport (sport)', ],
        )
        ## TODO: make values available dynamic depending on grouping variable
        self.grouping_values = pn.widgets.MultiSelect(name='Grouping Values',
            description='Hold down Ctrl key so you can make multiple selections',
            options=['Archery (1)', 'Badminton (2)', 'Basketball (3)'],
        )
        self.btn_run_analysis = pn.widgets.Button(name="Get ANOVA Results")
        self.btn_run_analysis.on_click(self.run_analysis)
        self.btn_close_analysis = pn.widgets.Button(name='Close')
        self.btn_close_analysis.on_click(close_form)  ## watch out - don't close form (setting form_or_none to None) without also setting un_analysis_var.value to False

    def run_analysis(self, event):
        ## validate
        selected_values = self.grouping_values.value
        if len(selected_values) < 2:
            self.user_msg_var.value = ("Please select at least two grouping values "
                "so the ANOVA has enough groups to compare average values by group. "
                "Hold down the Ctrl key while making selections.")
            return
        self.user_msg_var.value = None
        group_vals = [int(val[val.index('(')+1: val.index(')')]) for val in selected_values]
        ## get HTML
        html_design = anova.AnovaDesign(
            measure_field_name='height',
            grouping_field_name='sport',
            group_values=group_vals,
            csv_file_path='sports.csv',
            data_label_mappings={
                'country': {
                    'variable_label': 'Country',
                    'variable_comment': 'Only the countries in the tournament',
                    'value_labels': {
                        1: 'USA',
                        2: 'South Korea',
                        3: 'NZ',
                        4: 'Denmark',
                    },
                },
                'sport': {
                    'variable_label': 'Sport',
                    'variable_comment': 'Only the sports in the tournament',
                    'value_labels': {
                        1: 'Archery',
                        2: 'Badminton',
                        3: 'Basketball',
                    },
                },
            },
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
                self.grouping_variable, self.grouping_values,
                self.btn_run_analysis, self.btn_close_analysis,
                name=f"ANOVA Design", margin=20,
            )
        else:
            form = None
        return form


def show_form(do_show_form: bool, output_type_str: str):
    if not do_show_form:
        form = None
    elif not output_type_str:
        form = None
    elif output_type_str == Output.ANOVA:
        anova_form = ANOVAForm()
        form = anova_form.ui()
    else:
        form = None
    return form

def respond_to_output_selection(event):
    """
    E.g. the user has clicked the Freq Table button
    """
    output_type_var.value = event.obj.name  ## doubles as output type indicator e.g. ANOVA or Frequency Table
    show_form_var.value = True

def show_output(raw_html_to_display: str):
    if raw_html_to_display:
        escaped_html = html.escape(raw_html_to_display)
        iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'
        html_output_widget = pn.pane.HTML(iframe_html, sizing_mode='stretch_both')
    else:
        html_output_widget = pn.pane.HTML('Waiting for some output to be generated ...',
            sizing_mode="stretch_both")
    return html_output_widget

form_or_none = pn.bind(show_form,show_form_var.param.value, output_type_var.param.value)

data = Data()
data_col = data.ui()

btn_freq_table = pn.widgets.Button(name=Output.FREQ_TABLE, description=f"Click to design your {Output.FREQ_TABLE}")
btn_bar_chart = pn.widgets.Button(name=Output.BAR_CHART, description=f"Click to design your {Output.BAR_CHART}")
stats_test_radio_group = pn.widgets.RadioBoxGroup(
    name='Statistical Test',
    options=[
        'ANOVA',
        'Chi Square',
        'Kruskal-Wallis H',
        'Mann-Whitney U',
        "Pearson's R Correlation",
        "Spearman's R Correlation",
        'Independent Samples T-Test',
        'Paired Samples T-Test',
        'Wilcoxon Signed Ranks',
    ],
    inline=False)

def set_stats_output(stats_val):
    print(f"{stats_val=}")
    stats_test_var.value = stats_val

bum = pn.bind(set_stats_output, stats_test_radio_group.param.value)

btn_stats_test = pn.widgets.Button(name='Configure Test', description=f"Click to design your {stats_test_var.value}")

btn_freq_table.on_click(respond_to_output_selection)
btn_bar_chart.on_click(respond_to_output_selection)
btn_stats_test.on_click(respond_to_output_selection)

table_chart_col = pn.Column(btn_freq_table, btn_bar_chart)
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

def give_output_tab_focus(do_give_output_tab_focus: bool):
    if do_give_output_tab_focus:
        tabs.active = 3

output_focus = pn.bind(give_output_tab_focus, give_output_tab_focus_var.param.value)

def allow_user_to_set_tab_focus(current_active: int):
    give_output_tab_focus_var.value = False

user_tab_focus = pn.bind(allow_user_to_set_tab_focus, tabs.param.active)

pn.template.MaterialTemplate(
    title="SOFA Stats",
    main=[tabs, output_focus, user_tab_focus, bum, ],
).servable()
