# /// script
# dependencies = ['sofastats @ /home/g/projects/sofastats']
# ///
from sofastats.output.stats import anova

anova.AnovaDesign(
    ## main settings (required)
    measure_field_name='height',
    grouping_field_name='sport',
    group_values=[1, 2, 3],  ## Archery, Badminton, Basketball (see data_label_mappings below)

    ## Where the data comes from ****************
    csv_file_path='sports.csv',
    # csv_separator=',',
    overwrite_csv_derived_table_if_there=True,
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
    data_label_mappings={
        ## Be careful to start and end things with the same type of quotes
        ## Also remember to put commas at the ends of items
        ## Each indent should be four spaces (not tabs)
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
        ## -----
        'sport': {
            'variable_label': 'Sport',
            'variable_comment': 'Only the sports in the tournament',
            'value_labels': {
                1: 'Archery',
                2: 'Badminton',
                3: 'Basketball',
            },
        },
        ## -----
    }
    # data_labels_yaml_file_path='',
).make_output()
