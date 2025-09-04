from pathlib import Path

import pandas as pd
import panel as pn

pn.extension('floatpanel')
pn.extension('tabulator')

N_CSV_ROWS = 12

from sofastats.conf.images import (AREA_CHART, BAR_SIMPLE, CROSS_TAB, FREQ_TABLE, PIE_CHART)


class Gui:

    @staticmethod
    def close(event):
        print(Gui.w1.value)
        Gui.form.destroy()

    @staticmethod
    def make_chart(event):
        print("Made chart!")

    @staticmethod
    def on_button_click(event):
        print(f"{event.obj.description} clicked :-)")
        Gui.w1 = pn.widgets.TextInput(name='Measure:')
        w2 = pn.widgets.TextInput(name='Variable A:')
        w3 = pn.widgets.TextInput(name='Variable B:')
        btn_close = pn.widgets.Button(name='Close')
        btn_close.on_click(Gui.close)
        btn_make_chart = pn.widgets.Button(name='Make Chart')
        btn_make_chart.on_click(Gui.make_chart)
        Gui.form = pn.layout.FloatPanel(Gui.w1, w2, w3, btn_close, btn_make_chart,
            name='Design', margin=20, height=600, contained=False, position='center')
        Gui.form.servable()

    def __init__(self):
        ## Data *****************************************************************
        data_title = pn.pane.Markdown(f"## Select a CSV to see the first {N_CSV_ROWS} rows")
        self.file_input = pn.widgets.FileInput(accept='.csv')
        self.file_input.param.watch(self.display_csv, 'value')
        df = pd.DataFrame()
        self.tab_df = pn.widgets.Tabulator(df, disabled=True)
        self.tab_df.visible = False
        data_col = pn.Column(data_title, self.file_input, self.tab_df)
        ## Tables *****************************************************************
        table_title = pn.pane.Markdown(f"## Tables")
        ## Cross-Tab
        button_cross_tab_stylesheet = f"""
        :host {{
            background-image: url("{CROSS_TAB}");
            background-repeat: no-repeat;
            width: 516px;
            height: 152px;
            --primary-color: None;
            border: #cdcdcd solid 5px;
            border-radius: 6px;
        }}
        """
        cross_tab_title = pn.pane.Markdown(f"## Cross-Tab (click to design)")
        cross_tab_btn = pn.widgets.Button(
            description='Cross-Tab Table', button_type='primary', stylesheets=[button_cross_tab_stylesheet])
        cross_tab_btn.on_click(Gui.on_button_click)
        cross_tab_col = pn.Column(cross_tab_title, cross_tab_btn)
        ## Frequency Table
        button_frequency_table_stylesheet = f"""
        :host {{
            background-image: url("{FREQ_TABLE}");
            background-repeat: no-repeat;
            width: 329px;
            height: 126px;
            --primary-color: None;
            border: #cdcdcd solid 5px;
            border-radius: 6px;
        }}
        """
        freq_tab_title = pn.pane.Markdown(f"## Frequency Table (click to design)")
        freq_tab_btn = pn.widgets.Button(
            description='Frequency Table', button_type='primary', stylesheets=[button_frequency_table_stylesheet])
        freq_tab_btn.on_click(Gui.on_button_click)
        freq_tab_col = pn.Column(freq_tab_title, freq_tab_btn)
        table_col = pn.Column(table_title, freq_tab_col, cross_tab_col)
        ## Charts *****************************************************************
        ## Area
        button_area_chart_stylesheet = f"""
        :host {{
            background-image: url("{AREA_CHART}");
            background-repeat: no-repeat;
            border: #cdcdcd solid 5px;
            border-radius: 6px;
            width: 438px;
            height: 264px;
            --primary-color: None;
        }}
        """
        area_chart_title = pn.pane.Markdown(f"## Area Chart (click to design)")
        area_chart_btn = pn.widgets.Button(
            description='Area Chart', button_type='primary', stylesheets=[button_area_chart_stylesheet])
        area_chart_btn.on_click(Gui.on_button_click)
        area_chart_col = pn.Column(area_chart_title, area_chart_btn)

        ## Simple Bar Chart
        button_bar_simple_stylesheet = f"""
        :host {{
            background-image: url("{BAR_SIMPLE}");
            background-repeat: no-repeat;
            width: 396px;
            height: 264px;
            border: #cdcdcd solid 5px;
            border-radius: 6px;
            --primary-color: None;
        }}
        """
        bar_simple_title = pn.pane.Markdown(f"## Simple Bar Chart (click to design)")
        bar_simple_btn = pn.widgets.Button(
            description='Simple Bar Chart', button_type='primary', stylesheets=[button_bar_simple_stylesheet])
        bar_simple_btn.on_click(Gui.on_button_click)
        bar_simple_chart_col = pn.Column(bar_simple_title, bar_simple_btn)

        ## Simple Pie Chart
        button_pie_stylesheet = f"""
        :host {{
            background-image: url("{PIE_CHART}");
            background-repeat: no-repeat;
            width: 300px;
            height: 264px;
            border: #cdcdcd solid 5px;
            border-radius: 6px;
            --primary-color: None;
        }}
        """
        pie_title = pn.pane.Markdown(f"## Pie Chart (click to design)")
        pie_btn = pn.widgets.Button(
            description='Pie Chart', button_type='primary', stylesheets=[button_pie_stylesheet])
        pie_btn.on_click(Gui.on_button_click)
        pie_chart_col = pn.Column(pie_title, pie_btn)

        ## Charts combine
        charts_flexbox = pn.FlexBox(area_chart_col, bar_simple_chart_col, pie_chart_col, )

        ## Statistical Tests *****************************************************************
        stats_select_radio_group = pn.widgets.RadioBoxGroup(
            name='Statistical Test',
            options=['ANOVA', 'Chi Square', 'Independent Samples T-Test', 'Kruskal-Wallis H', 'Mann-Whitney U', 'Normality', 'Paired Samples T-Test', "Pearson's R", "Spearman's R", "Wilcoxon's Signed Ranks", ],
            inline=False,
        )

        ## Stats combine
        stats_flexbox = pn.FlexBox(stats_select_radio_group, )

        ## Combine
        self.tabs = pn.Tabs(
            ('Data', data_col),
            ('Tables', table_col),
            ('Charts', charts_flexbox),
            ('Statistics', stats_flexbox),
        )

    def display_csv(self, csv_fpath: Path):
        if self.file_input.filename:
            print(self.file_input.filename)
            csv_fpath = self.file_input.filename
            df = pd.read_csv(csv_fpath)
            print(df)
            self.tab_df.value = df.head(n=N_CSV_ROWS)
            self.tab_df.visible = True

    def run(self):
        pn.template.MaterialTemplate(
            site="SOFA Stats",
            main=[self.tabs, ],
        ).servable()

gui = Gui()
gui.run()

# w = pn.widgets.Button()  ## TODO: Ben - do we make and destroy or just hide and unhide?
