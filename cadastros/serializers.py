from rest_framework import serializers
from .models import Aparelho, Cliente

class AparelhoSerializer(serializers.ModelSerializer):
    createdAt = serializers.IntegerField(source="created_at", required=False, allow_null=True)
    deliveredAt = serializers.IntegerField(source="delivered_at", required=False, allow_null=True)

    class Meta:
        model = Aparelho
        fields = ["id", "cliente", "modelo", "marca", "numero_serial", "descricao", "preco", "createdAt", "deliveredAt", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

class ClienteSerializer(serializers.ModelSerializer):
    aparelhos = AparelhoSerializer(many=True, read_only=True)
    total_aparelhos = serializers.IntegerField(read_only=True)
    valor_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Cliente
        fields = ["id", "nome", "telefone", "cpf", "endereco", "aparelhos", "total_aparelhos", "valor_total", "criado_em", "atualizado_em"]
        read_only_fields = ["id", "criado_em", "atualizado_em"]

    def validate_cpf(self, value):
        value = value.strip() or None
        query = Cliente.objects.filter(cpf=value) if value else Cliente.objects.none()
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("Já existe um cliente cadastrado com este CPF.")
        return value
