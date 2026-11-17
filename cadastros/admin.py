from django.contrib import admin
from datetime import datetime, timezone as datetime_timezone
from django.utils import timezone

from .models import Aparelho, Cliente


def formatar_data_millis(valor):
    if valor is None:
        return "—"
    try:
        instante = datetime.fromtimestamp(valor / 1000, tz=datetime_timezone.utc)
    except (OverflowError, OSError, ValueError):
        return "—"
    return timezone.localtime(instante).strftime("%d/%m/%Y %H:%M:%S %Z")


class AparelhoInline(admin.TabularInline):
    model = Aparelho
    extra = 0
    exclude = ["created_at", "delivered_at"]
    readonly_fields = ["created_at_format", "delivered_at_format"]

    @admin.display(description="Criado em")
    def created_at_format(self, obj):
        return formatar_data_millis(obj.created_at)

    @admin.display(description="Entregue em")
    def delivered_at_format(self, obj):
        return formatar_data_millis(obj.delivered_at)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone", "cpf", "criado_em"]
    search_fields = ["nome", "telefone", "cpf"]
    inlines = [AparelhoInline]


@admin.register(Aparelho)
class AparelhoAdmin(admin.ModelAdmin):
    list_display = ["modelo", "marca", "cliente", "preco", "created_at_format", "delivered_at_format"]
    search_fields = ["modelo", "marca", "numero_serial", "cliente__nome"]
    list_filter = ["marca"]
    exclude = ["created_at", "delivered_at"]
    readonly_fields = ["created_at_format", "delivered_at_format"]

    @admin.display(description="Criado em")
    def created_at_format(self, obj):
        return formatar_data_millis(obj.created_at)

    @admin.display(description="Entregue em")
    def delivered_at_format(self, obj):
        return formatar_data_millis(obj.delivered_at)
