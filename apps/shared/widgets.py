from django import forms


class GisooRichTextWidget(forms.Textarea):
    """RTL editor stored as HTML in the existing text field. No CDN."""

    def __init__(self, attrs=None):
        base = {
            "class": "gisoo-richtext-source vLargeTextField",
            "data-gisoo-editor": "1",
            "rows": 18,
        }
        if attrs:
            base.update(attrs)
        super().__init__(attrs=base)

    class Media:
        css = {"all": ("admin/css/gisoo_richtext.css",)}
        js = ("admin/js/gisoo_richtext.js",)
