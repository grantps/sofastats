"""
Stats form, stats chooser, and stats config

Using nested modals.
Upper modals and buttons opening and closing them must be defined inside lower modals.
"""
import panel as pn

from stats_chooser import get_stats_chooser_modal

pn.extension('modal')

def get_stats_main():
    stats_need_help_style = {
        'margin-top': '20px',
        'background-color': '#F6F6F6',
        'border': '2px solid black',
        'border-radius': '5px',
        'padding': '0 5px 5px 5px',
    }
    stats_text = pn.pane.Markdown("### Need help choosing a test?", width_policy='max')
    stats_chooser_modal = get_stats_chooser_modal()
    btn_open_stats_chooser = pn.widgets.Button(name="Test Selector")
    def open_stats_chooser(_event):
        stats_chooser_modal.show()
    btn_open_stats_chooser.on_click(open_stats_chooser)
    get_help_row = pn.Row(stats_text, btn_open_stats_chooser, styles=stats_need_help_style, width=800)
    return pn.Column(get_help_row, stats_chooser_modal, )
