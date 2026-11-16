from django.db import models

class Cliente(models.Model):
    nome = models.CharField("nome", max_length=150, db_index=True)
    telefone = models.CharField("telefone", max_length=30, blank=True)
    cpf = models.CharField("CPF", max_length=14, blank=True, unique=True, null=True)
    endereco = models.TextField("endereço", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome", "id"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.nome

class Aparelho(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="aparelhos")
    modelo = models.CharField("modelo", max_length=120)
    marca = models.CharField("marca", max_length=100, blank=True)
    numero_serial = models.CharField("número de serial", max_length=120, blank=True)
    descricao = models.TextField("descrição", blank=True)
    preco = models.DecimalField("preço", max_digits=12, decimal_places=2, default=0)
    created_at = models.BigIntegerField("createdAt", null=True, blank=True)
    delivered_at = models.BigIntegerField("deliveredAt", null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "aparelho"
        verbose_name_plural = "aparelhos"

    def __str__(self):
        return f"{self.marca} {self.modelo}".strip()
