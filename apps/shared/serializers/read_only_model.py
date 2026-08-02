from rest_framework.serializers import ModelSerializer


class ReadOnlyModelSerializer(ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field in fields:
            fields[field].read_only = True
        return fields
