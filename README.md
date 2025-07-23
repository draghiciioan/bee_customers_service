# Serviciul de Clienți BeeConect

## Prezentare generală

Serviciul de Clienți BeeConect este un microserviciu responsabil pentru gestionarea datelor clienților în cadrul platformei BeeConect. Acesta oferă un API cuprinzător pentru crearea, recuperarea, actualizarea și ștergerea profilurilor clienților, precum și pentru gestionarea datelor legate de clienți, cum ar fi etichetele și notițele. Serviciul include, de asemenea, funcționalități de conformitate GDPR pentru exportul și ștergerea datelor.

Acest microserviciu este conceput pentru a face parte dintr-o arhitectură mai largă de microservicii, integrându-se cu alte servicii precum autentificare, comenzi și programări.

## Caracteristici principale

- **Gestionarea clienților**: Crearea, recuperarea, actualizarea și ștergerea profilurilor clienților
- **Etichetarea clienților**: Adăugarea și gestionarea etichetelor pentru categorizarea clienților (de ex., "VIP", "Blacklist")
- **Notițe despre clienți**: Adăugarea și gestionarea notițelor interne despre clienți
- **Statistici clienți**: Urmărirea și recuperarea statisticilor clienților (comenzi, programări, valoare pe durata vieții)
- **Conformitate GDPR**: Exportul și ștergerea datelor clienților pentru conformitatea cu GDPR
- **Publicarea evenimentelor**: Publicarea evenimentelor către RabbitMQ pentru comunicarea între servicii
- **Limitarea ratei**: Protejarea endpoint-urilor API împotriva abuzurilor prin limitarea ratei
- **Autentificare și autorizare**: Securizarea endpoint-urilor cu control de acces bazat pe roluri

## Arhitectură

Serviciul de Clienți BeeConect este construit folosind următoarele tehnologii:

- **FastAPI**: Framework web de înaltă performanță pentru construirea API-urilor
- **SQLAlchemy**: Toolkit SQL și ORM pentru interacțiuni cu baza de date
- **PostgreSQL**: Bază de date primară pentru stocarea datelor clienților
- **RabbitMQ**: Broker de mesaje pentru publicarea evenimentelor
- **Redis**: Utilizat pentru stocarea evenimentelor eșuate și limitarea ratei
- **Pydantic**: Validarea datelor și gestionarea setărilor
- **Alembic**: Instrument de migrare a bazei de date

Serviciul urmează o arhitectură stratificată:

1. **Stratul API**: Gestionează cererile și răspunsurile HTTP (app/api)
2. **Stratul de servicii**: Conține logica de afaceri (app/services)
3. **Stratul de date**: Gestionează interacțiunile cu baza de date (app/models, app/db)
4. **Stratul de scheme**: Validează și transformă datele (app/schemas)

## Endpoint-uri API

### Endpoint-uri pentru clienți

- `POST /api/customers/`: Creează un nou profil de client
- `GET /api/customers/{customer_id}`: Obține un client după ID
- `GET /api/customers/`: Obține o listă de clienți cu opțiuni de filtrare
- `PATCH /api/customers/{customer_id}`: Actualizează informațiile unui client
- `POST /api/customers/{customer_id}/avatar`: Încarcă și setează imaginea avatar a unui client
- `DELETE /api/customers/{customer_id}`: Șterge un client
- `GET /api/customers/{customer_id}/stats`: Obține statistici pentru un client specific

### Endpoint-uri pentru etichete

- `POST /api/customers/tags/`: Creează o nouă etichetă
- `GET /api/customers/tags/customer/{customer_id}`: Obține toate etichetele pentru un client specific
- `DELETE /api/customers/tags/{tag_id}`: Șterge o etichetă
- `POST /api/customers/{customer_id}/tags`: Creează una sau mai multe etichete pentru un client
- `DELETE /api/customers/{customer_id}/tags/{tag_id}`: Șterge o etichetă de la un client specific

### Endpoint-uri pentru notițe

- `POST /api/customers/{customer_id}/notes`: Creează o notiță pentru un client specific
- `GET /api/customers/{customer_id}/notes`: Recuperează toate notițele pentru un client
- `DELETE /api/customers/{customer_id}/notes/{note_id}`: Șterge o notiță specifică pentru un client

### Endpoint-uri GDPR

- `POST /api/gdpr/export`: Exportă toate datele pentru un client specific
- `POST /api/gdpr/delete`: Șterge toate datele pentru un client specific

### Endpoint-uri pentru sănătate și metrici

- `GET /`: Mesaj de bun venit și informații despre serviciu
- `GET /health`: Endpoint pentru verificarea sănătății
- `GET /metrics`: Endpoint pentru metrici Prometheus

## Modele de date

### Customer (Client)

Entitatea principală care reprezintă un profil de client:

- `id`: Cheie primară UUID
- `user_id`: Referință UUID către un utilizator global
- `business_id`: Referință UUID către o afacere
- `full_name`: Numele complet al clientului
- `email`: Adresa de email a clientului
- `phone`: Numărul de telefon al clientului (opțional)
- `gender`: Genul clientului (masculin, feminin, altul)
- `avatar_url`: URL către imaginea avatar a clientului (opțional)
- `total_orders`: Numărul de comenzi ale clientului
- `total_appointments`: Numărul de programări ale clientului
- `last_order_date`: Data ultimei comenzi a clientului
- `last_appointment_date`: Data ultimei programări a clientului
- `lifetime_value`: Valoarea monetară totală a comenzilor clientului
- `created_at`: Timestamp-ul când a fost creat clientul
- `updated_at`: Timestamp-ul când a fost actualizat ultima dată clientul

### CustomerTag (Etichetă Client)

Reprezintă o etichetă asociată unui client:

- `id`: Cheie primară UUID
- `customer_id`: Cheie străină UUID către Customer
- `label`: Eticheta (de ex., "VIP", "Blacklisted")
- `color`: Cod de culoare pentru afișare UI (opțional)
- `priority`: Întreg pentru ordinea de sortare/afișare
- `created_by`: UUID-ul utilizatorului care a creat eticheta

### CustomerNote (Notiță Client)

Reprezintă o notiță asociată unui client:

- `id`: Cheie primară UUID
- `customer_id`: Cheie străină UUID către Customer
- `content`: Conținutul notiței (maxim 500 caractere)
- `created_by`: UUID-ul administratorului care a creat notița
- `created_at`: Timestamp-ul când a fost creată notița

### CustomerHistory (Istoric Client)

Urmărește date istorice suplimentare despre un client:

- `id`: Cheie primară UUID
- `customer_id`: Cheie străină UUID către Customer
- `first_order_date`: Data primei comenzi a clientului
- `first_appointment_date`: Data primei programări a clientului
- `returned_orders`: Numărul de comenzi returnate de client
- `cancelled_appointments`: Numărul de programări anulate de client

## Configurare

Serviciul poate fi configurat folosind variabile de mediu sau un fișier `.env`. Iată principalele opțiuni de configurare:

### Setări bază de date

- `DATABASE_URL`: String de conexiune PostgreSQL (implicit: "postgresql://postgres:postgres@localhost:5432/bee_customers")

### Setări JWT

- `SECRET_KEY`: Cheie secretă pentru generarea token-urilor JWT (implicit: "supersecretkey")
- `ALGORITHM`: Algoritmul utilizat pentru generarea token-urilor JWT (implicit: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Timpul de expirare al token-ului JWT în minute (implicit: 30)

### Setări CORS

- `CORS_ORIGINS`: Listă separată prin virgulă de origini permise pentru CORS (implicit: "*")

### Servicii externe

- `AUTH_SERVICE_URL`: URL-ul serviciului de autentificare (implicit: "http://localhost:8001")
- `ORDERS_SERVICE_URL`: URL-ul serviciului de comenzi (implicit: "http://localhost:8002")
- `SCHEDULING_SERVICE_URL`: URL-ul serviciului de programări (implicit: "http://localhost:8003")
- `LOG_SERVICE_URL`: URL-ul serviciului de logging (opțional)

### Limitarea ratei

- `CUSTOMER_PATCH_RATE`: Limita de rată pentru endpoint-ul de actualizare client (implicit: "5/minute")

### Setări RabbitMQ

- `RABBITMQ_URL`: String de conexiune RabbitMQ (implicit: "amqp://guest:guest@localhost:5672/")
- `RABBITMQ_EXCHANGE`: Numele exchange-ului RabbitMQ (implicit: "bee.customers.events")

### Setări Redis

- `REDIS_URL`: String de conexiune Redis (implicit: "redis://localhost:6379/0")

## Instalare și configurare

### Cerințe preliminare

- Python 3.12 sau mai nou
- PostgreSQL
- RabbitMQ
- Redis

### Configurare pentru dezvoltare locală

1. Clonează repository-ul:
   ```bash
   git clone https://github.com/your-organization/bee-customers-service.git
   cd bee-customers-service
   ```

2. Creează un mediu virtual și instalează dependențele:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Pe Windows
   pip install poetry
   poetry install
   ```

3. Creează un fișier `.env` cu configurația ta:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bee_customers
   SECRET_KEY=your-secret-key
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   REDIS_URL=redis://localhost:6379/0
   ```

4. Rulează migrările bazei de date:
   ```bash
   alembic upgrade head
   ```

5. Pornește serviciul:
   ```bash
   poetry run python main.py
   ```

   API-ul va fi disponibil la http://localhost:8000.

   > **Notă:** Există o diferență de port între dezvoltarea locală (8000) și implementarea Docker (8007). Exemplele curl din această documentație folosesc portul 8007 pentru a se potrivi cu configurația Docker, dar dacă rulezi serviciul local, va trebui să folosești portul 8000 în schimb.

### Configurare Docker

1. Construiește imaginea Docker:
   ```bash
   docker build -t bee-customers-service .
   ```

2. Rulează containerul:
   ```bash
   docker run -p 8007:8007 \
     -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/bee_customers \
     -e RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/ \
     -e REDIS_URL=redis://redis:6379/0 \
     bee-customers-service
   ```

Dockerfile-ul folosește următoarea configurație:
- Imagine de bază: Python 3.12 slim
- Instalează Poetry și dependențele proiectului (excluzând dependențele de dezvoltare)
- Rulează aplicația folosind Uvicorn pe portul 8007
- Comandă: `poetry run uvicorn main:app --host=0.0.0.0 --port=8007`

## Exemple de utilizare

### Crearea unui client

```bash
curl -X POST "http://localhost:8007/api/customers/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "0712345678",
    "gender": "male",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "business_id": "123e4567-e89b-12d3-a456-426614174001"
  }'
```

### Obținerea unui client

```bash
curl -X GET "http://localhost:8007/api/customers/123e4567-e89b-12d3-a456-426614174002" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Adăugarea unei etichete la un client

```bash
curl -X POST "http://localhost:8007/api/customers/123e4567-e89b-12d3-a456-426614174002/tags" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "label": "VIP",
    "color": "#FFD700"
  }'
```

### Adăugarea unei notițe la un client

```bash
curl -X POST "http://localhost:8007/api/customers/123e4567-e89b-12d3-a456-426614174002/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "Clientul a solicitat un apel de urmărire săptămâna viitoare."
  }'
```

### Exportarea datelor clientului (GDPR)

```bash
curl -X POST "http://localhost:8007/api/gdpr/export" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "business_id": "123e4567-e89b-12d3-a456-426614174001"
  }'
```

## Depanare

### Probleme comune

1. **Erori de conexiune la baza de date**:
   - Asigură-te că PostgreSQL rulează și este accesibil
   - Verifică dacă variabila de mediu `DATABASE_URL` este corectă
   - Verifică permisiunile utilizatorului bazei de date

2. **Erori de conexiune RabbitMQ**:
   - Asigură-te că RabbitMQ rulează și este accesibil
   - Verifică dacă variabila de mediu `RABBITMQ_URL` este corectă
   - Verifică permisiunile utilizatorului RabbitMQ

3. **Erori de conexiune Redis**:
   - Asigură-te că Redis rulează și este accesibil
   - Verifică dacă variabila de mediu `REDIS_URL` este corectă

4. **Erori de autentificare**:
   - Asigură-te că variabila de mediu `SECRET_KEY` este setată corect
   - Verifică dacă token-ul JWT este valid și nu a expirat
   - Verifică dacă utilizatorul are permisiunile necesare

### Loguri

Serviciul folosește logging structurat. Pentru a vizualiza logurile:

```bash
# În modul de dezvoltare
poetry run python main.py

# În modul de producție
tail -f /path/to/logs/bee-customers-service.log
```

## Publicarea evenimentelor

Serviciul publică evenimente către RabbitMQ când anumite acțiuni au loc:

- `customer.created`: Când un nou client este creat
- `customer.updated`: Când un client este actualizat
- `customer.deleted`: Când un client este șters
- `customer.tag.added`: Când o etichetă este adăugată unui client
- `customer.tag.removed`: Când o etichetă este eliminată de la un client
- `customer.note.added`: Când o notiță este adăugată unui client

Aceste evenimente pot fi consumate de alte servicii pentru a reacționa la schimbările din datele clienților.

## Retrimiterea evenimentelor eșuate

Dacă publicarea evenimentelor către RabbitMQ eșuează, evenimentele sunt stocate în Redis. Pentru a retrimite aceste evenimente:

```bash
poetry run python scripts/resend_failed_events.py
```

## Licență

[Specificați licența sub care este lansat serviciul]