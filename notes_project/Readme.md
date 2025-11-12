#  Collaborative Notes API (Django + DRF + WebSockets)

A real-time note collaboration API built with **Django REST Framework** and **Django Channels**.  
Supports note creation, editing, versioning, and live typing indicators using Redis.

---

##  Features

- CRUD APIs for notes
- Optimistic concurrency control for edits
- Version history tracking per note
- Real-time updates via WebSockets
- Typing indicators (powered by Redis)
- JWT-based authentication
- Postman collection included

---

##  Tech Stack

| Component | Technology |
|------------|-------------|
| Backend | Django, Django REST Framework |
| Realtime | Django Channels, WebSockets |
| Message Broker | Redis |
| Database | SQLite |
| Auth | JWT (via `djangorestframework-simplejwt`) |


---

## Installation & Setup

### 1️.Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>


Activate the virtual environment:

Windows:
venv\Scripts\activate

Linux / macOS:
source venv/bin/activate

3️. Install Dependencies:
pip install -r requirements.txt

4️.Start Redis:

Using WSL
sudo service redis-server start


5. Run the Server
daphne notes_project.asgi:application --port 8000



API Reference (Postman)

Included a postman_collection.json

Available Endpoints
Method	Endpoint	Description
GET	/api/notes/	List all notes
POST	/api/notes/	Create a new note
PATCH	/api/notes/:id/	Update a note (version control applied)
WS	/ws/notes/:id/	Real-time collaboration via websocket



