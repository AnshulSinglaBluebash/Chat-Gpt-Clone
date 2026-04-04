# ChatGPT Clone

A simple ChatGPT-style application built with FastAPI, PostgreSQL, JWT authentication, OpenAI, and a Streamlit frontend.

## Features

- JWT-based signup and login
- Protected chat API with bearer token auth
- OpenAI-powered responses
- pgvector-powered embeddings and basic retrieval
- Chat sessions and chat history
- PostgreSQL database with SQLAlchemy models
- Swagger UI for API testing
- Streamlit frontend for chat interaction
- Health check, CORS, and basic logging

## Project Structure

```text
ChatGpt_Clone/
  .env.example              # Sample environment variables
  alembic.ini               # Alembic configuration
  create_table.py           # DB table creation helper
  README.md                 # Project documentation
  alembic/
    env.py                  # Alembic migration environment
    versions/               # Database migration files
  app/
    main.py                 # FastAPI app entrypoint, CORS, logging, health route
    auth/
      routes.py             # Signup, login, and current-user APIs
      jwt_handler.py        # JWT create/decode helpers
      utils.py              # Password hashing and verification
    chat/
      routes.py             # Chat send/history/session APIs
      service.py            # OpenAI response generation
      rag.py                # Embeddings + retrieval logic
    db/
      database.py           # SQLAlchemy engine/session setup
      models.py             # ORM models
      schemas.py            # Pydantic request/response schemas
      test_db.py            # DB connection test helper
    langserve/
      routes.py             # LangServe route module placeholder
  streamlit_app/
    app.py                  # Streamlit frontend
    __init__.py
```

## Backend APIs

- `POST /auth/signup`
- `POST /auth/login`
- `GET /auth/me`
- `POST /chat/send`
- `GET /chat/history/{session_id}`
- `GET /chat/sessions`
- `GET /health`

## Environment Variables

Create a `.env` file using `.env.example`.

Required values:

- `SECRET_KEY`
- `DATABASE_URL`
- `OPENAI_API_KEY`

Optional:

- `BACKEND_URL`

## Run Backend

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Run Streamlit Frontend

```bash
streamlit run streamlit_app/app.py
```

## Authentication Flow

1. Sign up with `/auth/signup`
2. Log in with `/auth/login`
3. Copy the `access_token`
4. Authorize Swagger using `Bearer <token>`
5. Call `/chat/send`

## Notes

- Do not commit your real `.env` file or API keys.
- Use `session_id: null` for a new conversation.
- Reuse the returned `session_id` to continue the same chat session.
- The first chat request seeds a small knowledge base into the `embeddings` table and uses pgvector similarity search to retrieve relevant context.
