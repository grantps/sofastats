# /// script
# dependencies = ['sofastats @ git+https://github.com/grantps/sofastats']
# ///
from sofastats.output.stats import anova

anova.AnovaDesign(
    measure_field_name='height',
    grouping_field_name='sport',
    group_values=[1, 2, 3],
    csv_file_path='sports.csv',
    data_label_mappings={
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
        'sport': {
            'variable_label': 'Sport',
            'variable_comment': 'Only the sports in the tournament',
            'value_labels': {
                1: 'Archery',
                2: 'Badminton',
                3: 'Basketball',
            },
        },
    }
).make_output()
