# bee_customers_service - Technical Documentation

## 1. Scope, Responsibilities, and Key Concepts

### 🎯 Service Purpose
The `bee_customers_service` manages extended customer profiles within the BeeConect platform, with the primary goals of:
- Centralizing interaction history (orders, appointments)
- Enabling personalized customer experiences
- Supporting businesses in customer retention, loyalty, and segmentation

### 🧱 Core Responsibilities

| Functionality | Description |
|---------------|-------------|
| ✅ Customer Profile | Centralizes personal data: name, email, phone, gender, preferences |
| ✅ Order History | Linked to bee_orders_service |
| ✅ Appointment History | Linked to bee_scheduling_service |
| ✅ Notes and Tags | Visible only to administrators |
| ✅ Customer Statistics | Order count, total value, last order date |
| ✅ GDPR Compliance | Supports export and deletion requests |

### 🔑 Key Concepts

| Concept | Description |
|---------|-------------|
| Customer | Any user who places orders or makes appointments |
| Tag | Configurable label: e.g., "VIP", "Prefers Monday mornings", etc. |
| Internal Note | Short text attached to profile, accessible only by admins |
| History | Aggregation of data from orders and appointments |
| Frequency | Calculable: visits/month, average spending, cancellation rates, etc. |
| GDPR | Customer can request: data export or deletion |

### 🧠 Differentiation from bee_auth_service

| bee_auth_service | bee_customers_service |
|------------------|------------------------|
| Handles authentication | Handles extended profile |
| Email, password, authentication | Name, phone, preferences, tags, statistics |
| JWT and social login | Commercial and behavioral information |

### 🔗 Integration with Other Microservices

| Microservice | Interaction |
|--------------|-------------|
| bee_orders_service | Receives references to completed orders |
| bee_scheduling_service | Receives references to appointments |
| bee_notifications_service | Can personalize messages based on profile |
| bee_marketing_service* | (optional future) segmentation based on tags |

### 🧾 Example Customer Profile

```json
{
  "client_id": "uuid",
  "full_name": "Ana Popescu",
  "email": "ana@email.com",
  "phone": "+40712345678",
  "gender": "female",
  "tags": ["VIP", "Frequent returner"],
  "notes": "Prefers morning slots",
  "total_orders": 12,
  "last_order_date": "2025-07-10"
}
```

## 2. Data Models

### 🧍‍♂️ 2.1 Customer Model
Represents an active customer in a BeeConect business. Extends the minimal profile defined in bee_auth_service.

```python
class Customer(Base):
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Connections
    user_id = Column(UUID(as_uuid=True), unique=False, nullable=False)       # reference to global user
    business_id = Column(UUID(as_uuid=True), nullable=False)                 # local profile per business

    # Personal information
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    gender = Column(Enum("male", "female", "other", name="gender_enum"))
    avatar_url = Column(String(255), nullable=True)  # avatar image link

    # Aggregated statistics
    total_orders = Column(Integer, default=0)
    total_appointments = Column(Integer, default=0)
    last_order_date = Column(Date)
    last_appointment_date = Column(Date)
    lifetime_value = Column(Numeric(10, 2), default=0.00)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "business_id", name="uq_user_per_business"),
    )
```

### 🏷️ 2.2 CustomerTag Model
Custom labels useful for classification, marketing, or internal management.

```python
class CustomerTag(Base):
    __tablename__ = "customer_tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    label = Column(String(50), nullable=False)  # e.g.: "VIP", "Blacklisted"
```

✅ Possible extensions: color, priority, created_by

### 📝 2.3 CustomerNote Model
Confidential notes written by administrators, visible only in the backend.

```python
class CustomerNote(Base):
    __tablename__ = "customer_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    content = Column(String(500), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=False)  # admin user_id
    created_at = Column(DateTime, default=datetime.utcnow)
```

📌 Ideal for situations like:
- "Has been late 3 times"
- "Prefers morning appointments"

### 🧾 2.4 CustomerHistory Model (optional)
Either local cache or aggregated from external microservices for rapid UI.

```python
class CustomerHistory(Base):
    __tablename__ = "customer_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    first_order_date = Column(Date)
    first_appointment_date = Column(Date)
    returned_orders = Column(Integer, default=0)
    cancelled_appointments = Column(Integer, default=0)
```

### 🔐 Design Logic: user_id + business_id
The same person can have completely different behaviors, tags, and history depending on the business.

| Example | Business A (salon) | Business B (clinic) |
|---------|-------------------|---------------------|
| Tag | "VIP", "subscription" | "no-show", "opportunist" |
| Statistics | 20 visits / 6 months | 2 cancelled appointments |
| Notes | "prefers Friday 9 AM" | "refuses card payment" |

### 🎨 Avatar (image)
- Can be uploaded directly by user (e.g., URL to S3/Cloudinary)
- Or automatically generated (random avatar + initials)
- Or default fallback (icon 👤)

### 🔁 Other Considerations:
| Detail | Recommended Decision |
|--------|----------------------|
| Email/phone synchronization | Save from auth on first order or appointment |
| Account deletion | Delete profile, tags, notes |
| GDPR compliant | Provide export endpoint + deletion on customer request |
| Indexes | On business_id, user_id, full_name, phone |

## 3. REST Endpoints

This section defines all REST interfaces of the service, organized by clear functionalities:
- customer profile management
- avatar upload/update
- tags, notes, statistics
- advanced listing and searching

### 👤 3.1 Customer Profile Creation/Update

**POST /customers**  
Creates customer profile for a specific business.
```json
{
  "user_id": "uuid",
  "business_id": "uuid",
  "full_name": "Ana Popescu",
  "email": "ana@email.com",
  "phone": "+40712345678",
  "gender": "female"
}
```

**PATCH /customers/{id}**  
Allows data updates:
```json
{
  "phone": "+40798765432",
  "avatar_url": "https://cdn.myapp.com/avatars/ana.jpg"
}
```

### 🖼️ 3.2 Avatar Image Upload

**POST /customers/{id}/avatar** (multipart/form-data)  
Receives .jpg/.png file, saves it to S3/CDN and updates avatar_url.  
📌 Secured: only the customer or administrators can modify the avatar.

### 🔍 3.3 Customer Search (admin)

**GET /customers?business_id=uuid&query=ana**  
Allows searching by: name, email, phone  
Returns paginated results + useful UI data.

### 🏷️ 3.4 Tag Management

**POST /customers/{id}/tags**
```json
{ "label": "VIP" }
```
📌 Multiple tags can be added (e.g., ["VIP", "Blacklisted"]).

**DELETE /customers/{id}/tags/{tag_id}**

### 📝 3.5 Note Management

**POST /customers/{id}/notes**
```json
{
  "content": "Customer prefers morning slots",
  "created_by": "uuid_admin"
}
```

**GET /customers/{id}/notes**  
📌 Only business admins can view.

### 📊 3.6 Customer Statistics

**GET /customers/{id}/stats**
```json
{
  "total_orders": 12,
  "total_appointments": 8,
  "lifetime_value": 2750.00,
  "last_order_date": "2025-07-15"
}
```
📌 Can be aggregated from external microservices (bee_orders_service, bee_scheduling_service) on request or cron.

### 🔐 Access and Permissions

| Endpoint | Who has access? |
|----------|----------------|
| POST /customers | Only internal services (auth, orders, etc.) |
| PATCH /customers | The customer or business admins |
| GET /customers | Only admin_business and admin_manager |
| POST /tags / notes | Exclusively administrators |
| GET /stats | Admins or customer for self-view |

## 4. RabbitMQ Events

These events are essential for integration into the distributed BeeConect system:
- synchronize changes in other microservices (e.g., orders, notifications)
- trigger automatic actions (e.g., welcome email, data revalidation)
- help with traceability and audit

### ⚙️ General RabbitMQ Configuration

| Parameter | Value |
|-----------|-------|
| Exchange | bee.customers.events |
| Type | topic |
| Routing keys | v1.customer.* |
| Message format | JSON |

### 📤 4.1 Event: v1.customer.created
Automatically sent after creating a new profile.

```json
{
  "event": "v1.customer.created",
  "customer_id": "uuid",
  "user_id": "uuid",
  "business_id": "uuid",
  "full_name": "Ana Popescu",
  "email": "ana@email.com",
  "created_at": "2025-07-21T14:00:00Z"
}
```

➡️ Useful for:
- bee_notifications_service → send welcome email
- bee_log_service → customer creation traceability

### ✏️ 4.2 Event: v1.customer.updated
Sent after important modifications (e.g., phone, avatar, preferences).

```json
{
  "event": "v1.customer.updated",
  "customer_id": "uuid",
  "fields_changed": ["phone", "avatar_url"],
  "updated_at": "2025-07-21T15:25:00Z"
}
```

➡️ Useful for:
- updating cache in internal UI
- audit in bee_log_service

### 🏷️ 4.3 Event: v1.customer.tagged
Sent when a new tag is added (e.g., "VIP").

```json
{
  "event": "v1.customer.tagged",
  "customer_id": "uuid",
  "tag": "VIP",
  "created_by": "admin_id",
  "business_id": "uuid"
}
```

➡️ Useful for:
- bee_marketing_service (future): trigger campaigns
- bee_notifications_service: send personalized messages

### 📝 4.4 Event: v1.customer.note_added
Internal notes added → useful only for logs or audit.

```json
{
  "event": "v1.customer.note_added",
  "customer_id": "uuid",
  "created_by": "admin_id",
  "note": "Prefers morning appointments",
  "created_at": "2025-07-21T16:00:00Z"
}
```

➡️ Useful for:
- bee_log_service: keep note history

### 🧠 Best Practices

| Technique | Benefit |
|-----------|---------|
| trace_id in all messages | full flow traceability from frontend to database |
| versioning (v1.) | can evolve events without breaking existing consumers |
| extra_payload per context | can add additional fields without impact |

## 5. Security, Validations, and Traceability

This section defines all essential measures for:
- preventing unauthorized access
- validating data before saving
- complete traceability of all actions

### 🔐 5.1 Authentication & Authorization

| Action | Who is allowed? |
|--------|----------------|
| GET /customers?business_id=... | Only admin_business, admin_manager |
| GET /customers/{id} | The customer themselves or administrators |
| PATCH /customers/{id} | The customer themselves or administrators |
| POST /tags, POST /notes | Exclusively for administrators |
| POST /avatar | Only the customer themselves or business admin |
| GET /stats | Only the customer themselves or admins |

📌 Valid JWT token + role verification + business_id relevant to context

### 📏 5.2 Data Validations

| Check | Detail |
|-------|--------|
| Valid email | Format + unique per global user (from auth) |
| Valid phone | Regex for +40, 07xx etc. (optional only) |
| Avatar URL | MIME type verification + allowed extension (jpg, png, webp) |
| Unique tag | No duplicates like "VIP" twice |
| Note: max 500 characters | Explicit content limitation |

### 🔎 5.3 Complete Traceability
All actions are logged and automatically sent to bee_log_service, including:

| Event | Saved Information |
|-------|------------------|
| Customer creation | user_id, business_id, IP, browser |
| Profile edit | fields_changed, user_id, date/time |
| Tag addition | tag_name, admin_id, timestamp |
| Note addition | note_content, admin_id |
| Avatar modification | old vs. new URL |

📦 Standardized format with trace_id and request_id (from API Gateway)

### 🛡️ 5.4 Anti-Abuse Measures

| Problem | Proposed Solution |
|---------|------------------|
| Profile flood (repeated update) | Rate-limit on PATCH endpoint |
| Avatar spam | Extension verification + size < 1MB |
| Offensive notes | Regex/filter unacceptable language (optional) |

### 🔄 5.5 Synchronization with bee_auth_service

- Data from auth (email, name) can be retrieved on first interaction
- If customer updates email/phone, we also notify auth_service
- user_id is immutable after profile creation

## 6. Production Preparation

This section covers everything needed for the service to work flawlessly in production: testing, CI/CD, logging, monitoring, Docker.

### 🔁 6.1 CI/CD (GitHub Actions)

```yaml
name: CI Customers Service

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: |
          pip install poetry
          poetry install
          poetry run pytest --cov=bee_customers_service
```

✅ Includes code validation, test execution + coverage measurement.

### 🧪 6.2 Automated Testing

| Test Type | What We Check |
|-----------|--------------|
| Valid profile creation | Complete data is saved |
| Search by name/email | Returns paginated results |
| Tag addition | No duplicates allowed |
| Confidential notes | Visible only to admins |
| Invalid avatars | Are rejected (mime, size, extension) |
| PATCH ratelimit | Flooding blocked |

🔧 Tooling:
- pytest, pytest-asyncio
- httpx.AsyncClient
- freezegun for date testing

### 🐳 6.3 Docker & Docker Compose

**Dockerfile**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-dev
CMD ["poetry", "run", "uvicorn", "main:app", "--host=0.0.0.0", "--port=8007"]
```

**docker-compose.yml**
```yaml
services:
  bee_customers_service:
    build: .
    ports:
      - "8007:8007"
    depends_on:
      - rabbitmq
      - postgres
    environment:
      - DATABASE_URL=...
      - RABBITMQ_URL=...
```

### 📊 6.4 Monitoring (Prometheus)
Example with prometheus-fastapi-instrumentator:

| Metric | Description |
|--------|-------------|
| customers_created_total | Total number of profiles created |
| notes_created_total | Total number of notes added |
| tagged_customers_total | Total number of tagged customers |
| api_response_duration | Endpoint response time |

### 🪵 6.5 Structured Logging (for Loki/ELK)

```python
logger.info("Customer created", extra={
    "user_id": user.id,
    "customer_id": customer.id,
    "business_id": customer.business_id,
    "trace_id": trace_id,
})
```

📌 Each log has: timestamp, level, service_name, trace_id

### ✅ Other Best Practices

| Measure | Benefit |
|---------|---------|
| /healthcheck | Integrable in Docker/K8s orchestrator |
| trace_id from API Gateway | Cross-microservice traceability |
| RabbitMQ retry | With temporary backup in Redis/local storage |
| Native rate limit & anti-flood | Protection per IP/token, scalable in gateway |