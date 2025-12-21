# UniBus Core API 🚌

Microserviço minimalista em FastAPI para a plataforma UniBus, fornecendo operações CRUD para estudantes, rotas e viagens com integração à API de Validação de Estudantes.

## ✨ Funcionalidades

- **Gestão de Estudantes**: Cadastro e gerenciamento de perfis de estudantes com validação de elegibilidade
- **Validação de CEP**: Integração com ViaCEP API (gratuita) para validação automática de endereços
- **Validação de Estudantes**: Integração com API de validação para verificar email institucional
- **Gestão de Rotas**: Definição de rotas entre cidades
- **Gestão de Viagens**: Agendamento de viagens em rotas com cálculo automático do horário de chegada
- **Banco PostgreSQL**: Persistência robusta e escalável com SQLAlchemy ORM
- **Docker Compose**: PostgreSQL containerizado com volume persistente
- **Documentação Automática**: OpenAPI/Swagger UI disponível em `/docs`
- **Validações Robustas**: Pydantic v2 para validação de dados e email único
- **Tratamento de Erros**: Respostas HTTP apropriadas (400, 404, 422)
- **CORS Configurado**: Pronto para integração com frontends

## 🛠️ Stack Tecnológico

- **Python 3.11** - Linguagem base
- **FastAPI** - Framework web moderno para construção de APIs
- **SQLAlchemy 2.0** - ORM e toolkit SQL
- **Pydantic v2** - Validação de dados usando type hints
- **PostgreSQL 15** - Banco de dados relacional robusto
- **psycopg2** - Driver PostgreSQL para Python
- **httpx** - Cliente HTTP assíncrono para chamadas às APIs externas
- **ViaCEP API** - API pública gratuita para validação de CEP
- **Uvicorn** - Servidor ASGI de alta performance
- **Docker & Docker Compose** - Containerização e orquestração

## 🏗️ Arquitetura do Sistema

A arquitetura do UniBus segue o **Cenário 2** do guia do MVP: **API Principal → API Secundária → API Externa**. Este modelo garante modularidade, separação de responsabilidades e escalabilidade independente de cada componente.

```mermaid
graph TB
    subgraph "Cliente"
        CLIENT[🖥️ Cliente HTTP/Frontend]
    end
    
    subgraph "UniBus Core API (Porta 8000)"
        CORE[🚌 FastAPI Core API]
        CORE_DB[(🐘 PostgreSQL<br/>Core Database<br/>Port 5433)]
    end
    
    subgraph "UniBus Validation API (Porta 8001)"
        VALIDATION[✅ FastAPI Validation API]
        VALIDATION_DB[(💾 SQLite<br/>Validation Database)]
    end
    
    subgraph "Serviços Externos"
        VIACEP[🌐 ViaCEP API<br/>https://viacep.com.br]
    end
    
    CLIENT -->|1. POST /students| CORE
    CORE -->|2. GET /ws/{cep}/json| VIACEP
    VIACEP -->|3. Dados do CEP| CORE
    CORE -->|4. POST /validate-student| VALIDATION
    VALIDATION -->|5. Resultado validação| CORE
    CORE -->|6. Salva estudante| CORE_DB
    CORE -->|7. HTTP 201 Created| CLIENT
    
    VALIDATION -.->|Consulta regras| VALIDATION_DB
    
    style CORE fill:#4CAF50,stroke:#2E7D32,color:#fff
    style VALIDATION fill:#2196F3,stroke:#1565C0,color:#fff
    style VIACEP fill:#FF9800,stroke:#E65100,color:#fff
    style CORE_DB fill:#00897B,stroke:#004D40,color:#fff
    style VALIDATION_DB fill:#5C6BC0,stroke:#283593,color:#fff
    style CLIENT fill:#9E9E9E,stroke:#424242,color:#fff
```

### Fluxo de Criação de Estudante

Quando um novo estudante é criado via `POST /students`, o sistema executa o seguinte fluxo:

1. **Cliente** envia dados do estudante (nome, email, CEP) para o **UniBus Core API**
2. **Core API** consulta a **ViaCEP API** (serviço externo HTTPS) para validar o CEP e obter informações de endereço
3. **ViaCEP** retorna dados oficiais: cidade, código IBGE, estado
4. **Core API** consulta a **UniBus Validation API** (API secundária) para verificar se o email é institucional
5. **Validation API** valida o email (deve conter `@aluno` ou `.edu.br`) e matrícula (mínimo 6 caracteres)
6. Se todas as validações forem bem-sucedidas, o **Core API** salva o estudante no **PostgreSQL**
7. **Core API** retorna `HTTP 201 Created` ao cliente com os dados do estudante cadastrado

### Autonomia dos Serviços

Cada componente da arquitetura possui **total autonomia e independência**:

| Componente | Banco de Dados | Containerização | Porta |
|------------|----------------|-----------------|-------|
| **UniBus Core API** | PostgreSQL (persistente) | `Dockerfile` próprio | 8000 |
| **UniBus Validation API** | SQLite (local) | `Dockerfile` próprio | 8001 |
| **ViaCEP API** | N/A (serviço externo) | N/A | 443 (HTTPS) |

**Benefícios desta arquitetura:**
- ✅ **Escalabilidade independente**: Cada serviço pode ser escalado separadamente
- ✅ **Desenvolvimento desacoplado**: Equipes podem trabalhar em paralelo
- ✅ **Resiliência**: Falha em um serviço não derruba o sistema completo (fallback implementado)
- ✅ **Manutenção simplificada**: Alterações em um serviço não afetam os demais
- ✅ **Testabilidade**: Cada componente pode ser testado isoladamente

### Estratégia de Fallback

- **ViaCEP indisponível**: Cadastro é **rejeitado** (CEP é informação crítica)
- **Validation API indisponível**: Estudante é **aceito por padrão** (garante disponibilidade do sistema)

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
│   ├── external.py          # Cliente HTTP para integração com validation-api
│   ├── viacep.py            # Cliente HTTP para integração com ViaCEP API
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
- `cep`: Código de Endereçamento Postal (validado via ViaCEP)
- `city`: Cidade do estudante (auto-preenchido via ViaCEP)
- `city_ibge_code`: Código IBGE da cidade (auto-preenchido via ViaCEP)
- `created_at`: Timestamp de registro automático

### Route (Rota)

- `id`: Chave primária (auto-incremento)
- `name`: Nome/identificador da rota
- `origin_city`: Cidade de origem
- `destination_city`: Cidade de destino
- `distance_km`: Distância em quilômetros (opcional, pode ser preenchido manualmente)
- `estimated_duration_min`: Tempo estimado em minutos (opcional, pode ser preenchido manualmente)

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

### Arquitetura de Integração

O UniBus Core API se integra com o **Student Validation API** para validar a elegibilidade dos estudantes:

```
┌─────────────────────┐           ┌──────────────────────────┐
│                     │           │                          │
│  UniBus Core API    │──────────▶│ Student Validation API   │
│  (Port 8000)        │  HTTP     │  (Port 8001)             │
│                     │◀──────────│                          │
└─────────────────────┘           └──────────────────────────┘
         │                                    │
         │                                    │
         ▼                                    ▼
┌─────────────────────┐           ┌──────────────────────────┐
│                     │           │  Validação de Email:     │
│  PostgreSQL         │           │  - @aluno ou .edu.br     │
│  (Port 5433)        │           │  Matrícula: >= 6 chars   │
│                     │           │                          │
└─────────────────────┘           └──────────────────────────┘
```

**Fluxo de Validação:**

1. Cliente faz POST `/students` com dados do estudante
2. Core API chama validation-api com `name`, `email` e `city`
3. Validation-api verifica:
   - Email institucional (`@aluno` ou `.edu.br`)
   - Matrícula válida (>= 6 caracteres)
4. Se válido: estudante é salvo no banco PostgreSQL
5. Se inválido: retorna HTTP 400 com mensagem de erro
6. Se validation-api indisponível: aceita estudante por padrão (fallback)

---

## 📡 API Secundária: Student Validation API

### Visão Geral

O **UniBus Core API** integra-se com a **Student Validation API** (API secundária) para validar a elegibilidade de estudantes antes de cadastrá-los no sistema. Esta integração garante que apenas estudantes com credenciais institucionais válidas possam se registrar na plataforma UniBus.

### Quando é Chamada?

A validation-api é chamada **exclusivamente** no momento da **criação de um novo estudante**:

| Endpoint | Método | Quando Chama API Secundária | Motivo |
|----------|--------|----------------------------|--------|
| `POST /students` | CREATE | ✅ **Sempre** (antes de salvar no banco) | Validar elegibilidade do estudante |
| `PUT /students/{id}` | UPDATE | ❌ Nunca | Atualização não requer revalidação |
| `GET /students` | LIST | ❌ Nunca | Apenas consulta dados existentes |
| `GET /students/{id}` | READ | ❌ Nunca | Apenas consulta dados existentes |
| `DELETE /students/{id}` | DELETE | ❌ Nunca | Remoção não requer validação |

**⚠️ Importante:** A validação ocorre **apenas uma vez**, no momento do cadastro inicial. Atualizações posteriores não acionam nova validação.

### Por Que é Chamada?

#### 🎯 Objetivo Principal
Garantir que **apenas estudantes com email institucional válido** possam se cadastrar no sistema UniBus, cumprindo os requisitos do projeto universitário.

#### 📋 Critérios de Validação

A validation-api verifica:

1. **Email Institucional**: O email deve conter um dos seguintes padrões:
   - `@aluno` (ex: `maria@aluno.puc.br`, `joao@aluno.ufrj.br`)
   - `.edu.br` (ex: `pedro@estudante.edu.br`)

2. **Matrícula Válida**: O campo `registration` (mapeado do campo `city`) deve ter:
   - Pelo menos **6 caracteres**

#### ✅ Exemplos de Emails Válidos
```
✓ maria@aluno.puc-rio.br
✓ joao@aluno.ufrj.br
✓ pedro.silva@edu.br
✓ ana@estudante.edu.br
```

#### ❌ Exemplos de Emails Inválidos
```
✗ joao@gmail.com          → Não é institucional
✗ maria@hotmail.com       → Não é institucional
✗ pedro@empresa.com.br    → Não contém @aluno nem .edu.br
```

### Especificação Técnica

#### Endpoint da Validation API

```http
POST http://localhost:8001/validate-student
Content-Type: application/json
```

#### Request Payload

```json
{
  "name": "Maria Silva",
  "email": "maria@aluno.puc.br",
  "registration": "Rio de Janeiro"
}
```

**Nota:** O campo `registration` é preenchido com o valor do campo `city` do estudante.

#### Response - Estudante Válido (200 OK)

```json
{
  "is_valid": true,
  "reason": "Email and registration are valid"
}
```

#### Response - Estudante Inválido (200 OK)

```json
{
  "is_valid": false,
  "reason": "Email must contain @aluno or .edu.br"
}
```

ou

```json
{
  "is_valid": false,
  "reason": "Registration must be at least 6 characters"
}
```

### Tratamento de Erros e Fallback

#### 🔄 Estratégia de Fallback

Se a **validation-api estiver indisponível** (timeout, connection error, 5xx), o UniBus Core API implementa uma estratégia de fallback:

```
Validation API Offline → Aceita Estudante por Padrão → HTTP 201 Created
```

**Motivo:** Garantir disponibilidade do sistema mesmo quando a API secundária estiver fora do ar.

#### 📊 Comportamento por Cenário

| Cenário | Validation API Status | Core API Comportamento | HTTP Response |
|---------|----------------------|------------------------|---------------|
| Email válido | ✅ Online | Salva no banco | `201 Created` |
| Email inválido | ✅ Online | **Não salva** no banco | `400 Bad Request` |
| API offline/timeout | ❌ Offline | Salva no banco (fallback) | `201 Created` |
| API retorna 5xx | ❌ Error | Salva no banco (fallback) | `201 Created` |

#### Implementação do Fallback

```python
# Em app/services.py
async def validate_student_eligibility(name: str, email: str, city: str) -> dict:
    validation_data = await validation_client.validate_student(name, email, city)
    
    if validation_data:
        return {
            "is_valid": validation_data.get("is_valid", False),
            "reason": validation_data.get("reason", "Unknown"),
            "validation_api_available": True,
        }
    else:
        # Fallback: aceita estudante se API estiver offline
        return {
            "is_valid": True,
            "reason": "Validation API unavailable - student accepted by default",
            "validation_api_available": False,
        }
```

### Exemplo de Uso Completo

#### 1. Estudante Válido (Email Institucional)

```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ana Costa",
    "email": "ana@aluno.puc.br",
    "city": "Rio de Janeiro"
  }'
```

**Sequência de Eventos:**
1. Core API recebe requisição
2. Valida schema Pydantic (formato de email)
3. **Chama validation-api**: `POST http://localhost:8001/validate-student`
4. Validation-api retorna: `{"is_valid": true, "reason": "..."}`
5. Core API salva estudante no PostgreSQL
6. Retorna: `201 Created` com dados do estudante

**Response:**
```json
{
  "id": 1,
  "name": "Ana Costa",
  "email": "ana@aluno.puc.br",
  "city": "Rio de Janeiro",
  "created_at": "2025-12-15T10:30:00"
}
```

#### 2. Estudante Inválido (Email Comum)

```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Santos",
    "email": "joao@gmail.com",
    "city": "São Paulo"
  }'
```

**Sequência de Eventos:**
1. Core API recebe requisição
2. Valida schema Pydantic ✅
3. **Chama validation-api**: `POST http://localhost:8001/validate-student`
4. Validation-api retorna: `{"is_valid": false, "reason": "Email must contain @aluno or .edu.br"}`
5. Core API **não salva** no banco
6. Retorna: `400 Bad Request` com motivo da rejeição

**Response:**
```json
{
  "detail": "Student validation failed: Email must contain @aluno or .edu.br"
}
```

#### 3. Validation API Offline (Fallback)

```bash
# Simular API offline (desligar validation-api)
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pedro Oliveira",
    "email": "pedro@exemplo.com",
    "city": "Brasília"
  }'
```

**Sequência de Eventos:**
1. Core API recebe requisição
2. Valida schema Pydantic ✅
3. **Tenta chamar validation-api**: timeout/connection error
4. Fallback ativado: `{"is_valid": true, "reason": "Validation API unavailable..."}`
5. Core API salva estudante no PostgreSQL (aceita por padrão)
6. Retorna: `201 Created`

**Response:**
```json
{
  "id": 2,
  "name": "Pedro Oliveira",
  "email": "pedro@exemplo.com",
  "city": "Brasília",
  "created_at": "2025-12-15T10:35:00"
}
```

### Configuração

#### Variáveis de Ambiente

```bash
# .env
VALIDATION_API_URL=http://localhost:8001
VALIDATION_API_TIMEOUT=10.0
```

#### Docker Compose

```yaml
services:
  unibus-core-api:
    environment:
      - VALIDATION_API_URL=http://student-validation-api:8001
      - VALIDATION_API_TIMEOUT=10.0
```

### Logs e Debugging

Para verificar as chamadas à validation-api, monitore os logs:

```bash
# Ver logs do Core API
docker-compose logs -f unibus-core-api

# Exemplos de logs
INFO: Calling validation-api for student: maria@aluno.puc.br
INFO: Validation successful: is_valid=True
ERROR: Validation-API unavailable, using fallback
```

### Health Check da Validation API

Verifique se a validation-api está disponível:

```bash
curl http://localhost:8001/health
```

**Response esperado:**
```json
{
  "status": "healthy",
  "service": "student-validation-api"
}
```

---

## 🌐 API Pública de Terceiros: ViaCEP

### Visão Geral

O **UniBus Core API** integra-se com a **ViaCEP** - uma API **pública e gratuita** mantida pela comunidade brasileira para consulta de informações de endereços através do CEP (Código de Endereçamento Postal).

**URL da API:** https://viacep.com.br/

### Licença e Acesso

- **Licença:** Pública e **totalmente gratuita** - sem custos de uso
- **Cadastro/API Key:** **Não requer cadastro** - acesso direto e livre
- **Documentação oficial:** https://viacep.com.br/
- **Código fonte:** Projeto de código aberto mantido pela comunidade

A ViaCEP é um serviço público que pode ser utilizado livremente por qualquer desenvolvedor ou aplicação, sem necessidade de registro, autenticação ou chaves de API. Ideal para MVPs e projetos universitários.

### Arquitetura do Sistema

![Arquitetura do Sistema](./arquitetura.png)

> **Nota:** Diagrama de arquitetura mostrando a integração entre o UniBus Core API, ViaCEP, Student Validation API e PostgreSQL. *(Requisito obrigatório do MVP)*

### Por Que é Usada?

A ViaCEP é utilizada para **validar e normalizar dados de localização** dos estudantes durante o cadastro. Em vez de permitir entrada manual de cidade (sujeita a erros de digitação e inconsistências), o sistema:

1. ✅ **Garante que o CEP existe** antes de aceitar o cadastro
2. ✅ **Normaliza o nome da cidade** usando dados oficiais dos Correios
3. ✅ **Obtém automaticamente o código IBGE** da cidade
4. ✅ **Previne dados inconsistentes** (ex: "Rio", "RJ", "Rio de Janeiro" seriam normalizados para "Rio de Janeiro")
5. ✅ **Enriquece o cadastro** com informações oficiais sem custo adicional

### Como é Usada?

A ViaCEP é chamada **exclusivamente** durante a **criação e atualização de estudantes**:

| Endpoint | Método | Quando Chama ViaCEP | Motivo |
|----------|--------|---------------------|--------|
| `POST /students` | CREATE | ✅ **Sempre** (antes de validar elegibilidade) | Validar CEP e obter cidade + código IBGE |
| `PUT /students/{id}` | UPDATE | ✅ **Sempre** (antes de atualizar) | Revalidar CEP e atualizar localização |
| `GET /students` | LIST | ❌ Nunca | Apenas consulta dados já persistidos |
| `GET /students/{id}` | READ | ❌ Nunca | Apenas consulta dados já persistidos |
| `DELETE /students/{id}` | DELETE | ❌ Nunca | Remoção não requer validação |

### Especificação Técnica

#### Endpoint Consultado

```http
GET https://viacep.com.br/ws/{cep}/json/
```

**Exemplo de Request:**
```bash
GET https://viacep.com.br/ws/20040020/json/
```

#### Response - CEP Válido (200 OK)

```json
{
  "cep": "20040-020",
  "logradouro": "Praça Floriano",
  "complemento": "- lado ímpar",
  "bairro": "Centro",
  "localidade": "Rio de Janeiro",
  "uf": "RJ",
  "ibge": "3304557",
  "gia": "",
  "ddd": "21",
  "siafi": "6001"
}
```

**Campos utilizados pelo UniBus:**
- `localidade` → Armazenado como `city`
- `ibge` → Armazenado como `city_ibge_code`
- `cep` → Armazenado como `cep` (formatado)

#### Response - CEP Inválido (200 OK)

```json
{
  "erro": true
}
```

Quando a ViaCEP retorna `{"erro": true}`, o UniBus rejeita o cadastro com **HTTP 400 Bad Request**.

### Fluxo de Integração

**Sequência ao criar um estudante:**

```
1. Cliente envia: name, email, cep
   ↓
2. UniBus valida formato do CEP (regex Pydantic)
   ↓
3. UniBus chama ViaCEP: GET https://viacep.com.br/ws/{cep}/json/
   ↓
4a. CEP válido → ViaCEP retorna dados
    → UniBus extrai: city (localidade) + city_ibge_code (ibge)
    → Continua para validação de elegibilidade (validation-api)
    ↓
4b. CEP inválido → ViaCEP retorna {"erro": true}
    → UniBus retorna HTTP 400: "Invalid CEP"
    → Cadastro abortado
```

### Exemplo de Uso Completo

#### Criar Estudante com CEP Válido

```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Silva",
    "email": "maria@aluno.puc.br",
    "cep": "20040-020"
  }'
```

**Processamento Interno:**

1. Pydantic valida formato do CEP: `20040-020` ✅
2. ViaCEP consultado: `GET https://viacep.com.br/ws/20040020/json/`
3. ViaCEP retorna:
   ```json
   {
     "localidade": "Rio de Janeiro",
     "ibge": "3304557",
     "uf": "RJ"
   }
   ```
4. Validation-api consultada com `registration: "20040020"` ✅
5. Estudante salvo no banco:

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Maria Silva",
  "email": "maria@aluno.puc.br",
  "cep": "20040-020",
  "city": "Rio de Janeiro",
  "city_ibge_code": "3304557",
  "created_at": "2025-12-15T14:30:00"
}
```

#### Criar Estudante com CEP Inválido

```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Santos",
    "email": "joao@aluno.ufrj.br",
    "cep": "99999-999"
  }'
```

**Processamento Interno:**

1. Pydantic valida formato: `99999-999` ✅
2. ViaCEP consultado: `GET https://viacep.com.br/ws/99999999/json/`
3. ViaCEP retorna: `{"erro": true}` ❌
4. UniBus aborta o cadastro

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid CEP: Invalid CEP"
}
```

### Tratamento de Erros

| Cenário | Comportamento UniBus | HTTP Status |
|---------|---------------------|-------------|
| CEP válido e encontrado | Continua com cadastro | - |
| CEP não encontrado (erro: true) | Rejeita cadastro | `400 Bad Request` |
| ViaCEP timeout (10s) | Rejeita cadastro | `400 Bad Request` |
| ViaCEP offline/indisponível | Rejeita cadastro | `400 Bad Request` |
| CEP com formato inválido | Rejeita antes de chamar API | `422 Unprocessable Entity` |

**⚠️ Importante:** Diferente da Validation-API (que tem fallback), a **ViaCEP não possui fallback**. Se a API estiver indisponível, o cadastro é rejeitado, pois a localização é considerada **informação crítica** para o sistema UniBus.

### Implementação Técnica

**Módulo dedicado:** `app/viacep.py`

```python
class ViaCEPClient:
    base_url = "https://viacep.com.br/ws"
    timeout = 10.0  # 10 segundos

    async def get_address(self, cep: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações de endereço pelo CEP.
        
        Returns:
            Dict com city, city_ibge_code, state, etc.
            ou None se CEP inválido/erro
        """
```

**Configuração:**
- Timeout: 10 segundos
- Método: GET assíncrono (httpx.AsyncClient)
- Tratamento: TimeoutException, RequestError, parsing errors
- Sem autenticação (API pública)

### Vantagens da Integração

✅ **Gratuita:** Sem custos ou limites de requisições  
✅ **Confiável:** Dados oficiais dos Correios  
✅ **Simples:** API RESTful sem autenticação  
✅ **Completa:** Retorna dados estruturados e padronizados  
✅ **Mantida:** Projeto ativo com suporte da comunidade  
✅ **Sem Cadastro:** Não requer API key ou registro prévio  

### Limitações e Considerações

⚠️ **Sem SLA oficial:** API comunitária sem garantias de uptime  
⚠️ **Dependência externa:** Cadastro de estudantes depende da disponibilidade da API  
⚠️ **Apenas Brasil:** Válido apenas para CEPs brasileiros  
⚠️ **Sem fallback:** Se a API estiver offline, cadastros são bloqueados  

**Mitigação:** Para ambientes de produção críticos, considere:
- Cache de CEPs consultados (Redis)
- Retry automático com backoff exponencial
- Monitoramento de disponibilidade da API
- Plano de contingência (banco de dados local de CEPs)

### CEPs de Teste

Para testes e desenvolvimento, use CEPs válidos:

| CEP | Cidade | Estado | IBGE |
|-----|--------|--------|------|
| `20040-020` | Rio de Janeiro | RJ | 3304557 |
| `01310-100` | São Paulo | SP | 3550308 |
| `30190-001` | Belo Horizonte | MG | 3106200 |
| `40020-000` | Salvador | BA | 2927408 |
| `70040-902` | Brasília | DF | 5300108 |

### Alternativas Consideradas

Durante o planejamento do MVP, outras opções foram avaliadas:

| API | Status | Motivo da Não Escolha |
|-----|--------|----------------------|
| BrasilAPI | ❌ | Menos popular, menor documentação |
| CEPAberto | ❌ | Requer cadastro e API key |
| Google Maps API | ❌ | Paga, exige configuração complexa |
| Postmon | ❌ | Projeto descontinuado |
| **ViaCEP** | ✅ **Escolhida** | Gratuita, simples, confiável, bem documentada |

### Recursos Adicionais

- 📖 **Documentação oficial:** https://viacep.com.br/
- 🐙 **Repositório GitHub:** https://github.com/IgorHalfeld/viacep
- 📊 **Status da API:** Sem página oficial de status
- 💬 **Suporte:** Comunidade via GitHub Issues

---

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
- `POST /routes` - Criar nova rota
- `PUT /routes/{id}` - Atualizar rota
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
- `VALIDATION_API_URL` - URL da student-validation-api (padrão: `http://localhost:8001`)
- `VALIDATION_API_TIMEOUT` - Timeout em segundos (padrão: `10.0`)

**5. Inicie o PostgreSQL (via Docker)**

```bash
# Opção A: Usar docker-compose (mais fácil)
docker-compose up -d postgres

# Opção B: Rodar PostgreSQL standalone
docker run -d \
  --name postgres-unibus \
  -e POSTGRES_USER=unibus_user \
  -e POSTGRES_PASSWORD=unibus_pass \
  -e POSTGRES_DB=unibus_db \
  -p 5433:5432 \
  postgres:15-alpine
```

**6. Execute a aplicação**

```bash
# Definir variável de ambiente do banco
export DATABASE_URL=postgresql://unibus_user:unibus_pass@localhost:5433/unibus_db

# Rodar aplicação
uvicorn app.main:app --reload --port 8000

# Ou usando o ambiente virtual diretamente
.venv/bin/uvicorn app.main:app --reload --port 8000
```

**7. Acesse a API**

- **API Base:** http://localhost:8000
- **Swagger UI (Docs Interativos):** http://localhost:8000/docs
- **ReDoc (Docs Alternativos):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **PostgreSQL:** localhost:5433 (user: unibus_user, pass: unibus_pass, db: unibus_db)

### 🐳 Deploy com Docker

**Opção 1: Docker Compose (Recomendado)**

Inicia PostgreSQL e a API automaticamente:

```bash
# Subir todos os serviços (PostgreSQL + API)
docker-compose up --build

# Rodar em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Parar e remover volumes (apaga dados do banco)
docker-compose down -v
```

**Opção 2: Docker simples (requer PostgreSQL externo)**

```bash
# Build da imagem
docker build -t unibus-core-api:latest .

# Executar container
docker run -d \
  --name unibus-core \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://unibus_user:unibus_pass@host.docker.internal:5432/unibus_db \
  -e VALIDATION_API_URL=http://host.docker.internal:8001 \
  unibus-core-api:latest

# Ver logs
docker logs -f unibus-core

# Parar e remover
docker stop unibus-core && docker rm unibus-core
```

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL de conexão PostgreSQL | `postgresql://unibus_user:unibus_pass@localhost:5432/unibus_db` |
| `VALIDATION_API_URL` | URL base da Student Validation API | `http://localhost:8001` |
| `VALIDATION_API_TIMEOUT` | Timeout para requisições à validation-api (segundos) | `10.0` |

**Arquivo `.env.example` fornecido como template.**

### Configuração PostgreSQL (Docker Compose)

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `POSTGRES_USER` | `unibus_user` | Usuário do banco |
| `POSTGRES_PASSWORD` | `unibus_pass` | Senha do banco |
| `POSTGRES_DB` | `unibus_db` | Nome do banco |
| Porta | `5433:5432` | Porta mapeada (5433 no host → 5432 no container) |

## 📋 Regras de Negócio

### Criação de Estudantes

O processo de criação de estudantes envolve **duas validações em APIs externas**:

#### 1. Validação de CEP (ViaCEP - API Pública Gratuita)

1. **Validação de formato:** Pydantic valida que o CEP segue o padrão `12345-678` ou `12345678`
2. **Consulta à ViaCEP:** Sistema consulta `https://viacep.com.br/ws/{cep}/json/`
3. **CEP válido:** Extrai `city` (localidade) e `city_ibge_code` (IBGE) automaticamente
4. **CEP inválido:** Retorna HTTP 400 (Bad Request) com mensagem "Invalid CEP"
5. **ViaCEP offline:** Retorna HTTP 400 (sem fallback - localização é crítica)

#### 2. Validação de Elegibilidade (Validation API)

1. **Chamada automática:** Após validar CEP, chama validation-api passando `name`, `email` e `cep` (como registration)
2. **Sucesso (estudante válido):** Retorna HTTP 201 (Created) com dados completos
3. **Falha (estudante inválido):** Retorna HTTP 400 (Bad Request) com motivo da rejeição
4. **Fallback (validation-api offline):** Aceita estudante por padrão e retorna HTTP 201

**Regras de validação na validation-api:**
- Email institucional: deve conter `@aluno` ou `.edu.br`
- Registration (CEP): deve ter pelo menos 6 caracteres (CEPs sempre têm 8 dígitos, então sempre passa)

**Fluxo completo:**
```
POST /students (name, email, cep)
  ↓
1. Validação Pydantic (formato)
  ↓
2. ViaCEP: valida CEP → extrai city + city_ibge_code
  ↓
3. Validation API: valida email institucional
  ↓
4. Salva no PostgreSQL com dados normalizados
  ↓
Retorna HTTP 201 com estudante completo
```

### Criação/Atualização de Rotas

1. **Campos opcionais:** `distance_km` e `estimated_duration_min` são opcionais e podem ser preenchidos manualmente
2. **Validação de cidades:** `origin_city` e `destination_city` são obrigatórios

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

### Criar um Estudante (com CEP)

```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao.silva@aluno.puc.br",
    "cep": "20040-020"
  }'
```

**Resposta (201 Created):**
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao.silva@aluno.puc.br",
  "cep": "20040-020",
  "city": "Rio de Janeiro",
  "city_ibge_code": "3304557",
  "created_at": "2025-12-15T12:00:00"
}
```

**Nota:** Os campos `city` e `city_ibge_code` são automaticamente preenchidos pela integração com ViaCEP.

### Criar uma Rota

```bash
curl -X POST "http://localhost:8000/routes" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Rio - São Paulo Express",
    "origin_city": "Rio de Janeiro",
    "destination_city": "São Paulo"
  }'
```

**Resposta (201 Created):**
```json
{
  "id": 1,
  "name": "Rio - São Paulo Express",
  "origin_city": "Rio de Janeiro",
  "destination_city": "São Paulo",
  "distance_km": null,
  "estimated_duration_min": null
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

A aplicação usa **PostgreSQL 15** para persistência robusta e escalável. O banco roda em container Docker com volume persistente.

### Tabelas Criadas

```sql
-- students
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    cep VARCHAR NOT NULL,
    city VARCHAR NOT NULL,
    city_ibge_code VARCHAR NOT NULL,
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

**Via psql (PostgreSQL CLI):**

```bash
# Conectar ao PostgreSQL no Docker
docker exec -it unibus-postgres psql -U unibus_user -d unibus_db

# Dentro do psql:
\dt                    # Listar tabelas
\d students           # Descrever tabela students
\d+ routes            # Detalhes completos da tabela routes
SELECT * FROM students; # Query SQL
\q                    # Sair
```

**Via Python (SQLAlchemy):**

```bash
.venv/bin/python -c "
from app.db import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tabelas:', inspector.get_table_names())
for table in inspector.get_table_names():
    print(f'\n{table}:')
    for col in inspector.get_columns(table):
        print(f"  - {col['name']}: {col['type']}")
"
```

**Via pgAdmin ou DBeaver:**

- Host: `localhost`
- Port: `5433`
- Database: `unibus_db`
- User: `unibus_user`
- Password: `unibus_pass`

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
- Criação de rota
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

**PostgreSQL em Produção:**

```python
# Usar serviços gerenciados
DATABASE_URL=postgresql://user:password@db-host:5432/unibus_prod

# Opções recomendadas:
# - AWS RDS PostgreSQL
# - Azure Database for PostgreSQL
# - Google Cloud SQL
# - Supabase
# - Neon

# Configurações de produção em app/db.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Conexões no pool
    max_overflow=10,       # Conexões extras
    pool_pre_ping=True,    # Verificar conexões
    pool_recycle=3600      # Reciclar após 1h
)
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
