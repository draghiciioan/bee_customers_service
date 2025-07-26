# BeeConnect Customers Service

> **Versiune**: 0.1.0
> **Ultima actualizare**: 26 iulie 2025

## Cuprins

1. [Introducere](#introducere)
2. [Tehnologii cheie](#tehnologii-cheie)
3. [Structura proiectului](#structura-proiectului)
4. [Instalare și rulare rapidă](#instalare-și-rulare-rapidă)
5. [Variabile de mediu](#variabile-de-mediu)
6. [Fluxuri principale](#fluxuri-principale)
7. [Baza de date](#baza-de-date)
8. [API Reference](#api-reference)
9. [Evenimente RabbitMQ](#evenimente-rabbitmq)
10. [Rate‑limiting & Securitate](#rate‑limiting--securitate)
11. [Ghid Dev & Testare](#ghid-dev--testare)
12. [Ghid Deploy (Docker & Kubernetes)](#ghid-deploy-docker--kubernetes)
13. [CI/CD](#cicd)
14. [Integrare React + Vite](#integrare-react--vite)
15. [FAQ](#faq)

---

## Introducere

`bee_customers_service` este microserviciul care gestionează **profilurile clienților** din ecosistemul **BeeConnect**. Responsabilități principale:

* CRUD complet pentru clienți (create / read / update / delete).
* Etichete (tags) și notițe (notes) interne pentru segmentare & context.
* Statistici agregate (valoare pe viață, număr comenzi/rezervări etc.).
* Conformitate **GDPR** (export & dreptul de a fi uitat).
* Serviciu **event‑driven** — publică evenimente pe RabbitMQ când apar modificări.
* Protecție anti‑abuz prin rate‑limiting adaptiv (SlowAPI+Redis).

---

## Tehnologii cheie

| Tehnologie                    | Rol                                       |
| ----------------------------- | ----------------------------------------- |
| **FastAPI 0.116**             | Framework API REST                        |
| **SQLAlchemy 2 + Alembic**    | ORM & migrații DB                         |
| **PostgreSQL**                | Baza de date principală                   |
| **Redis**                     | Rate‑limiting & coadă fallback evenimente |
| **aio‑pika**                  | Publicare evenimente RabbitMQ             |
| **Prometheus Instrumentator** | Metrici `/metrics`                        |
| **slowapi**                   | Rate‑limit                                |
| **pytest**                    | Teste unit & integrare (≈ 90 % coverage)  |
| **Docker & K8s**              | Deploy                                    |

---

## Structura proiectului

```text
.
├── app/
│   ├── api/            # Rute FastAPI (customers, notes, tags, gdpr)
│   ├── core/           # Config globală, rate‑limit, auth deps
│   ├── db/             # Session & Base
│   ├── models/         # SQLAlchemy models (customer, tag, note, history)
│   ├── schemas/        # Pydantic I/O
│   ├── services/       # Business logic & event publisher
│   └── main.py         # Entry‑point ASGI
├── tests/              # 100+ teste
├── alembic/            # Migrații DB
└── Dockerfile          # Imagine producție
```

---

## Instalare și rulare rapidă

```bash
# 1. Clonare & build imagine
git clone https://github.com/beeconnect/bee_customers_service.git
cd bee_customers_service
docker build -t bee-customers-service .

# 2. Pornește dependențe
docker compose up -d postgres redis rabbitmq

# 3. Rulează microserviciul
docker run -p 8002:8000 --env-file .env.local bee-customers-service
```

Accesează Swagger la `http://localhost:8002/docs`.

---

## Variabile de mediu

| Nume                  | Implicit                                                              | Descriere                                       |
| --------------------- | --------------------------------------------------------------------- | ----------------------------------------------- |
| `DATABASE_URL`        | `postgresql+asyncpg://postgres:postgres@localhost:5432/bee_customers` | Conexiune DB                                    |
| `RABBITMQ_URL`        | `amqp://guest:guest@localhost:5672/`                                  | Broker mesaje                                   |
| `RABBITMQ_EXCHANGE`   | `bee.customers.events`                                                | Exchange events                                 |
| `REDIS_URL`           | `redis://localhost:6379/0`                                            | Cache & queue fallback                          |
| `CUSTOMER_PATCH_RATE` | `5/minute`                                                            | Limitare PATCH per client                       |
| `CORS_ORIGINS`        | `*`                                                                   | Origini permise                                 |
| `AUTH_SERVICE_URL`    | `http://auth:8001`                                                    | Validare token                                  |
| ...                   |                                                                       | Vezi `app/core/config.py` pentru lista completă |

---

## Fluxuri principale

### Creare client

```mermaid
sequenceDiagram
  participant FE as Front‑end
  participant CS as Customers Service
  participant DB as PostgreSQL
  FE->>CS: POST /v1/customers (body)
  CS->>DB: INSERT customer
  CS-->>FE: 201 CustomerResponse
  CS--)Rabbit: CustomerCreatedEvent
```

### Actualizare profil + rate‑limit

```mermaid
sequenceDiagram
  FE->>CS: PATCH /v1/customers/{id} (JSON Patch)
  CS->>Redis: Check & increment rate
  alt > CUSTOMER_PATCH_RATE
    CS-->>FE: 429 Too Many Requests
  else allowed
    CS->>DB: UPDATE customer
    CS--)Rabbit: CustomerUpdatedEvent
    CS-->>FE: 200 CustomerResponse
  end
```

### Export GDPR

```mermaid
sequenceDiagram
  FE->>CS: POST /v1/customers/gdpr/export {user_id}
  CS->>DB: gather data
  CS-->>FE: 200 {zip_url}
```

---

## Baza de date

```mermaid
erDiagram
  customer ||--o{ customer_note : has
  customer ||--o{ customer_tag : has
  customer ||--|| customer_history : extends

  customer {
    UUID id PK
    UUID user_id
    UUID business_id
    VARCHAR full_name
    VARCHAR email
    VARCHAR phone
    ENUM gender
    VARCHAR avatar_url
    INT total_orders
    NUM lifetime_value
    TIMESTAMP created_at
    TIMESTAMP updated_at
  }
  customer_note {
    UUID id PK
    UUID customer_id FK
    TEXT content
    TIMESTAMP created_at
  }
  customer_tag {
    UUID id PK
    UUID customer_id FK
    VARCHAR name
  }
  customer_history {
    UUID id PK
    UUID customer_id FK
    DATE first_order_date
    DATE last_order_date
    INT returned_orders
  }
```

---

## API Reference

> Prefix **/v1/customers** (secured prin Bearer JWT).

| Metodă    | Path                             | Descriere                               | Rol necesar           |
| --------- | -------------------------------- | --------------------------------------- | --------------------- |
| `POST`    | `/`                              | Creează client                          | `internal_service`    |
| `GET`     | `/{customer_id}`                 | Returnează client                       | `customer` \| `admin` |
| `GET`     | `/`                              | Listă paginată + filtru business/search | `admin`               |
| `PATCH`   | `/{customer_id}`                 | Update (JSON Patch)                     | `admin`               |
| `DELETE`  | `/{customer_id}`                 | Șterge definitv                         | `admin`               |
| `POST`    | `/{customer_id}/avatar`          | Upload avatar (multipart)               | `admin`               |
| `GET`     | `/{customer_id}/stats`           | Statistici agregate                     | `admin`               |
| **Notes** |                                  |                                         |                       |
| `POST`    | `/{customer_id}/notes`           | Creează notiță                          | `admin`               |
| `GET`     | `/{customer_id}/notes`           | Listă notițe                            | `admin`               |
| `DELETE`  | `/{customer_id}/notes/{note_id}` | Șterge notiță                           | `admin`               |
| **Tags**  |                                  |                                         |                       |
| `POST`    | `/tags`                          | Creează tag global                      | `admin`               |
| `GET`     | `/tags`                          | Listă tag‑uri                           | `admin`               |
| `POST`    | `/{customer_id}/tags`            | Atașează tag‑uri (batch)                | `admin`               |
| **GDPR**  |                                  |                                         |                       |
| `POST`    | `/gdpr/export`                   | Exportă date client                     | `customer`            |

### Exemplu: `PATCH /v1/customers/{id}`

```http
PATCH /v1/customers/72e9...
Content-Type: application/json-patch+json

[
  {"op": "replace", "path": "/full_name", "value": "Ionuț Popescu"},
  {"op": "add", "path": "/tags/-", "value": "VIP"}
]
```

---

## Evenimente RabbitMQ

| Event                  | Routing key             | Trigger       |
| ---------------------- | ----------------------- | ------------- |
| `CustomerCreatedEvent` | `customers.created`     | La creare     |
| `CustomerUpdatedEvent` | `customers.updated`     | La update     |
| `CustomerDeletedEvent` | `customers.deleted`     | La ștergere   |
| `GDPRExportRequested`  | `customers.gdpr.export` | Cerere export |

Publicare (simplu):

```python
await publish_event(
    "customers.updated",
    {"customer_id": str(id), "changes": diff},
    trace_id,
)
```

---

## Rate‑limiting & Securitate

* **slowapi** + **Redis** → rulează `CUSTOMER_PATCH_RATE` (default 5/min).
* Dependință `require_admin`/`require_customer_or_admin` în `app/api/dependencies.py` asigură RBAC.
* CORS & Security Headers configurate default.

---

## Ghid Dev & Testare

```bash
poetry install --with dev
pre-commit run --all-files
pytest -q  # >90% coverage
```

---

## Ghid Deploy (Docker & Kubernetes)

### Docker Compose

```yaml
version: "3"
services:
  customers:
    build: .
    env_file: .env.prod
    depends_on: [postgres, redis, rabbitmq]
    ports: ["8002:8000"]
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: customers
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
  redis:
    image: redis:7-alpine
  rabbitmq:
    image: rabbitmq:3-management
```

### Fragmente Helm values

```yaml
customersService:
  image:
    repository: ghcr.io/beeconnect/customers
    tag: 0.1.0
  env:
    DATABASE_URL: "postgresql://..."
    RABBITMQ_URL: "amqp://..."
  probes:
    readiness: "/health"
    liveness: "/health"
  resources:
    limits:
      cpu: "250m"
      memory: "256Mi"
```

---

## CI/CD

* Workflow `ci.yml` → lint → tests → docker build & push → Helm release automat.
* Versiuni semantice cu tag Git (`v0.1.0`). Rollback: `helm rollback customers N`.

---

## Integrare React + Vite

### 1. Instalează dependențe

```bash
npm i axios react-query jwt-decode
```

### 2. Hook `useCustomers.ts`

```ts
import { useQuery, useMutation, useQueryClient } from "react-query";
import axios from "axios";

export function useCustomers() {
  const qc = useQueryClient();
  const list = useQuery(["customers"], async () => {
    const { data } = await axios.get("/v1/customers?limit=50");
    return data;
  });

  const update = useMutation(
    ({ id, patch }: { id: string; patch: any[] }) =>
      axios.patch(`/v1/customers/${id}`, patch, {
        headers: { "Content-Type": "application/json-patch+json" },
      }),
    {
      onSuccess: () => qc.invalidateQueries(["customers"]),
    }
  );

  return { list, update };
}
```

### 3. Tabel interactiv (Tailwind + TanStack Table)

```tsx
function CustomersTable() {
  const { list, update } = useCustomers();
  if (list.isLoading) return <div>Loading...</div>;

  return (
    <table className="w-full border">
      <thead className="bg-gray-100">
        <tr>
          <th className="p-2">Nume</th>
          <th>Email</th>
          <th>Telefon</th>
          <th>Acțiuni</th>
        </tr>
      </thead>
      <tbody>
        {list.data.map((c) => (
          <tr key={c.id} className="border-t">
            <td className="p-2">{c.full_name}</td>
            <td>{c.email}</td>
            <td>{c.phone}</td>
            <td>
              <button
                className="text-blue-600"
                onClick={() =>
                  update.mutate({
                    id: c.id,
                    patch: [
                      { op: "replace", path: "/full_name", value: `${c.full_name} ✅` },
                    ],
                  })
                }
              >
                Mark OK
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

---

## FAQ

| Întrebare                            | Răspuns                                                                     |
| ------------------------------------ | --------------------------------------------------------------------------- |
| **De ce primesc 429 la PATCH?**      | Ai depășit `CUSTOMER_PATCH_RATE`. Crește pragul sau implementează back‑off. |
| **Cum adaug un câmp nou în profil?** | Creează coloană + Alembic migrație, actualizează model & schema.            |
| **Pot extinde filtrele de căutare?** | Da, adaptează `CustomerService.get_customers` și adaugă query params.       |

---

> Feedback binevenit! Trimite un PR sau deschide un issue 😉
