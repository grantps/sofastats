"""
c && cd ~/projects/sofastats/example_scripts/ && panel serve --dev modal_experiment.py
"""

import panel as pn

pn.extension('modal')

modal_a = pn.layout.Modal(pn.pane.Markdown("## A all the way!"), name='a', background_close=False, width=200, height=200)
btn_a = pn.widgets.Button(name="Open A")
modal_a.append(pn.pane.Markdown("Added :-) after but not in event ???"))

def open_a(_event):
    ## If the next line is enabled, even the "A all the way!" will not appear in the Modal let alone "Added in ..." :-(
    # modal_a.append(pn.pane.Markdown("Added in event so won't be part of modal but will appear elsewhere :-("))
    modal_a.show()

btn_a.on_click(open_a)

pn.template.VanillaTemplate(
    title='Modal Experiment',
    main=[btn_a, modal_a, ],
).servable()

##===============================================================================================

# modal_a = pn.layout.Modal(pn.pane.Markdown("## A all the way!"), name='a')
# modal_b = pn.layout.Modal(pn.pane.Markdown("## B - who you want to be!"), name='b')
#
# btn_a = pn.widgets.Button(name="Open A")
# btn_b = pn.widgets.Button(name="Open B")
# def open_a(_event):
#     modal_a.show()
# def open_b(_event):
#     modal_b.show()
# btn_a.on_click(open_a)
# btn_b.on_click(open_b)
# pn.template.VanillaTemplate(
#     title='Modal Experiment',
#     main=[btn_a, btn_b, modal_a, modal_b],
# ).servable()

##===============================================================================================

# modal_b = pn.layout.Modal(pn.pane.Markdown("## B - who you want to be!"), name='b', background_close=False)
# modal_b.css_classes = ['full-screen-modal', ]
# btn_b = pn.widgets.Button(name="Open B")
# modal_a = pn.layout.Modal(pn.pane.Markdown("## A all the way!"), btn_b, name='a', background_close=False)
# modal_a.css_classes = ['full-screen-modal', ]
# btn_a = pn.widgets.Button(name="Open A")
#
# def open_a(_event):
#     modal_a.show()
# def open_b(_event):
#     print(modal_b.objects)
#     modal_b.append(pn.pane.Markdown("Sausage!!!!!!"))
#     print(modal_b.objects)
#     modal_b.show()
# btn_a.on_click(open_a)
# btn_b.on_click(open_b)
# pn.template.VanillaTemplate(
#     title='Modal Experiment',
#     main=[btn_a, btn_b, modal_a, modal_b],
# ).servable()

##===============================================================================================

# w1 = pn.widgets.TextInput(name='Text:')
# w2 = pn.widgets.FloatSlider(name='Slider')
#
# modal = pn.Modal(w1, w2, name='Basic FloatPanel', margin=20)
# toggle_button = modal.create_button("toggle", name="Toggle modal")
# modal.append("Sausage2")
#
#
# col = pn.Column('**Example: Basic `Modal`**', toggle_button, modal)
# col.servable()
