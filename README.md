# UniBus Core API 🚌

Microserviço minimalista em FastAPI para a plataforma UniBus, fornecendo operações CRUD para estudantes, rotas e viagens com integração à UniBus Geo API para cálculo automático de distância e duração de rotas.

## ✨ Funcionalidades

- **Gestão de Estudantes**: Cadastro e gerenciamento de perfis de estudantes
- **Gestão de Rotas**: Definição de rotas entre cidades com cálculo automático de distância/duração
- **Gestão de Viagens**: Agendamento de viagens em rotas com cálculo automático do horário de chegada
- **Integração Geo-API**: Enriquecimento automático de dados de rotas com distância e duração estimada
- **Banco SQLite**: Persistência leve com SQLAlchemy ORM
- **Documentação Automática**: OpenAPI/Swagger UI disponível em `/docs`
- **Validações Robustas**: Pydantic v2 para validação de dados e email único
- **Tratamento de Erros**: Respostas HTTP apropriadas (400, 404, 422)
- **CORS Configurado**: Pronto para integração com frontends

## 🛠️ Stack Tecnológico

- **Python 3.11** - Linguagem base
- **FastAPI** - Framework web moderno para construção de APIs
- **SQLAlchemy 2.0** - ORM e toolkit SQL
- **Pydantic v2** - Validação de dados usando type hints
- **SQLite** - Banco de dados embutido
- **httpx** - Cliente HTTP assíncrono para chamadas à geo-api
- **Uvicorn** - Servidor ASGI de alta performance

## 📁 Estrutura do Projeto

```plaintext
unibus-core-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação FastAPI com CORS e inicialização
│   ├── db.py                # Engine SQLAlchemy, Base e session dependency
│   ├── models.py            # Models: Student, Route, Trip
│   ├── schemas.py           # Schemas Pydantic para validação
│   ├── services.py          # Lógica de negócio e cálculos
│   ├── external.py          # Cliente HTTP para integração com geo-api
│   └── routers/
│       ├── __init__.py
│       ├── students.py      # Endpoints CRUD de estudantes
│       ├── routes.py        # Endpoints CRUD de rotas
│       └── trips.py         # Endpoints CRUD de viagens
├── requirements.txt         # Dependências Python
├── Dockerfile               # Configuração de container
├── docker-compose.yml       # Orquestração de serviços
├── .env.example             # Template de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── test_api.py             # Script de testes da API
└── README.md               # Documentação
```

## 📊 Modelos de Dados

### Student (Estudante)

- `id`: Chave primária (auto-incremento)
- `name`: Nome do estudante
- `email`: Endereço de email (único, com validação)
- `city`: Cidade do estudante
- `created_at`: Timestamp de registro automático

### Route (Rota)

- `id`: Chave primária (auto-incremento)
- `name`: Nome/identificador da rota
- `origin_city`: Cidade de origem
- `destination_city`: Cidade de destino
- `distance_km`: Distância em quilômetros (obtida da geo-api)
- `estimated_duration_min`: Tempo estimado em minutos (obtido da geo-api)

**Relacionamento:** Uma rota pode ter múltiplas viagens (cascade delete)

### Trip (Viagem)

- `id`: Chave primária (auto-incremento)
- `route_id`: Chave estrangeira para Route (obrigatória)
- `bus_plate`: Placa do veículo (opcional)
- `departure_time`: Horário de partida programado
- `arrival_time`: Horário de chegada (calculado automaticamente)
- `available_seats`: Número de assentos disponíveis (>= 0)

**Relacionamento:** Cada viagem pertence a uma rota

## 🔌 Endpoints da API

### Health Check

- `GET /` - Health check básico do serviço
- `GET /health` - Status detalhado de saúde

### Students (Estudantes)

- `GET /students` - Listar todos os estudantes (com paginação: skip, limit)
- `GET /students/{id}` - Buscar estudante por ID
- `POST /students` - Criar novo estudante (valida email único)
- `PUT /students/{id}` - Atualizar estudante completo
- `DELETE /students/{id}` - Remover estudante (204 No Content)

### Routes (Rotas)

- `GET /routes` - Listar todas as rotas (com paginação)
- `GET /routes/{id}` - Buscar rota por ID
- `POST /routes` - Criar nova rota (chama geo-api automaticamente)
- `PUT /routes/{id}` - Atualizar rota (atualiza dados da geo-api)
- `DELETE /routes/{id}` - Remover rota (cascade delete trips)

### Trips (Viagens)

- `GET /trips` - Listar todas as viagens (com paginação)
- `GET /trips/{id}` - Buscar viagem por ID (inclui detalhes da rota)
- `POST /trips` - Criar nova viagem (calcula arrival_time automaticamente)
- `PUT /trips/{id}` - Atualizar viagem (recalcula arrival se necessário)
- `DELETE /trips/{id}` - Remover viagem

**Total:** 18 endpoints REST implementados

## 🚀 Instalação e Configuração

### Desenvolvimento Local

**1. Clone o repositório**

```bash
git clone https://github.com/oondels/unibus-core-api.git
cd unibus-core-api
```

**2. Crie o ambiente virtual**

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Configure variáveis de ambiente (opcional)**

```bash
cp .env.example .env
# Edite .env conforme necessário
```

Variáveis disponíveis:
- `GEO_API_URL` - URL da unibus-geo-api (padrão: `http://localhost:8001`)
- `GEO_API_TIMEOUT` - Timeout em segundos (padrão: `10.0`)

**5. Execute a aplicação**

```bash
uvicorn app.main:app --reload --port 8000
```

Ou usando o ambiente virtual diretamente:

```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**6. Acesse a API**

- **API Base:** http://localhost:8000
- **Swagger UI (Docs Interativos):** http://localhost:8000/docs
- **ReDoc (Docs Alternativos):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

### 🐳 Deploy com Docker

**Opção 1: Docker simples**

```bash
# Build da imagem
docker build -t unibus-core-api:latest .

# Executar container
docker run -d \
  --name unibus-core \
  -p 8000:8000 \
  -e GEO_API_URL=http://host.docker.internal:8001 \
  -v $(pwd)/unibus.db:/app/unibus.db \
  unibus-core-api:latest

# Ver logs
docker logs -f unibus-core

# Parar e remover
docker stop unibus-core && docker rm unibus-core
```

**Opção 2: Docker Compose (recomendado)**

```bash
# Subir todos os serviços
docker-compose up --build

# Rodar em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `GEO_API_URL` | URL base da UniBus Geo API | `http://localhost:8001` |
| `GEO_API_TIMEOUT` | Timeout para requisições à geo-api (segundos) | `10.0` |

**Arquivo `.env.example` fornecido como template.**

## 📋 Regras de Negócio

### Criação/Atualização de Rotas

1. **Chamada automática à geo-api:** Ao criar ou atualizar uma rota, o sistema automaticamente chama `POST /distance` na geo-api passando `origin_city` e `destination_city`
2. **Sucesso (geo-api disponível):** Retorna HTTP 201 (Created) com `distance_km` e `estimated_duration_min` preenchidos
3. **Falha (geo-api indisponível):** Salva a rota com valores `null` para distância/duração e retorna HTTP 202 (Accepted) com mensagem de aviso

### Criação de Viagens

1. **Validação de rota:** `route_id` deve existir (constraint de chave estrangeira)
2. **Cálculo automático:** `arrival_time = departure_time + route.estimated_duration_min`
3. **Sem duração:** Se a rota não tiver `estimated_duration_min`, `arrival_time` fica `null`
4. **Atualização inteligente:** Ao atualizar `departure_time`, recalcula `arrival_time` automaticamente

### Validação de Estudantes

1. **Email único:** Não permite emails duplicados (constraint UNIQUE)
2. **Erro de duplicação:** Retorna HTTP 400 (Bad Request) com mensagem clara
3. **Validação de formato:** Email deve ter formato válido (Pydantic EmailStr)

### Validações Gerais

- `available_seats` deve ser >= 0
- Campos obrigatórios validados pelo Pydantic
- Foreign keys validadas antes de inserção

## 📡 Exemplos de Uso

### Criar um Estudante

```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@example.com",
    "city": "Rio de Janeiro"
  }'
```

**Resposta (201 Created):**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao.silva@example.com",
  "city": "Rio de Janeiro",
  "created_at": "2025-12-12T12:00:00"
}
```

### Criar uma Rota (com enriquecimento via geo-api)

```bash
curl -X POST "http://localhost:8000/routes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rio - São Paulo Express",
    "origin_city": "Rio de Janeiro",
    "destination_city": "São Paulo"
  }'
```

**Resposta (201 Created se geo-api disponível):**
```json
{
  "id": 1,
  "name": "Rio - São Paulo Express",
  "origin_city": "Rio de Janeiro",
  "destination_city": "São Paulo",
  "distance_km": 430.5,
  "estimated_duration_min": 360
}
```

### Criar uma Viagem

```bash
curl -X POST "http://localhost:8000/trips" \
  -H "Content-Type: application/json" \
  -d '{
    "route_id": 1,
    "bus_plate": "ABC-1234",
    "departure_time": "2025-12-15T08:00:00",
    "available_seats": 40
  }'
```

**Resposta (201 Created com arrival_time calculado):**
```json
{
  "id": 1,
  "route_id": 1,
  "bus_plate": "ABC-1234",
  "departure_time": "2025-12-15T08:00:00",
  "arrival_time": "2025-12-15T14:00:00",
  "available_seats": 40
}
```

### Testar Script Automático

Use o script fornecido para testar todos os endpoints:

```bash
python test_api.py
```

## 🗄️ Banco de Dados

A aplicação usa **SQLite** para simplicidade e portabilidade no MVP. O arquivo `unibus.db` é criado automaticamente na raiz do projeto no primeiro startup.

### Tabelas Criadas

```sql
-- students
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    city VARCHAR NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- routes
CREATE TABLE routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    origin_city VARCHAR NOT NULL,
    destination_city VARCHAR NOT NULL,
    distance_km FLOAT,
    estimated_duration_min INTEGER
);

-- trips
CREATE TABLE trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    bus_plate VARCHAR,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME,
    available_seats INTEGER NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);
```

### Inicialização Automática

As tabelas são criadas automaticamente no startup usando `Base.metadata.create_all()` do SQLAlchemy. Não é necessária nenhuma configuração manual.

### Migrações (Produção)

Para ambientes de produção, considere usar **Alembic** para gerenciar migrações:

```bash
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Migração inicial"
alembic upgrade head
```

### Inspecionar Banco de Dados

```bash
# Usando SQLite CLI
sqlite3 unibus.db ".tables"
sqlite3 unibus.db ".schema students"

# Ou use o script Python fornecido
.venv/bin/python -c "
from app.db import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tabelas:', inspector.get_table_names())
"
```

## 🧪 Testes

### Documentação Interativa

A forma mais fácil de testar é usando a documentação interativa:

- **Swagger UI:** <http://localhost:8000/docs> - Interface completa para testar todos os endpoints
- **ReDoc:** <http://localhost:8000/redoc> - Documentação estática elegante

### Script de Teste Automático

Use o script fornecido para testar rapidamente:

```bash
python test_api.py
```

O script testa:
- Health check
- Criação de estudante
- Listagem de estudantes
- Criação de rota (com chamada à geo-api)
- Criação de viagem
- Listagem de viagens

### Ferramentas Recomendadas

- **curl** - Cliente HTTP de linha de comando (exemplos acima)
- **HTTPie** - Cliente HTTP moderno: `http POST localhost:8000/students name="Test" email="test@example.com" city="Rio"`
- **Postman** - Interface gráfica para testes de API
- **Insomnia** - Alternativa ao Postman
- **pytest** - Para testes unitários/integração (não implementado no MVP)

### Testes Unitários (Futuro)

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/ -v
```

## 🛠️ Notas de Desenvolvimento

### Configuração CORS

O CORS está configurado para permitir todas as origens (`allow_origins=["*"]`) para facilitar o desenvolvimento. **Para produção, restrinja para domínios específicos:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://unibus-frontend.com",
        "https://app.unibus.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Códigos de Status HTTP

A API retorna códigos de status HTTP padrão:

| Código | Significado | Uso |
|--------|-------------|-----|
| `200 OK` | Sucesso | GET, PUT bem-sucedidos |
| `201 Created` | Criado | POST bem-sucedido |
| `202 Accepted` | Aceito parcialmente | Rota criada mas geo-api indisponível |
| `204 No Content` | Sem conteúdo | DELETE bem-sucedido |
| `400 Bad Request` | Erro de validação | Email duplicado, FK inválida |
| `404 Not Found` | Não encontrado | Recurso não existe |
| `422 Unprocessable Entity` | Validação Pydantic | Dados inválidos |
| `500 Internal Server Error` | Erro interno | Erro não tratado |

### Estrutura de Erros

```json
{
  "detail": "Student with email joao@example.com already exists"
}
```

### Hot Reload

Em modo desenvolvimento (`--reload`), o servidor reinicia automaticamente ao detectar mudanças nos arquivos Python.

### Logs

Para habilitar logs SQL (debug):

```python
# Em app/db.py
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  # Mostra todas as queries SQL
)
```

## 🚀 Considerações para Produção

### 1. Banco de Dados

**Migrar de SQLite para PostgreSQL:**

```python
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/unibus

# app/db.py
import os
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)
```

### 2. Segurança

- **Autenticação:** Implementar JWT ou OAuth2
- **Secrets:** Usar AWS Secrets Manager, HashiCorp Vault ou Azure Key Vault
- **HTTPS:** Deploy atrás de reverse proxy (Nginx, Traefik) com SSL/TLS
- **Rate Limiting:** Usar `slowapi` para prevenir abuso
- **CORS:** Restringir origens permitidas

### 3. Performance

- **Process Manager:** Usar Gunicorn com múltiplos workers
  ```bash
  gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
  ```
- **Cache:** Implementar Redis para cache de rotas frequentes
- **Connection Pool:** Configurar pool de conexões do SQLAlchemy
- **Async Operations:** Manter operações assíncronas para melhor throughput

### 4. Observabilidade

- **Logging Estruturado:** JSON logs com contexto
  ```python
  import structlog
  logger = structlog.get_logger()
  ```
- **APM:** Application Performance Monitoring (New Relic, Datadog, Sentry)
- **Métricas:** Prometheus + Grafana
- **Tracing:** OpenTelemetry para rastreamento distribuído
- **Health Checks:** Liveness e readiness probes para Kubernetes

### 5. Deploy

- **Containerização:** Docker/Kubernetes (já implementado)
- **CI/CD:** GitHub Actions, GitLab CI, Jenkins
- **Ambiente:** Variáveis de ambiente para configuração
- **Migrações:** Alembic para controle de versão do schema
- **Backup:** Backups automáticos do banco de dados

### 6. Escala Horizontal

```yaml
# docker-compose.yml para múltiplas instâncias
services:
  unibus-api:
    image: unibus-core-api:latest
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://...
```

### 7. Qualidade de Código

- **Testes:** pytest com cobertura > 80%
- **Linting:** ruff, black, mypy
- **Pre-commit hooks:** Validar antes de commit
- **Documentação:** Manter README atualizado

## 📝 Licença

MIT License - Veja arquivo LICENSE para detalhes.

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## ❓ Suporte

Para questões e problemas:
- Abra uma issue no repositório: <https://github.com/oondels/unibus-core-api/issues>
- Consulte a documentação interativa: <http://localhost:8000/docs>

## 🚀 Próximos Passos

- [ ] Implementar testes unitários e de integração
- [ ] Adicionar autenticação JWT
- [ ] Criar relacionamento Student-Trip (bookings/reservas)
- [ ] Implementar paginação avançada com cursor
- [ ] Adicionar filtros de busca (por cidade, data, etc.)
- [ ] Implementar rate limiting
- [ ] Configurar CI/CD pipeline
- [ ] Migrar para PostgreSQL
- [ ] Adicionar observabilidade (logs, métricas, traces)

---

**Desenvolvido para o MVP UniBus** | Sprint 3 - Microserviços | PUC-Rio 2025
