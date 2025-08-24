# /// script

# ///

from webbrowser import open_new_tab
from sofastats.output.stats import anova

def anova_output():
    ## Design your ANOVA test
    design = anova.AnovaDesign(
        measure_field_name='height',
        grouping_field_name='sport',
        group_values=['Archery', 'Badminton', 'Basketball'],
        style_name='prestige_screen',
        csv_file_path='sports.csv',
        overwrite_csv_derived_table_if_there=True,
        high_precision_required=False,
        decimal_points=3,
    )
    ## Save your output file
    output_file_path = '/home/g/projects/sofastats/validation/anova_sofastats.html'
    design.to_html_design().to_file(output_file_path, title='ANOVA SOFAStats')
    ## Open output in your default web browser
    open_new_tab(url=f"file://{output_file_path}")

if __name__ == '__main__':
    anova_output()
