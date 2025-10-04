"""
c && cd ~/projects/sofastats/example_scripts/ && panel serve --dev ui.py
TODO: actually run analysis and display it in output tab
"""
import panel as pn

from data import Data
from charts_and_tables import get_charts_and_tables_main
from state import data_toggle
from stats import get_stats_main

pn.extension('modal')
pn.extension('tabulator')

## look in main css for template used to see what controls sidebar
## https://community.retool.com/t/how-to-open-a-modal-component-in-full-screen/18720/4
css = """
#main {
    border-left: solid grey 3px;
}
"""
pn.extension(raw_css=[css])

data_col = Data().ui()
charts_and_tables_col = get_charts_and_tables_main()
stats_col = get_stats_main()
output_tabs = pn.layout.Tabs(("Charts & Tables", charts_and_tables_col), ("Stats Test", stats_col))

btn_data_toggle = pn.widgets.Button(  ## seems like we must define in same place as you are watching it
    name="🞀 Close Data Window",
    description="Close uploaded data window",
    button_type="light", button_style='solid',
    styles={
        'margin-left': '-20px', 'margin-bottom': '20px',
        'border': '2px solid grey',
        'border-radius': '5px',
    })

@pn.depends(btn_data_toggle, watch=True)
def _update_main(_):
    data_toggle.value = not data_toggle.value

    if not data_toggle.value:
        btn_data_toggle.name = "Open Data Window 🞂"
        btn_data_toggle.description = "See your uploaded data again"
    else:
        btn_data_toggle.name = "🞀 Close Data Window"
        btn_data_toggle.description = "Close uploaded data window"


pn.template.VanillaTemplate(
    title='SOFA Stats',
    sidebar_width=750,
    sidebar=[data_col, ],
    main=[btn_data_toggle, output_tabs, ],
).servable()
