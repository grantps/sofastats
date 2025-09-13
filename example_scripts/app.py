"""
Ben - instructions:

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
"""
from enum import StrEnum

import panel as pn
import param

from sofastats.conf.images import FREQ_TABLE

pn.extension('floatpanel')
pn.extension('tabulator')

class Output(StrEnum):
    """
    Double as both output indicator and label (name) for button
    """
    FREQ_TABLE = 'Frequency Table'
    BAR_CHART = 'Bar Chart'
    ANOVA = 'ANOVA'

class Fields(StrEnum):
    MEASURE = 'measure'
    GROUPING_VARIABLE = 'grouping_variable'
    VARIABLE_A = 'variable_a'
    VARIABLE_B = 'variable_b'
    VALUE_A = 'value_a'
    VALUE_B = 'value_b'

fields_by_output_type = {
    Output.FREQ_TABLE: (Fields.VARIABLE_A, ),
    Output.BAR_CHART: (Fields.VARIABLE_A, Fields.VARIABLE_B),
    Output.ANOVA: (Fields.MEASURE, Fields.GROUPING_VARIABLE, Fields.VALUE_A, Fields.VALUE_B),
}

class Bool(param.Parameterized):
    value = param.Boolean(default=False)

class Text(param.Parameterized):
    value = param.String(default=None)

class DC(param.Parameterized):
    value = param.DataFrame(default=None)

## trigger variables (other things are bound to these)
output_type_var = Text(value=None)
show_form_var = Bool(value=False)

def close_form(event):
    print(f"Closing form ...")
    show_form_var.value = False


class ANOVAForm:

    def __init__(self):
        self.text_measure = pn.widgets.TextInput(name='Measure',
            placeholder='Measure which varies between different groups ...', width=500)
        self.grouping_variable = pn.widgets.TextInput(name='Grouping Variable',
            placeholder='Variable containing the groups ...', width=500)
        self.grouping_value_a = pn.widgets.TextInput(name='Grouping Value A',
            placeholder='First value in group variable ...', width=500)
        self.grouping_value_b = pn.widgets.TextInput(name='Grouping Value B',
            placeholder='Last value in group variable ...', width=500)
        self.btn_run_analysis = pn.widgets.Button(name="Get ANOVA Results")
        self.btn_run_analysis.on_click(self.run_analysis)
        self.btn_close_analysis = pn.widgets.Button(name='Close')
        self.btn_close_analysis.on_click(close_form)  ## watch out - don't close form (setting form_or_none to None) without also setting un_analysis_var.value to False

    def run_analysis(self, event):
        print(self.text_measure)

    def ui(self):
        if show_form_var.value:
            config = {"headerControls": {"close": "remove"}}
            form = pn.layout.FloatPanel(
                self.text_measure,
                self.grouping_variable, self.grouping_value_a, self.grouping_value_b,
                self.btn_run_analysis, self.btn_close_analysis,
                name=f"ANOVA Design", margin=20, height=600,
                contained=False, position='center', config=config,
            )
        else:
            form = None
        return form


def show_form(do_show_form: bool, output_type_str: str):
    print(f"{do_show_form=}; {output_type_str=}")
    if not do_show_form:
        form = None
    elif not output_type_str:
        form = None
    elif output_type_str == Output.ANOVA:
        print('ANOVA form!')
        anova_form = ANOVAForm()
        form = anova_form.ui()
    else:
        form = None
    return form

form_or_none = pn.bind(show_form,show_form_var.param.value, output_type_var.param.value)

def set_output_var(event):
    output_type_var.value = event.obj.name  ## doubles as output type indicator e.g. ANOVA or Frequency Table
    print(f"{event.obj.name} button set param output_type_var to '{output_type_var.value}'")
    show_form_var.value = True
    print(f"{event.obj.name} button also set param show_form_var to True")

btn_freq_table = pn.widgets.Button(name=Output.FREQ_TABLE, description=f"Click to design your {Output.FREQ_TABLE}")
btn_bar_chart = pn.widgets.Button(name=Output.BAR_CHART, description=f"Click to design your {Output.BAR_CHART}")
btn_anova = pn.widgets.Button(name=Output.ANOVA, description=f"Click to design your {Output.ANOVA}")

btn_freq_table.on_click(set_output_var)
btn_bar_chart.on_click(set_output_var)
btn_anova.on_click(set_output_var)

tabs = pn.Tabs(
    ('Tables', btn_freq_table),
    ('Charts', btn_bar_chart),
    ('Statistics', btn_anova),
)

pn.template.MaterialTemplate(
    title="SOFA Stats",
    main=[tabs, form_or_none, ],
).servable()
