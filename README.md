# CoreOps

CoreOps é um sistema leve de monitoramente de uptime construido com **FastSPI**, **Celery**, **Redis** e **PostgresSQL**.

O projeto inclui um dashboard web simples para gerenciar monitores, visualizar histórico de execuçôes e controlar o comportamento dos alertas

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

##Screenshots

<img width="1898" height="911" alt="image" src="https://github.com/user-attachments/assets/e6108833-9998-48fe-8d1c-275ab0934410" />
