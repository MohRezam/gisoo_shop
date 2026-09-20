from django.contrib.admin.filters import (
    AllValuesFieldListFilter,
    BooleanFieldListFilter,
    ChoicesFieldListFilter,
    RelatedFieldListFilter,
)


def _persian_all_choices(choices_iter):
    for index, choice in enumerate(choices_iter):
        if index == 0:
            choice = {**choice, "display": "همه"}
        yield choice


class PersianChoicesFilter(ChoicesFieldListFilter):
    def choices(self, changelist):
        yield from _persian_all_choices(super().choices(changelist))


class PersianAllValuesFilter(AllValuesFieldListFilter):
    def choices(self, changelist):
        yield from _persian_all_choices(super().choices(changelist))


class PersianRelatedFilter(RelatedFieldListFilter):
    def choices(self, changelist):
        yield from _persian_all_choices(super().choices(changelist))


class PersianBooleanFilter(BooleanFieldListFilter):
    def choices(self, changelist):
        mapping = {
            "All": "همه",
            "Yes": "بله",
            "No": "خیر",
            "Unknown": "نامشخص",
        }
        for choice in super().choices(changelist):
            display = str(choice.get("display", ""))
            for english, persian in mapping.items():
                if display == english or display.startswith(f"{english} ("):
                    display = display.replace(english, persian, 1)
                    break
            yield {**choice, "display": display}
