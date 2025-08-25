# /// script
# dependencies = ['sofastats @ /home/g/projects/sofastats']
# ///
from sofastats.output.stats import anova

anova.AnovaDesign(
    ## main settings (required)
    measure_field_name='height',
    grouping_field_name='sport',
    group_values=['Archery', 'Badminton', 'Basketball'],

    ## Where the data comes from ****************
    csv_file_path='sports.csv',
    # csv_separator=',',
    # overwrite_csv_derived_table_if_there=True,
    # cur=cur,
    # database_engine_name='',
    # source_table_name='',
    # table_filter='',

    ## Misc settings ****************************
    # style_name='prestige_screen',
    # high_precision_required=True,
    # decimal_points=3,

    ## Output ***********************************
    # output_file_path='/home/g/projects/sofastats/validation/anova_sofastats.html',
    # output_title='ANOVA SOFAStats',
    # show_in_web_browser=False,
    # data_labels_dict={},
    # data_labels_yaml_file_path='',
).make_output()
