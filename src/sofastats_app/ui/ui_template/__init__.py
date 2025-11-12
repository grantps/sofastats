import pathlib

import param

from panel.theme import Design
from panel.theme.native import Native
from panel.template.base import BasicTemplate


class ChocolateTemplate(BasicTemplate):
    """
    The ChocolateTemplate is a tweaked version of the built-in VanillaTemplate.
    It is named in honour of Truffles, the Polish Chocolate rabbit who inspired many of the cartoons.
    """
    def __init__(self, local_logo_url: str, **kwargs):
        super().__init__(**kwargs)
        self._render_variables['local_logo_url'] = local_logo_url

    design = param.ClassSelector(class_=Design, default=Native,
        is_instance=False, instantiate=False, doc="A Design applies a specific design system to a template.")

    _css = [pathlib.Path(__file__).parent / 'chocolate.css']

    _resources = {
        'css': {
            'lato': "https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext"
        },
    }

    _template = pathlib.Path(__file__).parent / 'chocolate.html'
