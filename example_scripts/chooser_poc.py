"""
Two UI areas: chooser, and selector
Within chooser, there is the big choice, and the sub-choosers.
Everything works through params which are driven by radio selections.
"""
from enum import StrEnum

import panel as pn
import param

class Alternative(StrEnum):
    NONE = 'None'
    TRUE = 'True'
    FALSE = 'False'

class DiffVsRel(StrEnum):
    DIFFERENCE = 'Difference'
    RELATIONSHIP = 'Relationship'
    UNKNOWN = 'Not Sure'

class NumGroups(StrEnum):
    TWO = 'Two Groups'
    THREE_PLUS = 'Three or More Groups'
    UNKNOWN = 'Not Sure'

class Normal(StrEnum):
    NORMAL = 'Normal'
    NOT_NORMAL = 'Not Normal'
    UNKNOWN = 'Not Sure'

class IndepVsPaired(StrEnum):
    INDEPENDENT = 'Independent'
    PAIRED = 'Paired'
    UNKNOWN = 'Not Sure'

class OrdinalVsCategorical(StrEnum):
    ORDINAL = 'Ordinal'
    CATEGORICAL = 'Categorical'
    UNKNOWN = 'Not Sure'

class StatsOptions(StrEnum):
    ANOVA = 'ANOVA'
    CHI_SQUARE = 'Chi Square'
    KRUSKAL_WALLIS = 'Kruskal-Wallis H'
    MANN_WHITNEY = 'Mann-Whitney U'
    PEARSONS = "Pearson's R Correlation"
    SPEARMANS = "Spearman's R Correlation"
    TTEST_INDEP = 'Independent Samples T-Test'
    TTEST_PAIRED = 'Paired Samples T-Test'
    WILCOXON = 'Wilcoxon Signed Ranks'

class Choice(param.Parameterized):
    value = param.String(default=Alternative.NONE)

difference_not_relationship_param = Choice(value=DiffVsRel.UNKNOWN)

two_not_three_plus_groups_for_diff_param = Choice(value=NumGroups.UNKNOWN)
normal_not_abnormal_for_diff_param = Choice(value=Normal.UNKNOWN)
independent_not_paired_for_diff_param = Choice(value=IndepVsPaired.UNKNOWN)

ordinal_at_least_for_rel_param = Choice(value=OrdinalVsCategorical.UNKNOWN)
normal_not_abnormal_for_rel_param = Choice(value=Normal.UNKNOWN)

difference_vs_relationship_radio = pn.widgets.RadioButtonGroup(
    name='Difference vs Relationship',
    options=[
        DiffVsRel.DIFFERENCE,
        DiffVsRel.RELATIONSHIP,
        DiffVsRel.UNKNOWN,
    ],
    button_type='primary', button_style='outline',
    description=("Are you trying to see if there are differences between groups "
        "(e.g. different mean height between players of different sports) "
        "or relationships (e.g. between education level and income)?"),
    value=DiffVsRel.UNKNOWN,
)


class SubChooser:

    ## DIFFERENCE ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @staticmethod
    def _set_indep_vs_paired_param(indep_vs_paired_value):
        # print(f"independent_not_paired_for_diff_param is now '{indep_vs_paired_value}'")
        independent_not_paired_for_diff_param.value = indep_vs_paired_value

    @staticmethod
    def get_indep_vs_paired_chooser(two_not_three_plus_groups_for_diff_param_val):
        indep_vs_paired_chooser_or_none = None
        if two_not_three_plus_groups_for_diff_param_val == NumGroups.TWO:
            independent_groups_radio = pn.widgets.RadioButtonGroup(
                name='Independent Groups',
                options=[
                    IndepVsPaired.INDEPENDENT,
                    IndepVsPaired.PAIRED,
                    IndepVsPaired.UNKNOWN,
                ],
                button_type='success', button_style='outline',
                description=("Are the groups independent e.g. 'NZ' and 'USA', or paired "
                    "(e.g. 'Student score before tutoring' and 'Student score after tutoring')?"),
                value=IndepVsPaired.UNKNOWN,
            )
            indep_vs_paired_param_setter = pn.bind(SubChooser._set_indep_vs_paired_param, independent_groups_radio)
            indep_vs_paired_chooser_or_none = pn.Column(
                pn.pane.Markdown("Are the Groups Independent or Paired?"), independent_groups_radio,
                indep_vs_paired_param_setter,
            )
        return indep_vs_paired_chooser_or_none

    @staticmethod
    def _set_norm_for_diff_param(norm_vs_abnormal_value):
        # print(f"normal_not_abnormal_for_diff_param is now '{norm_vs_abnormal_value}'")
        normal_not_abnormal_for_diff_param.value = norm_vs_abnormal_value

    @staticmethod
    def _set_num_of_groups_param(num_of_groups_value):
        # print(f"two_not_three_plus_groups_for_diff_param is now '{num_of_groups_value}'")
        two_not_three_plus_groups_for_diff_param.value = num_of_groups_value

    @staticmethod
    def difference_sub_chooser():  ## <====================== DIFFERENCE Main Act!
        normal_for_diff_radio = pn.widgets.RadioButtonGroup(
            name='Normality',
            options=[
                Normal.NORMAL,
                Normal.NOT_NORMAL,
                Normal.UNKNOWN,
            ],
            button_type='success', button_style='outline',
            description=("Is your data normal "
                "i.e. are the values numbers that at least roughly follow a normal distribution curve (bell curve)?"),
            value=Normal.UNKNOWN,
        )
        norm_for_diff_param_setter = pn.bind(SubChooser._set_norm_for_diff_param, normal_for_diff_radio)
        number_of_groups_radio = pn.widgets.RadioButtonGroup(
            name='Number of Groups',
            options=[
                NumGroups.TWO,
                NumGroups.THREE_PLUS,
                NumGroups.UNKNOWN,
            ],
            button_type='success', button_style='outline',
            description=("Are you looking at the difference between two groups "
                "e.g. 'Male' vs 'Female' or between three or more groups e.g. 'Archery' vs 'Badminton' vs 'Basketball'?"),
            value=NumGroups.UNKNOWN,
        )
        indep_vs_paired_chooser = pn.bind(SubChooser.get_indep_vs_paired_chooser, number_of_groups_radio)
        num_of_groups_param_setter = pn.bind(SubChooser._set_num_of_groups_param, number_of_groups_radio)
        col_items = [
            pn.pane.Markdown("Data Values are Normal?"), normal_for_diff_radio,
            pn.pane.Markdown("How Many Groups?"), number_of_groups_radio,
            indep_vs_paired_chooser,
            norm_for_diff_param_setter, num_of_groups_param_setter,
        ]
        sub_chooser = pn.Column(*col_items)
        return sub_chooser

    ## RELATIONSHIP ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @staticmethod
    def _set_norm_for_rel(normal_not_abnormal_for_rel_value):
        # print(f"normal_not_abnormal_for_rel_param is now '{normal_not_abnormal_for_rel_value}'")
        normal_not_abnormal_for_rel_param.value = normal_not_abnormal_for_rel_value

    @staticmethod
    def get_normal_chooser_or_none(ordinal_vs_categorical_val):
        normal_chooser_or_none = None
        if ordinal_vs_categorical_val == OrdinalVsCategorical.ORDINAL:
            normal_for_rel_radio = pn.widgets.RadioButtonGroup(
                name='Normality',
                options=[
                    Normal.NORMAL,
                    Normal.NOT_NORMAL,
                    Normal.UNKNOWN,
                ],
                button_type='success', button_style='outline',
                description=("Is your data normal "
                    "i.e. are the values numbers that at least roughly follow a normal distribution curve (bell curve)?"),
                value=Normal.UNKNOWN,
            )
            norm_for_rel_param_setter = pn.bind(SubChooser._set_norm_for_rel, normal_for_rel_radio)
            normal_chooser_or_none = pn.Column(pn.pane.Markdown("Data Values are Normal?"), normal_for_rel_radio,
                norm_for_rel_param_setter)
        return normal_chooser_or_none

    @staticmethod
    def _set_ordinal_vs_categorical(ordinal_vs_categorical_value):
        # print(f"ordinal_at_least_for_rel_param is now '{ordinal_vs_categorical_value}'")
        ordinal_at_least_for_rel_param.value = ordinal_vs_categorical_value

    @staticmethod
    def relationship_sub_chooser():  ## <====================== RELATIONSHIP Main Act!
        ordinal_vs_categorical_radio = pn.widgets.RadioButtonGroup(
            name='Ordinal vs Categorical',
            options=[
                OrdinalVsCategorical.ORDINAL,
                OrdinalVsCategorical.CATEGORICAL,
                OrdinalVsCategorical.UNKNOWN,
            ],
            button_type='success', button_style='outline',
            description=("Do the values have a true sort order (ordinal data) e.g. 1, 2, 3? "
                "Or are they just names e.g. 'NZ', 'Denmark', 'Sri Lanka' (categorical data)?"),
            value=Normal.UNKNOWN,
        )
        normal_chooser_or_none = pn.bind(SubChooser.get_normal_chooser_or_none, ordinal_vs_categorical_radio)
        ordinal_vs_categorical_param_setter = pn.bind(SubChooser._set_ordinal_vs_categorical, ordinal_vs_categorical_radio)
        sub_chooser = pn.Column(
            pn.pane.Markdown("Ordinal or Categorical?"), ordinal_vs_categorical_radio,
            normal_chooser_or_none, ordinal_vs_categorical_param_setter,
        )
        return sub_chooser

    @staticmethod
    def get_ui(diff_not_rel: DiffVsRel) -> pn.Column | None:
        if diff_not_rel == DiffVsRel.UNKNOWN:
            sub_chooser = None
        elif diff_not_rel == DiffVsRel.DIFFERENCE:
            sub_chooser = SubChooser.difference_sub_chooser()
        elif diff_not_rel == DiffVsRel.RELATIONSHIP:
            sub_chooser = SubChooser.relationship_sub_chooser()
        else:
            raise ValueError(f"Unexpected {diff_not_rel=}")
        return sub_chooser

def set_diff_vs_rel_param(difference_vs_relationship_value):
    # print(f"difference_not_relationship_param is now '{difference_vs_relationship_value}'")
    difference_not_relationship_param.value = difference_vs_relationship_value

sub_chooser_or_none = pn.bind(SubChooser.get_ui, difference_vs_relationship_radio)
diff_vs_rel_param_setter = pn.bind(set_diff_vs_rel_param, difference_vs_relationship_radio)

chooser_col = pn.Column(
    pn.pane.Markdown("## Help me choose"),
    pn.pane.Markdown("Finding differences or relationships?"),
    difference_vs_relationship_radio,
    sub_chooser_or_none,
    diff_vs_rel_param_setter,
)
stats_test_radio = pn.widgets.RadioBoxGroup(
    name='Statistical Test',
    options=[
        StatsOptions.ANOVA,
        StatsOptions.CHI_SQUARE,
        StatsOptions.KRUSKAL_WALLIS,
        StatsOptions.MANN_WHITNEY,
        StatsOptions.PEARSONS,
        StatsOptions.SPEARMANS,
        StatsOptions.TTEST_INDEP,
        StatsOptions.TTEST_PAIRED,
        StatsOptions.WILCOXON,
    ],
    inline=False)

def get_status(difference_not_relationship_value, two_not_three_plus_groups_for_diff_value,
        normal_not_abnormal_for_diff_value, independent_not_paired_for_diff_value, ordinal_at_least_for_rel_value,
        normal_not_abnormal_for_rel_value):
    print(difference_not_relationship_value, two_not_three_plus_groups_for_diff_value,
        normal_not_abnormal_for_diff_value, independent_not_paired_for_diff_value, ordinal_at_least_for_rel_value,
        normal_not_abnormal_for_rel_value)
    if difference_not_relationship_value == DiffVsRel.UNKNOWN:
        items = sorted(StatsOptions)
    elif difference_not_relationship_value == DiffVsRel.DIFFERENCE:
        if two_not_three_plus_groups_for_diff_value == NumGroups.UNKNOWN:
            if normal_not_abnormal_for_diff_value == Normal.UNKNOWN:
                items = [StatsOptions.ANOVA, StatsOptions.TTEST_INDEP, StatsOptions.TTEST_PAIRED,
                    StatsOptions.KRUSKAL_WALLIS, StatsOptions.MANN_WHITNEY, StatsOptions.WILCOXON]
            elif normal_not_abnormal_for_diff_value == Normal.NORMAL:
                items = [StatsOptions.ANOVA, StatsOptions.TTEST_INDEP, StatsOptions.TTEST_PAIRED]
            elif normal_not_abnormal_for_diff_value == Normal.NOT_NORMAL:
                items = [StatsOptions.KRUSKAL_WALLIS, StatsOptions.MANN_WHITNEY, StatsOptions.WILCOXON]
            else:
                raise Exception(F"Unexpected {normal_not_abnormal_for_diff_value=}")
        elif two_not_three_plus_groups_for_diff_value == NumGroups.TWO:
            if normal_not_abnormal_for_diff_value == Normal.UNKNOWN:
                if independent_not_paired_for_diff_value == IndepVsPaired.UNKNOWN:
                    items = [StatsOptions.TTEST_INDEP, StatsOptions.MANN_WHITNEY,
                        StatsOptions.TTEST_PAIRED, StatsOptions.WILCOXON]
                elif independent_not_paired_for_diff_value == IndepVsPaired.INDEPENDENT:
                    items = [StatsOptions.TTEST_INDEP, StatsOptions.MANN_WHITNEY]
                elif independent_not_paired_for_diff_value == IndepVsPaired.PAIRED:
                    items = [StatsOptions.TTEST_PAIRED, StatsOptions.WILCOXON]
                else:
                    raise Exception(F"Unexpected {independent_not_paired_for_diff_value=}")
            elif normal_not_abnormal_for_diff_value == Normal.NORMAL:
                if independent_not_paired_for_diff_value == IndepVsPaired.UNKNOWN:
                    items = [StatsOptions.TTEST_INDEP, StatsOptions.TTEST_PAIRED]
                elif independent_not_paired_for_diff_value == IndepVsPaired.INDEPENDENT:
                    items = [StatsOptions.TTEST_INDEP, ]
                elif independent_not_paired_for_diff_value == IndepVsPaired.PAIRED:
                    items = [StatsOptions.TTEST_PAIRED, ]
                else:
                    raise Exception(F"Unexpected {independent_not_paired_for_diff_value=}")
            elif normal_not_abnormal_for_diff_value == Normal.NOT_NORMAL:
                if independent_not_paired_for_diff_value == IndepVsPaired.UNKNOWN:
                    items = [StatsOptions.MANN_WHITNEY, StatsOptions.WILCOXON]
                elif independent_not_paired_for_diff_value == IndepVsPaired.INDEPENDENT:
                    items = [StatsOptions.MANN_WHITNEY]
                elif independent_not_paired_for_diff_value == IndepVsPaired.PAIRED:
                    items = [StatsOptions.WILCOXON, ]
                else:
                    raise Exception(F"Unexpected {independent_not_paired_for_diff_value=}")
            else:
                raise Exception(F"Unexpected {normal_not_abnormal_for_diff_value=}")
        elif two_not_three_plus_groups_for_diff_value == NumGroups.THREE_PLUS:
            if normal_not_abnormal_for_diff_value == Normal.UNKNOWN:
                items = []
            elif normal_not_abnormal_for_diff_value == Normal.NORMAL:
                items = []
            elif normal_not_abnormal_for_diff_value == Normal.NOT_NORMAL:
                items = []
            else:
                raise Exception(F"Unexpected {normal_not_abnormal_for_diff_value=}")
        else:
            raise Exception(F"Unexpected {two_not_three_plus_groups_for_diff_value=}")
    elif difference_not_relationship_value == DiffVsRel.RELATIONSHIP:
        if ordinal_at_least_for_rel_value == OrdinalVsCategorical.UNKNOWN:
            if normal_not_abnormal_for_rel_value == Normal.UNKNOWN:
                items = []
            elif normal_not_abnormal_for_rel_value == Normal.NORMAL:
                items = []
            elif normal_not_abnormal_for_rel_value == Normal.NOT_NORMAL:
                items = []
            else:
                raise Exception(F"Unexpected {normal_not_abnormal_for_rel_value=}")
        elif ordinal_at_least_for_rel_value == OrdinalVsCategorical.ORDINAL:
            if normal_not_abnormal_for_rel_value == Normal.UNKNOWN:
                items = []
            elif normal_not_abnormal_for_rel_value == Normal.NORMAL:
                items = []
            elif normal_not_abnormal_for_rel_value == Normal.NOT_NORMAL:
                items = []
            else:
                raise Exception(F"Unexpected {normal_not_abnormal_for_rel_value=}")
        elif ordinal_at_least_for_rel_value == OrdinalVsCategorical.CATEGORICAL:
            items  = []
        else:
            raise Exception(F"Unexpected {ordinal_at_least_for_rel_value=}")
    else:
        raise Exception(F"Unexpected {difference_not_relationship_value=}")
    msg = ", ".join(items)
    return pn.pane.Markdown(msg)

status = pn.bind(get_status,
    difference_not_relationship_param.param.value,
    two_not_three_plus_groups_for_diff_param.param.value,
    normal_not_abnormal_for_diff_param.param.value,
    independent_not_paired_for_diff_param.param.value,
    ordinal_at_least_for_rel_param.param.value,
    normal_not_abnormal_for_rel_param.param.value,
)

selector_col = pn.Column(
    stats_test_radio,
    status,
)

chooser_row = pn.Row(chooser_col, selector_col)

pn.template.MaterialTemplate(
    title="Stats Chooser",
    main=[chooser_row],
).servable()
