# flake8: noqa
from django.db import transaction
from django.db.models.sql.compiler import SQLDeleteCompiler

# this codes for handle cascade delete in the sql instead of orm to not make lot queries.


def get_delete_sql(query):
    return SQLDeleteCompiler(
        query.query, transaction.get_connection(), query.db
    ).as_sql()


def execute_compiled_sql(sql, params=None):
    rows_affected = 0
    with transaction.get_connection().cursor() as cur:
        params = params or None
        cur.execute(sql, params)
        rows_affected = cur.rowcount
    return rows_affected


def cascade_delete(
    from_model, instance_pk_query, skip_relations=[], base_model=None, level=0
):
    if base_model is None:
        base_model = from_model
    instance_pk_query = instance_pk_query.values_list("pk", flat=True)

    for m2m_field in from_model._meta.many_to_many:
        through_model = m2m_field.remote_field.through
        field_name = m2m_field.m2m_field_name()
        filterspec = {f"{field_name}__in": instance_pk_query}
        rec_count = execute_compiled_sql(
            *get_delete_sql(through_model.objects.filter(**filterspec))
        )

    for model_relation in from_model._meta.related_objects:
        related_model = model_relation.related_model
        if related_model in skip_relations:
            continue

        elif model_relation.on_delete.__name__ == "CASCADE":
            filterspec = {
                f"{model_relation.remote_field.column}__in": instance_pk_query
            }
            related_pk_values = related_model.objects.filter(**filterspec).values_list(
                related_model._meta.pk.name, flat=True
            )
            cascade_delete(
                related_model,
                related_pk_values,
                base_model=base_model,
                level=level + 1,
                skip_relations=skip_relations,
            )

    del_query = from_model.objects.filter(pk__in=instance_pk_query)
    rec_count = execute_compiled_sql(*get_delete_sql(del_query))
