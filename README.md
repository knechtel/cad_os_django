# CadApp API

API REST em Django REST Framework para cadastro de clientes e aparelhos, usando SQLite local.

## Executar

O ambiente virtual do projeto fica em `.venv`:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

A API fica em `http://127.0.0.1:8000/api/`. O Django REST Framework também disponibiliza uma interface navegável no navegador.

## Endpoints

| Método | Endpoint | Ação |
|---|---|---|
| GET, POST | `/api/clientes/` | Listar e cadastrar clientes |
| GET, PUT, PATCH, DELETE | `/api/clientes/{id}/` | Consultar, editar e excluir cliente |
| POST | `/api/clientes/importar/` | Importar vários clientes por JSON |
| GET, POST | `/api/aparelhos/` | Listar e cadastrar aparelhos |
| GET, PUT, PATCH, DELETE | `/api/aparelhos/{id}/` | Consultar, editar e excluir aparelho |
| POST | `/api/aparelhos/importar/` | Importar vários aparelhos por JSON |
| GET | `/api/clientes/{id}/relatorio.pdf/` | Baixar relatório PDF do cliente |

Clientes incluem seus aparelhos, quantidade e valor total no retorno. Aparelhos podem ser filtrados por cliente com `?cliente={id}`. Listas aceitam busca por `?search=termo` e ordenação com `?ordering=nome` (ou `-nome`). A paginação padrão retorna 20 itens por página.

### Exemplo de cadastro

```json
POST /api/clientes/
{
  "nome": "Maria da Silva",
  "telefone": "11999999999",
  "cpf": "123.456.789-00",
  "endereco": "Rua das Flores, 10"
}
```

```json
POST /api/aparelhos/
{
  "cliente": 1,
  "modelo": "Galaxy S24",
  "marca": "Samsung",
  "numero_serial": "ABC123",
  "descricao": "Aparelho para avaliação",
  "preco": "2500.00",
  "createdAt": 1735689600000,
  "deliveredAt": 1735776000000
}
```

### Importação em lote de aparelhos

Envie uma lista de aparelhos diretamente (ou dentro da propriedade `aparelhos`). Cada item usa os mesmos campos do cadastro individual, incluindo o ID do cliente. A operação é atômica: se algum item for inválido, nenhum aparelho é importado.

```json
POST /api/aparelhos/importar/
[
  {"cliente": 1, "modelo": "Galaxy S24", "marca": "Samsung", "preco": "2500.00"},
  {"cliente": 1, "modelo": "iPhone 15", "marca": "Apple", "preco": "3200.00"}
]
```

Também é aceito o formato `{ "aparelhos": [ ... ] }`. Em caso de sucesso, a API retorna os aparelhos criados com status `201`.

### Importação em lote de clientes

Envie uma lista de clientes diretamente ou dentro da propriedade `clientes`. O endpoint aceita os campos internos do cadastro individual ou o formato exportado pelo aplicativo (`name`, `phone`, `address` e `devices`). Os aparelhos aninhados são importados junto com cada cliente. CPFs devem ser únicos tanto entre os clientes existentes quanto dentro da própria lista.

```json
POST /api/clientes/importar/
[
  {"nome": "Maria da Silva", "telefone": "11999999999", "cpf": "123.456.789-00"},
  {"nome": "João Souza", "telefone": "11988888888", "endereco": "Rua das Flores, 10"}
]
```

Também é aceito o formato `{ "clientes": [ ... ] }`. A importação é atômica: se algum item for inválido, nenhum cliente é criado. Em caso de sucesso, a API retorna os clientes criados com status `201`.

No formato exportado, os campos são convertidos assim: `name` → `nome`, `phone` → `telefone`, `address` → `endereco`; em cada `device`, `model`, `brand`, `serialNumber`, `description`, `price`, `createdAt` e `deliveredAt` são convertidos para os campos de aparelho correspondentes. Os IDs recebidos, `customerId`, `devicesCount`, `totalValue`, `formattedCreatedAt`, `isDelivered` e `formattedDeliveredAt` não são gravados: IDs e totais são gerados/calculados pela API, e o estado de entrega é representado por `deliveredAt`.

```json
POST /api/clientes/importar/
[
  {
    "id": 1,
    "name": "Maiquel Knechtel",
    "phone": "51993501980",
    "cpf": "01637948042",
    "address": "coca Barcelos",
    "devices": [
      {
        "model": "model 2",
        "brand": "Lenovo",
        "serialNumber": "654676",
        "description": "não liga",
        "price": 188.0,
        "createdAt": 1793734167443,
        "deliveredAt": 1794101982229
      }
    ]
  }
]
```

## Campos

- Cliente: `nome`, `telefone`, `cpf`, `endereco`.
- Aparelho: `cliente`, `modelo`, `marca`, `numero_serial`, `descricao`, `preco`, `createdAt`, `deliveredAt`. Os dois últimos são inteiros de 64 bits (long) e podem ser nulos.

Excluir um cliente também exclui seus aparelhos associados. O CPF é opcional, mas quando informado deve ser único.
# cad_os_django
