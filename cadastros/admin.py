from django.contrib import admin
from .models import Aparelho, Cliente


class AparelhoInline(admin.TabularInline):
    model = Aparelho
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome", "telefone", "cpf", "criado_em"]
    search_fields = ["nome", "telefone", "cpf"]
    inlines = [AparelhoInline]


@admin.register(Aparelho)
class AparelhoAdmin(admin.ModelAdmin):
    list_display = ["modelo", "marca", "cliente", "preco"]
    search_fields = ["modelo", "marca", "numero_serial", "cliente__nome"]
    list_filter = ["marca"]
