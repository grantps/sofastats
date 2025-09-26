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
from pathlib import Path

import pandas as pd
import panel as pn
import param
from ruamel.yaml import YAML

pn.extension('tabulator')

## look in main css for template used to see what controls sidebar
css = """
#main {
    border-left: solid grey 3px;
}
"""
pn.extension(raw_css=[css])

yaml = YAML(typ='safe')  ## default, if not specified, is 'rt' (round-trip)
try:
    data_label_mappings = yaml.load(Path.cwd() / 'data_labels.yaml')  ## might be a str or Path so make sure
except FileNotFoundError:
    data_label_mappings = {}

class Bool(param.Parameterized):
    value = param.Boolean(default=False)

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
        # btn_data_toggle.styles.borderRight = "solid 10px green"

charts_and_tables_text = pn.pane.Markdown("Charts & Tables")
stats_text = pn.pane.Markdown("Stats Tests")
output_tabs = pn.layout.Tabs(("Charts & Tables", charts_and_tables_text), ("Stats Test", stats_text))
template = pn.template.VanillaTemplate(
    title='SOFA Stats',
    sidebar=[data_col, ],
    sidebar_width=750,
    main=[btn_data_toggle, pn.Column(output_tabs)]
)
template.servable()
