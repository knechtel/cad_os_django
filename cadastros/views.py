from decimal import Decimal

from django.db import transaction
from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

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

    @action(detail=False, methods=["post"], url_path="importar")
    def importar(self, request):
        """Importa clientes e aparelhos relacionados em uma única operação."""
        dados = request.data
        if isinstance(dados, dict):
            dados = dados.get("clientes")
        if not isinstance(dados, list) or not dados:
            return Response(
                {"detail": "Envie uma lista não vazia de clientes, diretamente ou no campo 'clientes'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        formato_externo = any(isinstance(item, dict) and ("name" in item or "devices" in item) for item in dados)
        aparelhos_por_cliente = []
        if formato_externo:
            clientes_dados = []
            for indice, item in enumerate(dados):
                if not isinstance(item, dict):
                    raise ValidationError({indice: "Cada cliente deve ser um objeto JSON."})
                clientes_dados.append({
                    "nome": item.get("name"),
                    "telefone": item.get("phone", ""),
                    "cpf": item.get("cpf") or "",
                    "endereco": item.get("address", ""),
                })
                devices = item.get("devices", [])
                if not isinstance(devices, list):
                    raise ValidationError({indice: {"devices": "Este campo deve ser uma lista."}})
                aparelhos_por_cliente.append(devices)
            dados = clientes_dados

        serializer = self.get_serializer(data=dados, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            clientes = serializer.save()
            if formato_externo:
                aparelhos_dados = []
                for cliente, devices in zip(clientes, aparelhos_por_cliente):
                    for device_indice, device in enumerate(devices):
                        if not isinstance(device, dict):
                            raise ValidationError({"devices": f"O aparelho {device_indice} do cliente {cliente.nome} deve ser um objeto JSON."})
                        aparelhos_dados.append({
                            "cliente": cliente.pk,
                            "modelo": device.get("model"),
                            "marca": device.get("brand", ""),
                            "numero_serial": device.get("serialNumber", ""),
                            "descricao": device.get("description", ""),
                            "preco": device.get("price", 0),
                            "createdAt": device.get("createdAt"),
                            "deliveredAt": device.get("deliveredAt"),
                        })
                if aparelhos_dados:
                    aparelhos_serializer = AparelhoSerializer(data=aparelhos_dados, many=True)
                    aparelhos_serializer.is_valid(raise_exception=True)
                    aparelhos_serializer.save()
        clientes = self.get_queryset().filter(pk__in=[cliente.pk for cliente in clientes])
        return Response(
            self.get_serializer(clientes, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="relatorio.pdf")
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

    @action(detail=False, methods=["post"], url_path="importar")
    def importar(self, request):
        """Importa vários aparelhos em uma única operação."""
        dados = request.data
        if isinstance(dados, dict):
            dados = dados.get("aparelhos")
        if not isinstance(dados, list) or not dados:
            return Response(
                {"detail": "Envie uma lista não vazia de aparelhos, diretamente ou no campo 'aparelhos'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=dados, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            aparelhos = serializer.save()
        return Response(
            self.get_serializer(aparelhos, many=True).data,
            status=status.HTTP_201_CREATED,
        )

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

    # Cabeçalho com a marca Delta em vetor e os dados da assistência.
    commands = [
        b"q", b"0.78 0.08 0.12 rg", b"50 814 m", b"65 790 l",
        b"37 790 l", b"h", b"f", b"Q",
        b"BT", b"/F1 15 Tf", b"70 798 Td", pdf_text("DELTA AIR LINES"), b"Tj", b"ET",
        b"BT", b"/F1 10 Tf", b"50 773 Td",
        pdf_text("Fernandes Bastos, 1978 - Loja 2 | Telefone: (51) 9350-1980"), b"Tj", b"ET",
        b"BT", b"/F1 11 Tf", b"50 746 Td", b"15 TL",
    ]
    for index, line in enumerate(lines[:45]):
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
