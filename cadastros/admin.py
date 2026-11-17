from django.contrib import admin
from datetime import datetime, timezone as datetime_timezone
from django.urls import reverse
from django.utils.html import format_html
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
    list_display = ["id", "nome", "telefone", "cpf", "criado_em"]
    search_fields = ["nome", "telefone", "cpf"]
    inlines = [AparelhoInline]
    readonly_fields = ["id", "link_relatorio"]

    @admin.display(description="Relatório")
    def link_relatorio(self, obj):
        if not obj or not obj.pk:
            return "Salve o cliente para gerar o relatório."
        url = reverse("cliente-relatorio-pdf", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Abrir relatório do cliente (PDF)</a>', url)


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
