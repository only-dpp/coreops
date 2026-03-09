# CoreOps

CoreOps é um sistema leve de monitoramente de uptime construido com **FastSPI**, **Celery**, **Redis** e **PostgresSQL**.

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
- PostgresSQL

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

**PostgresSQL**
- Armazena monitores
- Armazena histórico de execuções

---

## Getting Started

### 1. Clone o repositório

```bash
git clone https://github.com/only-dpp/coresops.git
cd coreops
```

### 2. Crie o arquivo de ambiente

```bash
cp .env.example .env
```
Edite o `.env`



