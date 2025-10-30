"""
Stats form, stats chooser, and stats config

Using nested modals.
Upper modals and buttons opening and closing them must be defined inside lower modals.
"""
from bokeh.models import Tooltip
from bokeh.models.dom import HTML
import panel as pn

from sofastats.ui.conf import Colour, StatsOption
from sofastats.ui.stats.stats_chooser import get_stats_chooser_modal
from sofastats.ui.stats.stats_config import get_stats_config_modal

pn.extension('modal')

css = f"""
.bk-panel-models-widgets-TooltipIcon {{
    padding: 2px 3px 2px 0;
    margin: -4px 10px 0 0;
    background-color: #e1e1e1;
    border-radius: 0 3px 3px 0;
}}
.bk-panel-models-widgets-TooltipIcon:hover,
.bk-panel-models-widgets-TooltipIcon:focus,
.bk-panel-models-widgets-TooltipIcon:active 
{{
    background-color: {Colour.BLUE_MID};
}}"""
pn.extension(raw_css=[css])

def get_html_tooltip(html_content: str, *, width: int, horizontal_offset: int, vertical_offset: int,
        extra_div_styles: dict[str, str] | None = None, show_arrow=False) -> Tooltip:
    """
    offsets: WARNING - if horizontal_offset and vertical_offset result in the tooltip overlapping the button
      then you will never see it because the mouse being over the top makes it go away.
      No defaults supplied because it is a custom question depending on width and height of button.
    """
    div_styles = {'width': f'{width}px', 'background-color': 'transparent', }
    extra_div_styles = extra_div_styles if extra_div_styles else {}
    div_styles.update(extra_div_styles)
    tooltip = Tooltip(
        content=HTML(html=html_content),
        position=(horizontal_offset, vertical_offset),
        attachment='below',  ## TooltipAttachment enum has values
        show_arrow=show_arrow,
        styles=div_styles,
        interactive=True, closable=True,
    )
    return tooltip

def get_stats_main():
    servables = pn.Column()
    stats_need_help_style = {
        'margin-top': '20px',
        'background-color': '#F6F6F6',
        'border': '2px solid black',
        'border-radius': '5px',
        'padding': '0 5px 5px 5px',
    }
    stats_text = pn.pane.Markdown(
        "### Need help choosing a test?", width_policy='max', styles={'color': Colour.BLUE_MID, 'font-size': '16px'})
    stats_chooser_modal = get_stats_chooser_modal()
    btn_open_stats_chooser_styles = {
        'margin-top': '10px',
    }
    ## https://panel.holoviz.org/how_to/styling/apply_css.html
    btn_test_selector_stylesheet = """
    :host(.solid) .bk-btn.bk-btn-primary {
      font-size: 16px;
    }
    """
    btn_open_stats_chooser = pn.widgets.Button(name="Test Selector", button_type='primary',
        styles=btn_open_stats_chooser_styles, stylesheets=[btn_test_selector_stylesheet, ])
    def open_stats_chooser(_event):
        stats_chooser_modal.show()
    btn_open_stats_chooser.on_click(open_stats_chooser)
    get_help_row = pn.Row(stats_text, btn_open_stats_chooser, styles=stats_need_help_style, width=800)

    STATS_BTN_WIDTH = 190
    STATS_BTN_HEIGHT = 27

    stats_btn_kwargs = {
        'button_type': 'primary',
        'width': STATS_BTN_WIDTH,
        'height': STATS_BTN_HEIGHT,
    }

    tool_tip_icon_kwargs = {
        'width': STATS_BTN_WIDTH - 15,
        'horizontal_offset': -180,
    }

    anova_html = """\
    <div>
        <div style="float: left; width: 50%">
            <p style="font-size: 16px; margin-top: 0; font-weight: bold;">ANOVA (Analysis Of Variance)</p>
            <p>The ANOVA (Analysis Of Variance) is good for seeing if there is a difference in means between multiple groups
            when the data is numerical and adequately normal. Generally the ANOVA is robust to non-normality.
            You can evaluate normality by clicking on the "Normality" button (under construction).
            The Kruskal-Wallis H may be preferable if your data is not adequately normal.</p>
        </div>
        <div style="float: left; width: 50%">
            <img src="images/bunny_head_small.svg" alt="Bunny logo" style="width: 50px; margin-left: 20px;"></img>
        </div>
    </div>"""
    chi_square_html = """\
    <h1>Chi Square Test</h1>
    <p>The Chi Square test is one of the most widely used tests in social science.
    It is good for seeing if the results for two variables are independent or related.
    Is there a relationship between gender and income group for example?</p>
    <img src="images/bunny_head_small.svg" alt="Bunny logo" width=50px></img
    """
    under_construction_html = """\
    <h1>Under Construction</h1>
    """
    btn_margins = (0, 0, 5, 0)
    tip_margins = (-9, 0, 0, 20)
    btn_anova = pn.widgets.Button(name='ANOVA', **stats_btn_kwargs, margin=btn_margins)
    anova_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(anova_html,
        horizontal_offset=195, vertical_offset=125, width=775), margin=tip_margins)
    btn_chi_square = pn.widgets.Button(name='Chi Square', description='Chi Square', **stats_btn_kwargs, margin=btn_margins)
    chi_square_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(chi_square_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_indep_ttest = pn.widgets.Button(name='Independent Samples T-Test', **stats_btn_kwargs, margin=btn_margins)
    indep_ttest_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_kruskal_wallis = pn.widgets.Button(name='Kruskal-Wallis H', **stats_btn_kwargs, margin=btn_margins)
    kruskal_wallis_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_mann_whitney = pn.widgets.Button(name='Mann-Whitney U', **stats_btn_kwargs, margin=btn_margins)
    mann_whitney_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_normality = pn.widgets.Button(name='Normality', **stats_btn_kwargs, margin=btn_margins)
    normality_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_paired_ttest = pn.widgets.Button(name='Paired Samples T-Test', **stats_btn_kwargs, margin=btn_margins)
    paired_ttest_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_pearsons = pn.widgets.Button(name="Pearson's R Correlation", **stats_btn_kwargs, margin=btn_margins)
    pearsons_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_spearmans = pn.widgets.Button(name="Spearman's R Correlation", **stats_btn_kwargs, margin=btn_margins)
    spearmans_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_wilcoxon = pn.widgets.Button(name='Wilcoxon Signed Ranks', **stats_btn_kwargs, margin=btn_margins)
    wilcoxon_tip = pn.widgets.TooltipIcon(value=get_html_tooltip(under_construction_html,
        vertical_offset=-20, **tool_tip_icon_kwargs), margin=tip_margins)
    btn_close = pn.widgets.Button(name="Close")
    def open_anova_config(_event):
        stats_config_modal = get_stats_config_modal(StatsOption.ANOVA, btn_close)
        servables.append(stats_config_modal)
        stats_config_modal.show()
        def close_config_modal(_event):
            stats_config_modal.hide()
        btn_close.on_click(close_config_modal)
    btn_anova.on_click(open_anova_config)
    def test_under_construction(event):
        stats_config_modal = pn.layout.Modal(pn.pane.Markdown(f"{event.obj.name} under construction"))
        servables.append(stats_config_modal)
        stats_config_modal.show()
    btn_chi_square.on_click(test_under_construction)
    btn_indep_ttest.on_click(test_under_construction)
    btn_kruskal_wallis.on_click(test_under_construction)
    btn_mann_whitney.on_click(test_under_construction)
    btn_normality.on_click(test_under_construction)
    btn_paired_ttest.on_click(test_under_construction)
    btn_pearsons.on_click(test_under_construction)
    btn_spearmans.on_click(test_under_construction)
    btn_wilcoxon.on_click(test_under_construction)

    stats_col = pn.Column(
        get_help_row,
        pn.pane.Markdown(
            "### Select the type of test you want to run",
            styles={'margin-top': '0px', 'margin-bottom': '0px', 'color': Colour.BLUE_MID, 'font-size': '16px'}),
        pn.Row(
            pn.Column(
                pn.Row(btn_anova, anova_tip),
                pn.Row(btn_chi_square, chi_square_tip),
                pn.Row(btn_indep_ttest, indep_ttest_tip),
                pn.Row(btn_kruskal_wallis, kruskal_wallis_tip),
            ),
            pn.Column(
                pn.Row(btn_mann_whitney, mann_whitney_tip),
                pn.Row(btn_normality, normality_tip),
                pn.Row(btn_paired_ttest, paired_ttest_tip),
                pn.Row(btn_pearsons, pearsons_tip),
            ),
            pn.Column(
                pn.Row(btn_spearmans, spearmans_tip),
                pn.Row(btn_wilcoxon, wilcoxon_tip),
            ),
        ),
        servables,
    )
    return pn.Column(stats_col, stats_chooser_modal, )
