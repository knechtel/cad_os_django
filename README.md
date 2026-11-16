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
| GET, POST | `/api/aparelhos/` | Listar e cadastrar aparelhos |
| GET, PUT, PATCH, DELETE | `/api/aparelhos/{id}/` | Consultar, editar e excluir aparelho |
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

## Campos

- Cliente: `nome`, `telefone`, `cpf`, `endereco`.
- Aparelho: `cliente`, `modelo`, `marca`, `numero_serial`, `descricao`, `preco`, `createdAt`, `deliveredAt`. Os dois últimos são inteiros de 64 bits (long) e podem ser nulos.

Excluir um cliente também exclui seus aparelhos associados. O CPF é opcional, mas quando informado deve ser único.
# cad_os_django
