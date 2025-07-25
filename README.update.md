# Actualizare Serviciu Clienți BeeConect

## Problema Rezolvată

Problema cu `bbe_customers_service` care nu funcționa corect în mediul beeconect-dev a fost rezolvată. Problema era că migrările bazei de date nu erau executate la pornirea containerului, astfel schema bazei de date nu era creată.

## Modificări Efectuate

1. A fost creat un script de pornire (`entrypoint.sh`) care:
   - Așteaptă ca PostgreSQL să fie pregătit
   - Rulează migrările bazei de date folosind Alembic
   - Pornește aplicația folosind Uvicorn

2. A fost modificat Dockerfile-ul pentru:
   - A adăuga Alembic ca dependență
   - A face scriptul de pornire executabil
   - A utiliza scriptul de pornire în loc de a rula direct Uvicorn

## Cum să Testați

1. Reconstruiți containerul pentru serviciul de clienți:
   ```
   cd C:\Users\jhony\Desktop\BeeConect\beeconect-dev
   make customers-service
   ```

2. Verificați logurile pentru a vă asigura că migrările sunt executate:
   ```
   docker logs -f beeconect-dev-customers-service-1
   ```

   Ar trebui să vedeți un output similar cu:
   ```
   Waiting for PostgreSQL to be ready...
   Running database migrations...
   INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
   INFO  [alembic.runtime.migration] Will assume transactional DDL.
   INFO  [alembic.runtime.migration] Running upgrade  -> 8c70b4aaf501, initial
   Starting the application...
   INFO:     Started server process [1]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8007 (Press CTRL+C to quit)
   ```

3. Testați endpoint-urile API:
   ```
   curl http://localhost:8016/api/customers
   ```

## Note Suplimentare

Dacă întâmpinați probleme cu scriptul de pornire, este posibil să fie necesară asigurarea că acesta are terminațiile de linie corecte (LF în loc de CRLF) atunci când rulează într-un container Linux. Puteți rezolva acest lucru rulând:

```
dos2unix entrypoint.sh
```

Sau setând Git să gestioneze automat terminațiile de linie:

```
git config --global core.autocrlf input
```

Apoi clonați din nou repository-ul sau verificați din nou fișierul.