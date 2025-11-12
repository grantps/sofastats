"""
c && cd ~/projects/sofastats/src/sofastats_app/ui && panel serve ui.py --static-dirs images=./images
"""
from enum import StrEnum
import html

import panel as pn

from sofastats_app.ui.conf import SIDEBAR_WIDTH, Colour, SharedKey
from sofastats_app.ui.data import Data
from sofastats_app.ui.charts_and_tables import get_charts_and_tables_main
from sofastats_app.ui.state import (data_toggle, give_output_tab_focus_param, got_data_param, html_param, shared,
                                    show_output_saved_msg_param, show_output_tab_param)
from sofastats_app.ui.stats.stats_tab import get_stats_main
from sofastats_app.ui.ui_template import ChocolateTemplate

pn.extension('modal')
pn.extension('tabulator')

class TabLabel(StrEnum):
    CHARTS_AND_TABLES = 'Charts & Tables'
    STATS_TESTS = 'Stats Tests'
    RESULTS = 'Results'

## look in main css for template used to see what controls sidebar
## https://community.retool.com/t/how-to-open-a-modal-component-in-full-screen/18720/4
css = f"""
#main {{
    border-left: solid grey 3px;
}}
.bk-tab, .bk-tab.bk-active {{
    font-size: 20px;
    color: {Colour.BLUE_MID};
}}
.alert-info {{
    font-size: 20px;
}}
#sofastats-logo {{
    width: 40px;
    margin-right: 0px;
}}
"""
pn.extension(raw_css=[css])

data_col = Data().ui()
charts_and_tables_col = get_charts_and_tables_main()
stats_col = get_stats_main()

def save_output(_event):
    html_text = html_param.value
    shared[SharedKey.CURRENT_OUTPUT_FPATH].parent.mkdir(exist_ok=True)  ## only make as required - minimise messing with user's file system
    with open(shared[SharedKey.CURRENT_OUTPUT_FPATH], 'w') as f:
        f.write(html_text)
    show_output_saved_msg_param.value = True

def show_output(html_value: str, show_output_saved_msg_value):
    if html_value:
        btn_save_output = pn.widgets.Button(
            name="Save Results", description="Save results so you can share them e.g. email as an attachment")
        btn_save_output.on_click(save_output)
        escaped_html = html.escape(html_value)
        iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'
        html_output_widget = pn.pane.HTML(iframe_html, sizing_mode='stretch_both')
        if show_output_saved_msg_value:
            saved_msg = f"Saved output to '{shared[SharedKey.CURRENT_OUTPUT_FPATH]}'"
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

def get_tabs(show_output_tab_value, give_output_tab_focus_value, got_data_value):

    if not got_data_value:
        return None

    if show_output_tab_value:
        tabs = pn.layout.Tabs(
            (TabLabel.CHARTS_AND_TABLES, charts_and_tables_col),
            (TabLabel.STATS_TESTS, stats_col),
            (TabLabel.RESULTS, html_output),
        )
    else:
        tabs = pn.layout.Tabs(
            (TabLabel.CHARTS_AND_TABLES, charts_and_tables_col),
            (TabLabel.STATS_TESTS, stats_col),
        )
    tabs.css_classes = ['bk-tabs']  ## Add the CSS class for styling

    def allow_user_to_set_tab_focus(_current_active_tab):
        give_output_tab_focus_param.value = False

    user_tab_focus = pn.bind(allow_user_to_set_tab_focus, tabs.param.active)

    if give_output_tab_focus_value:
        tabs.active = 2
    return pn.Column(tabs, user_tab_focus)

output_tabs = pn.bind(get_tabs,
    show_output_tab_param.param.value, give_output_tab_focus_param.param.value, got_data_param.param.value)

def get_btn_data_toggle(got_data_value):
    if not got_data_value:
        return None
    btn_data_toggle = pn.widgets.Button(  ## seems like we must define in same place as you are watching it
        icon="arrow-big-left", #"images/left_arrow.svg",
        name="Close Data Window",
        button_type="light", button_style='solid',
        styles={
            'margin-top': '-5px', 'margin-right': '20px', 'margin-bottom': '5px', 'margin-left': '-20px',
            'border': '2px solid grey',
            'border-radius': '5px',
        })

    @pn.depends(btn_data_toggle, watch=True)
    def _update_main(_):
        data_toggle.value = not data_toggle.value

        if not data_toggle.value:
            btn_data_toggle.icon = "arrow-big-right"
            btn_data_toggle.name = "Open Data Window"
        else:
            btn_data_toggle.icon = "arrow-big-left"
            btn_data_toggle.name = "Close Data Window"

    return btn_data_toggle

btn_data_toggle_or_none = pn.bind(get_btn_data_toggle, got_data_param.param.value)

ChocolateTemplate(
    title="SOFA Stats - no sweat stats!",
    sidebar_width=SIDEBAR_WIDTH,
    sidebar=[data_col, ],
    main=[btn_data_toggle_or_none, data_toggle, output_tabs, ],
    local_logo_url='bunny_head_small.svg',
).servable()
