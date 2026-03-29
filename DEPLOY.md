# Deploy CoreOps (VM Linux)

## 1. Clonar o repositório

```bash
git clone https://github.com/only-dpp/coreops.git
cd coreops
```

## 2. Garantir que o `.env` existe

Crie ou ajuste o arquivo `.env` antes de subir os containers.

Verifique principalmente:

- `DATABASE_URL`
- `REDIS_URL`
- credenciais do usuário admin
- variáveis de sessão / segurança

## 3. Subir serviços base

```bash
docker compose up -d db redis
```

## 4. Rodar migrations

```bash
docker compose run --rm api alembic upgrade head
```

## 5. Subir aplicação completa

```bash
docker compose up -d api worker beat nginx
```

## 6. Verificar se a API subiu corretamente

```bash
docker compose logs -f api
```

## 7. Verificar containers

```bash
docker compose ps
```

## 8. Testar localmente na VM

```bash
curl http://localhost/login
```

## 9. Acessar externamente

Abra no navegador usando o IP externo atual da VM:

```txt
http://IP_DA_VM/login
```

---

# Comandos úteis

## Ver status dos containers
```bash
docker compose ps
```

## Ver logs da API
```bash
docker compose logs -f api
```

## Reiniciar apenas a API
```bash
docker compose restart api
```

## Derrubar tudo
```bash
docker compose down
```

## Subir tudo rebuildando
```bash
docker compose up -d --build
```

---

# Diagnóstico rápido

## Se `curl http://localhost/login` funcionar, mas externamente não abrir
Provável problema de:

- IP externo incorreto
- firewall
- regra de rede no provedor cloud

## Se o Nginx responder `502 Bad Gateway`
O Nginx está funcionando, mas a API atrás dele não.

Possíveis causas:

- API não subiu
- migrations não foram rodadas
- erro no startup da aplicação
- banco ainda não estava pronto

## Se a VM reiniciar e o sistema parar de abrir
Sempre suspeite de:

- mudança no IP externo da VM

## Se o login ou dashboard der erro 500
Verificar:

- logs da API
- uso de `TemplateResponse`
- nome dos templates/parciais
- migrations e tabelas existentes no banco

## Se aparecer erro de tabela inexistente (`relation does not exist`)
Rodar novamente:

```bash
docker compose run --rm api alembic upgrade head
```
