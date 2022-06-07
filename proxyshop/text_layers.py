"""
TEXT LAYER MODULE
"""
import proxyshop.helpers as psd
from proxyshop.constants import con
from proxyshop.settings import cfg
from proxyshop import format_text as ft
from proxyshop.helpers import ps, app


"""
Text Layer Classes
"""


class TextField:
    """
    A generic TextField, which allows you to set a text layer's contents and text color.
    @param layer: TextItem layer to insert contents.
    @param contents: Text contents to be inserted.
    @param color: Font color to use for this TextItem.
    """
    def __init__(self, layer, contents = "", color = None):
        self.contents = contents.replace("\n", "\r")
        if color: self.text_color = color
        else: self.text_color = psd.get_text_layer_color(layer)
        self.layer = layer

    def execute(self):
        """
        Enables, fills, and colors the text item.
        """
        self.layer.visible = True
        self.layer.textItem.contents = self.contents
        self.layer.textItem.color = self.text_color


class ScaledTextField (TextField):
    """
    A TextField which automatically scales down its font size (in 0.25 pt increments) until
    its right bound no longer overlaps with a reference layer's left bound.
    """
    def __init__(self, layer, contents = "", color = None, reference = None):
        super().__init__(layer, contents, color)
        self.reference = reference

    def execute(self):
        super().execute()

        # Scale down the text layer until it doesn't overlap with a reference layer
        ft.scale_text_right_overlap(self.layer, self.reference)


class ExpansionSymbolField (TextField):
    """
    A TextField which represents a card's expansion symbol.
    @param layer: Expansion symbol layer
    @param contents: The symbol character
    @param rarity: The clipping mask to enable (uncommon, rare, mythic)
    @param reference: Reference layer to scale and center
    @param centered: Whether to center horizontally, ex: Ixalan
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        rarity = "common",
        reference = None, centered = False
    ):
        super().__init__(layer, contents, color)
        self.centered = centered
        self.rarity = rarity
        self.reference = reference

        # Special mythic rarities
        if rarity in (con.rarity_bonus, con.rarity_special):
            self.rarity = con.rarity_mythic

    def execute(self):
        super().execute()

        # Size to fit reference?
        if cfg.auto_symbol_size:
            if self.centered: psd.frame_expansion_symbol(self.layer, self.reference, True)
            else: psd.frame_expansion_symbol(self.layer, self.reference)
        app.activeDocument.activeLayer = self.layer

        # Rarity above common?
        if self.rarity == con.rarity_common: psd.apply_stroke(cfg.symbol_stroke, psd.rgb_white())
        else:
            mask_layer = psd.getLayer(self.rarity, self.layer.parent)
            mask_layer.visible = True
            psd.apply_stroke(cfg.symbol_stroke, psd.rgb_black())
            psd.select_layer_pixels(self.layer)
            app.activeDocument.activeLayer = mask_layer
            psd.align_horizontal()
            psd.align_vertical()
            psd.clear_selection()

        # Fill in the expansion symbol?
        if cfg.fill_symbol:
            app.activeDocument.activeLayer = self.layer
            if self.rarity == con.rarity_common: psd.fill_expansion_symbol(self.reference, psd.rgb_white())
            else: psd.fill_expansion_symbol(self.reference)


class BasicFormattedTextField (TextField):
    """
    A TextField where the contents may have symbols to be formatted using NDPMTG font,
    and may have italics abilities to be formatted as well. Doesn't support flavor text
    or centered text. For use with fields like mana costs and planeswalker abilities.
    PARAMS are identical to TextItem class.
    """
    def execute(self):
        super().execute()

        # Format text
        app.activeDocument.activeLayer = self.layer
        italic_text = ft.generate_italics(self.contents)
        ft.format_text(self.contents, italic_text, -1, False)


class FormattedTextField (TextField):
    """
    A TextField where the contents contain some number of symbols which should be replaced
    with glyphs from the NDPMTG font. For example, if the text contents for an instance of
    self class is "{2}{R}", formatting self text with NDPMTG would correctly show the mana
    cost 2R with text contents "o2or" with characters being appropriately colored. The big
    boy version which supports centered text and flavor text. For use with card rules text.
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        flavor_text = "",
        centered = False
    ):
        super().__init__(layer, contents, color)
        self.flavor_text = flavor_text.replace("\n", "\r")
        self.centered = centered

    def get_italics_and_flavor_index(self):
        """
        Returns an array of italic text for the instance's text contents and the index at which flavour text begins.
        Within flavour text, any text between asterisks should not be italicised, and the asterisks should not be
        included in the rendered flavour text.
        @return: Dict of flavor index, and italic text array
        """

        # generate italic text arrays from things in (parentheses), ability words, and the given flavor text
        italic_text = ft.generate_italics(self.contents)

        # Flavor text included?
        if len(self.flavor_text) > 1:
            # remove things between asterisks from flavor text if necessary
            flavor_text_split = self.flavor_text.split("*")
            if len(flavor_text_split) > 1:
                # asterisks present in flavor text
                for i in flavor_text_split:
                    # add the parts of the flavor text not between asterisks to italic_text
                    if i != "": italic_text.append(i)

                # reassemble flavor text without asterisks
                self.flavor_text = "".join(flavor_text_split)
            else: italic_text.append(self.flavor_text)
            flavor_index = len(self.contents)
        else: flavor_index = -1

        # Return the values
        return {
            'flavor_index': flavor_index,
            'italic_text': italic_text,
        }

    def execute(self):
        super().execute()

        # Generate italics text array from things in (parentheses), ability words, and the flavor text
        ret = self.get_italics_and_flavor_index()
        self.flavor_index = ret['flavor_index']
        self.italic_text = ret['italic_text']

        # Format text
        app.activeDocument.activeLayer = self.layer
        ft.format_text(self.contents + "\r" + self.flavor_text, self.italic_text, self.flavor_index, self.centered)
        if self.centered: self.layer.textItem.justification = ps.Justification.Center


class FormattedTextArea (FormattedTextField):
    """
    A FormattedTextField where the text is required to fit within a given area.
    An instance of this class will step down the font size until the text fits
    within the reference layer's bounds, then rasterize the text layer, and
    center it vertically with respect to the reference layer's selection area.
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        flavor = "",
        reference = None,
        divider = None,
        centered = False,
        fix_length = True
    ):
        super().__init__(layer, contents, color, flavor, centered)
        if divider and cfg.flavor_divider and len(self.flavor_text) > 0 and len(self.contents) > 0:
            con.flavor_text_lead = con.flavor_text_lead_divider
            self.divider = divider
        else: self.divider = None
        self.reference = reference

        # Prepare for text being too long
        if fix_length and len(contents) > 300:
            steps = int((len(contents)-200)/100)
            layer.textItem.size = layer.textItem.size - steps
            layer.textItem.leading = layer.textItem.leading - steps

    def insert_divider(self):
        """
        Inserts and correctly positions flavor bar divider.
        """
        if len(self.flavor_text) > 0:
            # Create a contents-only layer to reference
            contents_test = self.layer.duplicate()
            app.activeDocument.activeLayer = contents_test
            ft.format_text(self.contents, self.italic_text, self.flavor_index, self.centered)
            contents_replace = contents_test.textItem.contents
            contents_test.remove()

            # Create a flavor-text-only layer to reference
            flavor_test = self.layer.duplicate()
            app.activeDocument.activeLayer = flavor_test
            ft.format_text(self.flavor_text, [], 0, self.centered)
            flavor_replace = flavor_test.textItem.contents
            flavor_test.remove()

            # Established two separate layers: contents and flavor, each rasterized
            self.layer.visible = False
            layer_text_contents = self.layer.duplicate()
            psd.replace_text(layer_text_contents, flavor_replace, "")
            layer_text_contents.rasterize(ps.RasterizeType.EntireLayer)
            layer_flavor_text = self.layer.duplicate()
            psd.replace_text(layer_flavor_text, contents_replace, "")
            layer_flavor_text.rasterize(ps.RasterizeType.EntireLayer)
            self.layer.visible = True

            # Get contents southern bound, move flavor text to bottom, get its northern bound
            text_contents_bottom = layer_text_contents.bounds[3]
            layer_flavor_text.translate(0, self.layer.bounds[3] - layer_flavor_text.bounds[3])
            flavor_text_top = layer_flavor_text.bounds[1]

            # Take our final midpoint measurement and remove duplicates
            divider_y_midpoint = (text_contents_bottom + flavor_text_top) / 2
            layer_text_contents.remove()
            layer_flavor_text.remove()

            # Enable the divider and move it
            self.divider.visible = True
            app.activeDocument.activeLayer = self.divider
            app.activeDocument.selection.select([
                [0, divider_y_midpoint - 1],
                [1, divider_y_midpoint - 1],
                [1, divider_y_midpoint + 1],
                [0, divider_y_midpoint + 1]
            ])
            psd.align_vertical()
            psd.clear_selection()

    def execute(self):
        super().execute()
        if self.contents != "" or self.flavor_text != "":
            # Resize the text until it fits into the reference layer
            ft.scale_text_to_fit_reference(self.layer, self.reference)

            # Ensure the layer is centered vertically
            ft.vertically_align_text(self.layer, self.reference)

            # Ensure the layer is centered horizontally if needed
            if self.centered:
                psd.select_layer_pixels(self.reference)
                app.activeDocument.activeLayer = self.layer
                psd.align_horizontal()
                psd.clear_selection()

            # Insert flavor divider if needed
            if self.divider: self.insert_divider()


class CreatureFormattedTextArea (FormattedTextArea):
    """
    FormattedTextArea which also respects the bounds of creature card's power/toughness boxes.
    If the rasterized and centered text layer overlaps with another specified reference layer
    (which should represent the bounds of the power/toughness box), the layer will be shifted
    vertically to ensure that it doesn't overlap.
    """
    def __init__(
        self,
        layer,
        contents = "",
        color = None,
        flavor = "",
        reference = None,
        divider = None,
        pt_reference = None,
        pt_top_reference = None,
        centered = False,
        fix_length = True
    ):
        super().__init__(layer, contents, color, flavor, reference, divider, centered, fix_length)
        self.pt_reference = pt_reference
        self.pt_top_reference = pt_top_reference

    def execute(self):
        super().execute()

        # shift vertically if the text overlaps the PT box
        delta = ft.vertically_nudge_creature_text(self.layer, self.pt_reference, self.pt_top_reference)
        if delta and self.divider:
            if delta < 0: self.divider.translate(0, delta)
