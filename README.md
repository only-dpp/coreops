# CoreOps

![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)
![Celery](https://img.shields.io/badge/Celery-5.6.2-green?logo=celery)
![Redis](https://img.shields.io/badge/Redis-7.3.0-red?logo=redis)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![Python](https://img.shields.io/badge/Python-3.11-yellow?logo=python)


CoreOps é um sistema leve de monitoramente de uptime construido com **FastAPI**, **Celery**, **Redis** e **PostgresQL**.

O projeto inclui um dashboard web simples para gerenciar monitores, visualizar histórico de execuções e controlar o comportamento dos alertas

---

## Features 

- Monitoramente de endpoints HTTP
- Alerta por Email com templates HTML
- Alerta via webhook do Discord
- Pausar / retomar monitores
- Dashboard com atualizaçôes em tempo real
- Histórico de execução por monitor
- Autenticação com login baseado em sessão
- Proteção CSRF
- Processamento em bachground com Celery
- Execução agendada com Celery Beat
- Ambiente de desenvolvimento baseado em docker

---

## Screenshots

<img width="1898" height="911" alt="image" src="https://github.com/user-attachments/assets/e6108833-9998-48fe-8d1c-275ab0934410" />

<img width="1904" height="908" alt="image" src="https://github.com/user-attachments/assets/b2d251c9-0770-4f38-b5d7-b523db6ae46a" />

<img width="1907" height="907" alt="image" src="https://github.com/user-attachments/assets/c169adb8-46f8-4278-a278-1582c3b3064c" />

<img width="1801" height="832" alt="image" src="https://github.com/user-attachments/assets/20ec26ca-6bd9-436d-af5c-3277191c4c06" />

---

## Tech Stack

**Backend**
- FastAPI
- SQLAlchemy
- Alembic
- Celery
- Redis
- PostgreSQL

**Frontend**
- Jinja2 template
- HTMX
- Vanilla CSS

---

## Architecture

User → FastAPI API → PostgreSQL
│
Celery Worker
│
Celery Beat → Scheduler
│
Redis (broker)

---

### Componentes 

**API**
- Aplicação FastAPI
- Autenticação
- Renderização do dashboard
- Criação e gerenciamento de monitores

**Worker**
- Executa jobs de monitoramento
- Envia alertas

**Beat**
- Scheduler que dispara verificações

**Redis**
- Broker de mensagens para Celery

**postgreSQL**
- Armazena monitores
- Armazena histórico de execuções

---

## Getting Started

### 1. Clone o repositório

```bash
git clone https://github.com/only-dpp/coreops.git
cd coreops
```

### 2. Crie o arquivo de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e configure seus valores.

Campos importantes:
- `SMTP_USER`
- `SMTP_PASS`
- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

### 3. Suba os serviços

```bash
docker compose up -d --build
```

Isso iniciará:
- API
- WORKER
- Beat Scheduler
- Redis
- postgreSQL

### 4. Rode as migrações

```bash
docker compose exec api alembic upgrade head
```

### 5. Acesse o dashboard

Abra:
```bash
http://localhost:8000/login
```
Login com as credenciais definidas em `.env`

## Criando um Monitor

No dashboard 
1. Clique em **New Monitor**
2. Informe:
   - Nome
   - URL
   - Intervalo
   - Canal de alerta
3. Salve

O monitor começará a rodar automaticamente.

## alert Channels

### Discord

Informe a URL do webhook:
```bash
https://discord.com/api/webhook/...
```

### Email

Configure o **SMTP** no `.env`

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## Project Structure

```bash
coreops
│
├── app
│ ├── api
│ ├── core
│ ├── db
│ ├── templates
│ ├── static
│ └── web
│
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
└── .env.example
```

## Security Notes

Este projeto inclui camadas básicas de segurança:
- Autenticação baseada em sessão
- Hashing de senhas
- Proteção CSRF
- Configuração via variáveis de ambiente


### License

MIT License










