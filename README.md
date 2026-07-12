# Ticket Reservation API

**Backend PPM 2026 — Progetto d'esame**

- **Studente:** Lucas Henrique Melo Alves
- **Matricola:** 7110826
- **Tipo di progetto:** REST API (traccia 4 — *Ticket Reservation API*)
- **Framework:** Django + Django REST Framework (JWT con SimpleJWT)
- **Deployment:** `[inserisci qui l'URL di Render, es. https://ticket-reservation-api.onrender.com]`

---

## 1. Descrizione

API RESTful per la prenotazione di biglietti per eventi. Gli utenti anonimi
possono consultare gli eventi e la disponibilità dei posti; gli utenti
registrati possono prenotare, modificare e annullare i propri biglietti; gli
organizzatori possono creare e gestire i propri eventi e vedere la lista dei
partecipanti. L'autenticazione è basata su token JWT e i permessi sono
applicati **a livello di endpoint**, non solo descritti.

## 2. Funzionalità per ruolo

**Anonimo (non autenticato)**

- Elenco e dettaglio eventi (con ricerca per nome/luogo).
- Disponibilità posti di un evento (endpoint dedicato).

**Utente registrato (`USER`)**

- Registrazione e login (JWT).
- Creazione, lettura, modifica (solo riduzione quantità) e cancellazione delle
  **proprie** prenotazioni.
- Annullamento di una prenotazione (endpoint di stato che libera i posti).

**Organizzatore (`ORGANIZER`)**

- Tutto ciò che può fare un utente registrato.
- Creazione, modifica e cancellazione dei **propri** eventi.
- Visualizzazione della lista partecipanti dei propri eventi.

**Amministratore (`ADMIN` / superuser)**

- Accesso completo, incluso il pannello Django Admin (`/admin/`).

## 3. Installazione locale

```bash
# 1. Clona il repository
git clone <URL_DEL_REPO>
cd ticket-reservation-api

# 2. Crea e attiva un virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Installa le dipendenze
pip install -r requirements.txt

# 4. (Opzionale) Il DB db.sqlite3 è già incluso e pre-popolato.
#    Per ricrearlo da zero:
#      python manage.py migrate
#      python manage.py seed_demo

# 5. Avvia il server
python manage.py runserver
```

Base URL locale: `http://127.0.0.1:8000/`

Il database SQLite incluso è **`db.sqlite3`** e contiene già eventi,
prenotazioni e account demo. Il progetto è comunque ricreabile da un database
vuoto con `migrate` + `seed_demo`.

## 4. Account demo

> Credenziali create solo per la valutazione (nessun dato reale/personale).

| Username | Password | Ruolo |
|---|---|---|
| `admin_demo` | `admin12345` | Amministratore / superuser |
| `organizer_demo` | `organizer12345` | Organizzatore |
| `user_demo` | `user12345` | Utente standard |
| `user2_demo` | `user12345` | Utente standard (per testare le azioni vietate) |

## 5. Documentazione degli endpoint

Base URL locale: `http://127.0.0.1:8000` — Base URL online: vedi sezione Deploy.

| Metodo | URL | Auth | Ruolo | Body (esempio) | Descrizione |
|---|---|---|---|---|---|
| POST | `/api/auth/register/` | No | — | `{"username","email","password","role","phone_number"}` | Registrazione, restituisce token JWT |
| POST | `/api/auth/login/` | No | — | `{"username","password"}` | Login, restituisce `access` + `refresh` |
| POST | `/api/auth/token/refresh/` | No | — | `{"refresh"}` | Rinnova l'access token |
| GET | `/api/auth/me/` | Sì | any | — | Profilo dell'utente autenticato |
| GET | `/api/events/` | No | any | — | Lista eventi (`?search=`, `?location=`) |
| POST | `/api/events/` | Sì | ORGANIZER/ADMIN | `{"name","location","start_time","end_time","total_tickets","price"}` | Crea un evento |
| GET | `/api/events/<id>/` | No | any | — | Dettaglio evento |
| PUT/PATCH | `/api/events/<id>/` | Sì | owner ORGANIZER/ADMIN | campi evento | Modifica evento |
| DELETE | `/api/events/<id>/` | Sì | owner ORGANIZER/ADMIN | — | Elimina evento |
| GET | `/api/events/<id>/availability/` | No | any | — | Disponibilità posti |
| GET | `/api/events/<id>/attendees/` | Sì | owner ORGANIZER/ADMIN | — | Lista partecipanti (endpoint per ruolo) |
| GET | `/api/reservations/` | Sì | owner | — | Le proprie prenotazioni |
| POST | `/api/reservations/` | Sì | USER+ | `{"event","quantity"}` | Crea prenotazione (scala i posti) |
| GET | `/api/reservations/<id>/` | Sì | owner | — | Dettaglio prenotazione |
| PATCH | `/api/reservations/<id>/` | Sì | owner | `{"quantity"}` | Riduce la quantità (aumento vietato) |
| DELETE | `/api/reservations/<id>/` | Sì | owner | — | Elimina prenotazione e libera i posti |
| POST | `/api/reservations/<id>/cancel/` | Sì | owner | — | Annulla (stato `CANCELLED`) e libera i posti |

### Esempio di risposta — `GET /api/events/1/`

```json
{
  "id": 1,
  "name": "Firenze Jazz Night",
  "description": "An evening of live jazz in the heart of Florence.",
  "location": "Teatro Verdi, Firenze",
  "start_time": "2026-07-24T09:25:39Z",
  "end_time": "2026-07-24T12:25:39Z",
  "price": "25.00",
  "total_tickets": 120,
  "available_tickets": 115,
  "is_sold_out": false,
  "organizer": "organizer_demo",
  "created_at": "2026-07-09T13:25:39Z"
}
```

### Esempio di errore di validazione — `POST /api/reservations/`

```json
{ "quantity": ["Sono disponibili solo 3 biglietti per 'Firenze Jazz Night'."] }
```

## 6. Workflow di test con HTTPie

Installazione: <https://httpie.io/> — `pip install httpie`

Imposta la base URL (locale o deploy):

```bash
BASE=http://127.0.0.1:8000        # oppure: BASE=https://<il-tuo-servizio>.onrender.com
```

**1. Endpoint pubblico — lista eventi (nessuna auth):**

```bash
http GET $BASE/api/events/
http GET $BASE/api/events/1/availability/
```

**2. Login e salvataggio del token:**

```bash
http POST $BASE/api/auth/login/ username=user_demo password=user12345
# copia il campo "access" dalla risposta:
TOKEN="<incolla_qui_access_token>"
```

**3. Endpoint autenticato — le mie prenotazioni:**

```bash
http GET $BASE/api/reservations/ "Authorization: Bearer $TOKEN"
```

**4. Crea / modifica / annulla una prenotazione:**

```bash
# create
http POST $BASE/api/reservations/ "Authorization: Bearer $TOKEN" event=3 quantity=2
# update (riduci la quantità) — sostituisci <id>
http PATCH $BASE/api/reservations/<id>/ "Authorization: Bearer $TOKEN" quantity=1
# cancel (libera i posti)
http POST $BASE/api/reservations/<id>/cancel/ "Authorization: Bearer $TOKEN"
```

**5. Azione VIETATA — un utente standard prova a creare un evento (atteso `403`):**

```bash
http POST $BASE/api/events/ "Authorization: Bearer $TOKEN" \
  name="Test" location="X" \
  start_time="2027-01-01T10:00:00Z" end_time="2027-01-01T12:00:00Z" \
  total_tickets:=10
# -> 403 Forbidden: "Solo gli organizzatori possono creare o modificare gli eventi."
```

**6. Login come organizzatore e creazione evento (atteso `201`):**

```bash
http POST $BASE/api/auth/login/ username=organizer_demo password=organizer12345
OTOKEN="<access_token_organizer>"
http POST $BASE/api/events/ "Authorization: Bearer $OTOKEN" \
  name="New Show" location="Firenze" \
  start_time="2027-01-01T10:00:00Z" end_time="2027-01-01T12:00:00Z" \
  total_tickets:=50 price=5.00
# lista partecipanti (solo organizzatore/admin):
http GET $BASE/api/events/1/attendees/ "Authorization: Bearer $OTOKEN"
```

## 7. Test automatici

Suite DRF che copre accesso pubblico, permessi per ruolo, disponibilità posti,
overbooking e azioni vietate:

```bash
python manage.py test
```

## 8. Deployment su Render

1. Fai push del repository su GitHub.
2. Su [Render](https://render.com) → **New → Blueprint**, seleziona il repo:
   `render.yaml` configura automaticamente il servizio web (piano free).
   In alternativa **New → Web Service** con:
   - Build command: `./build.sh`
   - Start command: `gunicorn config.wsgi:application`
3. Variabili d'ambiente (già in `render.yaml`): `DJANGO_DEBUG=0`,
   `DJANGO_SECRET_KEY` (generata da Render).
4. Al primo deploy `build.sh` esegue `migrate` + `seed_demo`, così l'API online
   parte già con gli account e i dati demo.
5. Inserisci l'URL pubblico nella riga **Deployment** in cima a questo README.

> Nota: il filesystem free di Render è effimero; il DB SQLite viene ricreato e
> ripopolato ad ogni deploy tramite `seed_demo`. Per persistenza permanente si
> può collegare un database Postgres impostando la variabile `DATABASE_URL`
> (già supportata da `config/settings.py` via `dj-database-url`).

## 9. Struttura del progetto

```
ticket-reservation-api/
├── config/            # progetto Django (settings, urls, wsgi/asgi)
├── accounts/          # app 1: custom user + autenticazione JWT
├── events/            # app 2: eventi, prenotazioni, permessi, seed, test
│   └── management/commands/seed_demo.py
├── db.sqlite3         # database SQLite pre-popolato (incluso)
├── requirements.txt
├── build.sh / Procfile / render.yaml / runtime.txt
└── README.md
```
