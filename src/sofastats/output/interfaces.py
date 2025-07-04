"""
Note - output.utils.get_report() replies on the template param names here so keep aligned.
Not worth formally aligning them given how easy to do manually and how static.
"""
from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import sqlite3 as sqlite
from typing import Protocol

import jinja2
import pandas as pd

from sofastats import SQLITE_DB, logger
from sofastats.conf.main import INTERNAL_DATABASE_FPATH, SOFASTATS_WEB_RESOURCES_ROOT, DbeName
from sofastats.data_extraction.db import ExtendedCursor, get_dbe_spec
from sofastats.output.charts.conf import DOJO_CHART_JS
from sofastats.output.styles.utils import (get_generic_unstyled_css, get_style_spec, get_styled_dojo_chart_css,
    get_styled_placeholder_css_for_main_tbls, get_styled_stats_tbl_css)
from sofastats.utils.misc import get_safer_name

@dataclass(frozen=False)
class Source(ABC):
    """
    Output classes (e.g. MultiSeriesBoxplotChartSpec) inherit from Source
    but only to enforce validation and fill in attributes (e.g. setting dbe_name to SQLite where appropriate)
    via __post_init__.

    Originally, the common attributes:

    csv_fpath: Path | None = None
    csv_separator: str = ','
    overwrite_csv_derived_tbl_if_there: bool = False
    cur: Any | None = None
    dbe_name: str | None = None  ## database engine name
    src_tbl_name: str | None = None

    were here in the Source class and not in the output classes. Following the DRY principle.
    But because these Source attributes had defaults it forced us to give defaults to mandatory output class attributes
    and rely on output class __post_init__ to enforce them being supplied. Ugly.

    Instead, the decision was to force every output class to repeat the source attributes and their defaults.
    This sacrifices DRY but the copying and pasting is not hard, and it would be easy to make updates across the project
    if ever needed because we just look for inheritance from Source. So not a practical problem.

    At least, using the approach finally adopted, the signatures of the output classes are complete
    and include the Source attributes with their defaults.
    This makes it easier for end users to understand what is required.
    And nothing is required but strings and booleans which makes using the output class easy for end users..

    Alternative approaches in which we avoided inheritance were rejected
    as the output classes are the end-user interface, and we don't want to make the end user craft special objects
    (e.g. a source_spec object) to supply as an attribute to the output class.
    """

    def __post_init__(self):
        """
        Three main paths:
          1) CSV - will be ingested into internal pysofa SQLite database (tbl_name optional - later analyses
             might be referring to that ingested table so nice to let user choose the name)
          2) cursor, dbe_name, and tbl_name
          3) or just a tbl_name (assumed to be using internal pysofa SQLite database)
        Any supplied cursors are "wrapped" inside an ExtendedCursor so we can use .exe() instead of execute
        so better error messages on query failure.

        Client code supplies dbe_name rather than dbe_spec for simplicity but internally
        Source supplies all code that inherits from it dbe_spec ready to use.
        """
        if self.csv_fpath:
            if self.cur or self.dbe_name:
                raise Exception("If supplying a CSV path don't also supply database requirements")
            if not self.csv_separator:
                self.csv_separator = ','
            if not SQLITE_DB.get('sqlite_default_cur'):
                SQLITE_DB['sqlite_default_con'] = sqlite.connect(INTERNAL_DATABASE_FPATH)
                SQLITE_DB['sqlite_default_cur'] = ExtendedCursor(SQLITE_DB['sqlite_default_con'].cursor())
            self.cur = SQLITE_DB['sqlite_default_cur']
            self.dbe_spec = get_dbe_spec(DbeName.SQLITE)
            if not self.src_tbl_name:
                self.src_tbl_name = get_safer_name(self.csv_fpath.stem)
            ## ingest CSV into database
            df = pd.read_csv(self.csv_fpath, sep=self.csv_separator)
            if_exists = 'replace' if self.overwrite_csv_derived_tbl_if_there else 'fail'
            try:
                df.to_sql(self.src_tbl_name, SQLITE_DB['sqlite_default_con'], if_exists=if_exists, index=False)
            except Exception as e:  ## TODO: supply more specific exception
                logger.info(f"Failed at attempt to ingest CSV from '{self.csv_fpath}' "
                    f"into internal pysofa SQLite database as table '{self.src_tbl_name}'.\nError: {e}")
            else:
                logger.info(f"Successfully ingested CSV from '{self.csv_fpath}' "
                    f"into internal pysofa SQLite database as table '{self.src_tbl_name}'")
        elif self.cur:
            self.cur = ExtendedCursor(self.cur)
            if not self.dbe_name:
                raise Exception("When supplying a cursor, a dbe_name (database engine name) must also be supplied")
            else:
                self.dbe_spec = get_dbe_spec(self.dbe_name)
            if not self.src_tbl_name:
                raise Exception("When supplying a cursor, a tbl_name must also be supplied")
        elif self.src_tbl_name:
            if not SQLITE_DB.get('sqlite_default_cur'):
                SQLITE_DB['sqlite_default_con'] = sqlite.connect(INTERNAL_DATABASE_FPATH)
                SQLITE_DB['sqlite_default_cur'] = ExtendedCursor(SQLITE_DB['sqlite_default_con'].cursor())
            self.cur = SQLITE_DB['sqlite_default_cur']  ## not already set if in the third path - will have gone down first
            if self.dbe_name and self.dbe_name != DbeName.SQLITE:
                raise Exception("If not supplying a csv_fpath, or a cursor, the only permitted database engine is "
                    "SQLite (the dbe of the internal pysofa SQLite database)")
            self.dbe_spec = get_dbe_spec(DbeName.SQLITE)
        else:
            raise Exception("Either supply a path to a CSV "
                "(optional tbl_name for when ingested into internal pysofa SQLite database), "
                "a cursor (with dbe_name and tbl_name), "
                "or a tbl_name (data assumed to be in internal pysofa SQLite database)")

HTML_AND_SOME_HEAD_TPL = """\
<!DOCTYPE html>
<head>
<title>{{title}}</title>
<style type="text/css">
<!--
{{generic_unstyled_css}}
-->
</style>
"""

CHARTING_LINKS_TPL = """\
<link rel='stylesheet' type='text/css' href="{{sofastats_web_resources_root}}/tundra.css" />
<script src="{{sofastats_web_resources_root}}/dojo.xd.js"></script>
<script src="{{sofastats_web_resources_root}}/sofastatsdojo_minified.js"></script>
<script src="{{sofastats_web_resources_root}}/sofastats_charts.js"></script>            
"""

CHARTING_CSS_TPL = """\
<style type="text/css">
<!--
    .dojoxLegendNode {
        border: 1px solid #ccc;
        margin: 5px 10px 5px 10px;
        padding: 3px
    }
    .dojoxLegendText {
        vertical-align: text-top;
        padding-right: 10px
    }
    @media print {
        .screen-float-only{
        float: none;
        }
    }
    @media screen {
        .screen-float-only{
        float: left;
        }
    }
{{styled_dojo_chart_css}}
-->
</style>
"""

CHARTING_JS_TPL = """\
{{dojo_chart_js}}
"""

SPACEHOLDER_CSS_TPL = """\
<style type="text/css">
<!--
{{styled_placeholder_css_for_main_tbls}}
-->
</style>
"""

STATS_TBL_TPL = """\
<style type="text/css">
<!--
{{styled_stats_tbl_css}}
-->
</style>
"""

HEAD_END_TPL = "</head>"

BODY_START_TPL = "<body class='tundra'>"

BODY_AND_HTML_END_TPL = """\
</body>
</html>
"""

class OutputItemType(StrEnum):
    CHART = 'chart'
    MAIN_TABLE = 'main_table'
    STATS = 'stats'

@dataclass(frozen=True)
class HTMLItemSpec:
    html_item_str: str
    style_name: str
    output_item_type: OutputItemType

    def to_standalone_html(self, title: str) -> str:
        style_spec = get_style_spec(self.style_name)
        tpl_bits = [HTML_AND_SOME_HEAD_TPL, ]
        if self.output_item_type == OutputItemType.CHART:
            tpl_bits.append(CHARTING_LINKS_TPL)
            tpl_bits.append(CHARTING_CSS_TPL)
            tpl_bits.append(CHARTING_JS_TPL)
        if self.output_item_type == OutputItemType.MAIN_TABLE:
            tpl_bits.append(SPACEHOLDER_CSS_TPL)
        if self.output_item_type == OutputItemType.STATS:
            tpl_bits.append(STATS_TBL_TPL)
        tpl_bits.append(HEAD_END_TPL)
        tpl_bits.append(BODY_START_TPL)
        tpl_bits.append(self.html_item_str)  ## <======= the actual item content e.g. chart
        tpl_bits.append(BODY_AND_HTML_END_TPL)
        tpl = '\n'.join(tpl_bits)

        environment = jinja2.Environment()
        template = environment.from_string(tpl)
        context = {
            'generic_unstyled_css': get_generic_unstyled_css(),
            'sofastats_web_resources_root': SOFASTATS_WEB_RESOURCES_ROOT,
            'title': title,
        }
        if self.output_item_type == OutputItemType.CHART:
            context['styled_dojo_chart_css'] = get_styled_dojo_chart_css(style_spec.dojo)
            context['dojo_chart_js'] = DOJO_CHART_JS
        if self.output_item_type == OutputItemType.MAIN_TABLE:
            context['styled_placeholder_css_for_main_tbls'] = get_styled_placeholder_css_for_main_tbls(self.style_name)
        if self.output_item_type == OutputItemType.STATS:
            context['styled_stats_tbl_css'] = get_styled_stats_tbl_css(style_spec)
        html = template.render(context)
        return html

    def to_file(self, fpath: Path, title: str):
        with open(fpath, 'w') as f:
            f.write(self.to_standalone_html(title))

class HasToHTMLItemSpec(Protocol):
    def to_html_spec(self) -> HTMLItemSpec: ...

@dataclass(frozen=True)
class Report:
    html: str  ## include title

    def to_file(self, fpath: Path):
        with open(fpath, 'w') as f:
            f.write(self.html)
