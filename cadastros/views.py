from decimal import Decimal

from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.decorators import action

from .models import Aparelho, Cliente
from .serializers import AparelhoSerializer, ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    queryset = Cliente.objects.all().prefetch_related("aparelhos").annotate(
        total_aparelhos=Count("aparelhos", distinct=True),
        valor_total=Coalesce(Sum("aparelhos__preco"), Value(Decimal("0.00")), output_field=DecimalField(max_digits=14, decimal_places=2)),
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome", "telefone", "cpf", "endereco"]
    ordering_fields = ["nome", "criado_em"]
    ordering = ["nome"]

    @action(detail=True, methods=["get"], url_path="relatorio.pdf", renderer_classes=[])
    def relatorio_pdf(self, request, pk=None):
        cliente = get_object_or_404(Cliente.objects.prefetch_related("aparelhos"), pk=pk)
        linhas = ["CADASTRO DE CLIENTE", "", f"Nome: {cliente.nome}",
                  f"Telefone: {cliente.telefone or '-'}", f"CPF: {cliente.cpf or '-'}",
                  f"Endereco: {cliente.endereco or '-'}", "", "APARELHOS"]
        total = Decimal("0.00")
        for aparelho in cliente.aparelhos.all():
            linhas.extend([f"{aparelho.marca} {aparelho.modelo}".strip(),
                           f"Serial: {aparelho.numero_serial or '-'} | Preco: R$ {aparelho.preco:.2f}",
                           f"Descricao: {aparelho.descricao or '-'}", ""])
            total += aparelho.preco
        linhas.append(f"VALOR TOTAL: R$ {total:.2f}")
        response = HttpResponse(_build_pdf(linhas), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="cliente-{cliente.pk}.pdf"'
        return response


class AparelhoViewSet(viewsets.ModelViewSet):
    serializer_class = AparelhoSerializer
    queryset = Aparelho.objects.select_related("cliente").all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["modelo", "marca", "numero_serial", "descricao", "cliente__nome"]
    ordering_fields = ["modelo", "marca", "preco", "criado_em"]
    ordering = ["id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        cliente_id = self.request.query_params.get("cliente")
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset


def _build_pdf(lines):
    """Build a simple one-page PDF using only the Python standard library."""
    def pdf_text(value):
        encoded = value.encode("cp1252", errors="replace")
        escaped = encoded.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
        return b"(" + escaped + b")"

    commands = [b"BT", b"/F1 11 Tf", b"50 790 Td", b"15 TL"]
    for index, line in enumerate(lines[:48]):
        if index:
            commands.append(b"T*")
        commands.extend([pdf_text(line), b"Tj"])
    commands.append(b"ET")
    stream = b"\n".join(commands)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.extend(f"{offset:010} 00000 n \n".encode())
    output.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(output)
