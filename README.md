# FastAPI RBAC - Sistema Robusto de Controle de Acesso Baseado em Funções

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Descrição

Sistema completo e robusto de **RBAC (Role-Based Access Control)** construído com FastAPI, oferecendo autenticação JWT, operações CRUD completas e gerenciamento flexível de permissões através de roles e grupos.

### Principais Características

- **Autenticação JWT** - Sistema seguro de autenticação com tokens Bearer
- **Hash de Senhas** - Senhas criptografadas com bcrypt
- **CRUD Completo** - APIs RESTful para usuários, roles e grupos
- **Validação de Dados** - Schemas Pydantic para validação robusta
- **Tratamento de Erros** - Sistema de exceções customizadas com logs estruturados
- **Sessões de Banco Seguras** - Gerenciamento adequado de sessões SQLAlchemy
- **Configuração por Ambiente** - Suporte a variáveis de ambiente com pydantic-settings
- **Docker Otimizado** - Build multi-stage com usuário não-root
- **Documentação OpenAPI** - Swagger UI e ReDoc incluídos
- **Exemplos Práticos** - Endpoints demonstrando diferentes níveis de permissão

## Tecnologias Utilizadas

- **FastAPI** - Framework web assíncrono moderno
- **SQLAlchemy 2.0** - ORM poderoso para Python
- **Pydantic** - Validação de dados e configuração
- **PyJWT** - Implementação de JSON Web Tokens
- **Passlib** - Hashing seguro de senhas
- **Uvicorn** - Servidor ASGI de alta performance
- **PDM** - Gerenciador de dependências moderno
- **Docker** - Containerização da aplicação

## Arquitetura RBAC

Este sistema implementa um modelo RBAC de três camadas:

```
Usuário (User)
    ↓
    ├── Roles Diretos (Direct Roles)
    └── Grupos (Groups)
            ↓
            └── Roles do Grupo (Group Roles)
```

### Conceitos

- **User**: Usuário do sistema com credenciais de autenticação
- **Role**: Permissão ou função (ex: "admin", "moderator", "user")
- **Group**: Conjunto de roles para facilitar gerenciamento
- **Permissões**: Usuário tem permissão se possui role direta OU através de grupo

## Instalação e Configuração

### Pré-requisitos

- Python 3.12+
- PDM (Python Development Master)
- Docker e Docker Compose (opcional)

### 1. Clonar o Repositório

```bash
git clone https://github.com/victorgabrieldeon/fastapi-RBAc.git
cd fastapi-RBAc
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Application Settings
APP_NAME="FastAPI RBAC"
DEBUG=true

# Security Settings
SECRET_KEY="your-secret-key-change-in-production-use-openssl-rand-hex-32"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Settings
DATABASE_URL="sqlite:///./rbac.db"
```

### 3. Instalar Dependências

```bash
pdm install
```

### 4. Executar a Aplicação

#### Usando PDM:

```bash
pdm start
```

#### Usando Docker Compose:

```bash
docker-compose up --build
```

A API estará disponível em: **http://localhost:8000**

- **Documentação Swagger**: http://localhost:8000/docs
- **Documentação ReDoc**: http://localhost:8000/redoc

## Usuários de Teste

O sistema cria automaticamente usuários de exemplo na primeira execução:

| Usuário | Senha | Roles | Descrição |
|---------|-------|-------|-----------|
| `admin` | `admin123` | admin (via grupo) | Administrador completo |
| `moderator` | `mod123` | moderator (via grupo) | Moderador com acesso limitado |
| `user` | `user123` | user (via grupo) | Usuário regular |
| `superadmin` | `super123` | admin + superuser | Super administrador |

## Exemplos de Uso

### 1. Autenticação

#### Login e Obtenção de Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Obter Informações do Usuário Atual

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <seu_token>"
```

### 2. Endpoints Públicos e Protegidos

#### Endpoint Público (sem autenticação)

```bash
curl -X GET "http://localhost:8000/public"
```

#### Endpoint Protegido (requer autenticação)

```bash
curl -X GET "http://localhost:8000/authenticated" \
  -H "Authorization: Bearer <seu_token>"
```

#### Endpoint Admin (requer role "admin")

```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer <token_admin>"
```

#### Endpoint com Múltiplas Permissões (requer "admin" OU "moderator")

```bash
curl -X GET "http://localhost:8000/moderator" \
  -H "Authorization: Bearer <token_admin_ou_moderator>"
```

#### Endpoint Super Admin (requer "admin" E "superuser")

```bash
curl -X GET "http://localhost:8000/superuser" \
  -H "Authorization: Bearer <token_superadmin>"
```

### 3. Gerenciamento de Usuários

#### Criar Novo Usuário (requer admin)

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "joao",
    "password": "senha123",
    "email": "joao@example.com"
  }'
```

#### Listar Usuários (requer admin)

```bash
curl -X GET "http://localhost:8000/users?skip=0&limit=10" \
  -H "Authorization: Bearer <token_admin>"
```

#### Obter Usuário por ID

```bash
curl -X GET "http://localhost:8000/users/1" \
  -H "Authorization: Bearer <seu_token>"
```

#### Atualizar Usuário

```bash
curl -X PATCH "http://localhost:8000/users/1" \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "joao_silva",
    "email": "joao.silva@example.com"
  }'
```

#### Deletar Usuário (requer admin)

```bash
curl -X DELETE "http://localhost:8000/users/1" \
  -H "Authorization: Bearer <token_admin>"
```

### 4. Gerenciamento de Roles

#### Criar Nova Role (requer admin)

```bash
curl -X POST "http://localhost:8000/roles" \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "editor",
    "description": "Editor de conteúdo"
  }'
```

#### Listar Todas as Roles

```bash
curl -X GET "http://localhost:8000/roles" \
  -H "Authorization: Bearer <seu_token>"
```

#### Obter Role por ID

```bash
curl -X GET "http://localhost:8000/roles/1" \
  -H "Authorization: Bearer <seu_token>"
```

### 5. Gerenciamento de Grupos

#### Criar Novo Grupo (requer admin)

```bash
curl -X POST "http://localhost:8000/groups" \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "editores",
    "description": "Grupo de editores",
    "role_ids": [1, 2]
  }'
```

#### Listar Todos os Grupos

```bash
curl -X GET "http://localhost:8000/groups" \
  -H "Authorization: Bearer <seu_token>"
```

### 6. Atribuição de Roles e Grupos

#### Atribuir Role Direta ao Usuário (requer admin)

```bash
curl -X POST "http://localhost:8000/users/1/roles" \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": 2
  }'
```

#### Remover Role do Usuário (requer admin)

```bash
curl -X DELETE "http://localhost:8000/users/1/roles/2" \
  -H "Authorization: Bearer <token_admin>"
```

#### Atribuir Grupo ao Usuário (requer admin)

```bash
curl -X POST "http://localhost:8000/users/1/groups" \
  -H "Authorization: Bearer <token_admin>" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": 1
  }'
```

#### Remover Grupo do Usuário (requer admin)

```bash
curl -X DELETE "http://localhost:8000/users/1/groups/1" \
  -H "Authorization: Bearer <token_admin>"
```

## Exemplos com Python

### Usando requests

```python
import requests

# URL base da API
BASE_URL = "http://localhost:8000"

# 1. Fazer login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)
token = login_response.json()["access_token"]

# 2. Headers com token
headers = {
    "Authorization": f"Bearer {token}"
}

# 3. Criar novo usuário
new_user = requests.post(
    f"{BASE_URL}/users",
    headers=headers,
    json={
        "name": "maria",
        "password": "senha123",
        "email": "maria@example.com"
    }
)
print("Usuário criado:", new_user.json())

# 4. Listar usuários
users = requests.get(f"{BASE_URL}/users", headers=headers)
print("Usuários:", users.json())

# 5. Criar role
role = requests.post(
    f"{BASE_URL}/roles",
    headers=headers,
    json={
        "name": "editor",
        "description": "Editor de conteúdo"
    }
)
role_id = role.json()["id"]

# 6. Atribuir role ao usuário
assign = requests.post(
    f"{BASE_URL}/users/1/roles",
    headers=headers,
    json={"role_id": role_id}
)
print("Role atribuída:", assign.json())
```

### Usando httpx (async)

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Login
        login = await client.post(
            "http://localhost:8000/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Obter informações do usuário atual
        me = await client.get(
            "http://localhost:8000/auth/me",
            headers=headers
        )
        print("Usuário atual:", me.json())

        # Listar roles
        roles = await client.get(
            "http://localhost:8000/roles",
            headers=headers
        )
        print("Roles disponíveis:", roles.json())

asyncio.run(main())
```

## Estrutura do Projeto

```
fastapi-RBAc/
├── src/
│   ├── main/
│   │   ├── app.py              # Aplicação FastAPI principal
│   │   ├── config.py           # Configurações da aplicação
│   │   ├── dependencies.py     # Dependências FastAPI (auth, etc)
│   │   ├── exceptions.py       # Exceções customizadas
│   │   ├── logging_config.py   # Configuração de logging
│   │   ├── schemas.py          # Schemas Pydantic
│   │   ├── security.py         # JWT e hashing de senhas
│   │   └── routers/
│   │       ├── auth.py         # Endpoints de autenticação
│   │       ├── users.py        # Endpoints de usuários
│   │       ├── roles.py        # Endpoints de roles
│   │       ├── groups.py       # Endpoints de grupos
│   │       └── __init__.py
│   └── infra/
│       └── db/
│           ├── models.py       # Modelos SQLAlchemy
│           ├── utils.py        # Funções utilitárias do banco
│           └── base_repository.py
├── .env.example                # Exemplo de variáveis de ambiente
├── .dockerignore               # Arquivos ignorados no build Docker
├── .gitignore                  # Arquivos ignorados pelo Git
├── docker-compose.yml          # Configuração Docker Compose
├── Dockerfile                  # Build da imagem Docker
├── pyproject.toml              # Configuração do projeto e dependências
└── README.md                   # Este arquivo
```

## Recursos de Segurança

- **Senhas Hash**: Todas as senhas são hashadas com bcrypt antes de serem armazenadas
- **JWT Tokens**: Autenticação stateless com tokens que expiram
- **Validação de Entrada**: Schemas Pydantic validam todos os dados de entrada
- **Tratamento de Erros**: Exceções customizadas ocultam detalhes sensíveis em produção
- **Sessões Seguras**: Gerenciamento adequado de sessões do banco de dados
- **Docker Non-Root**: Container executa com usuário não privilegiado
- **CORS Configurável**: Controle de origens permitidas

## Desenvolvimento

### Executar Linter

```bash
pdm run ruff check src/
```

### Estrutura de Logs

A aplicação usa logging estruturado com diferentes níveis:

- **INFO**: Operações normais (criação de usuário, login, etc)
- **WARNING**: Erros de validação, tentativas de acesso negadas
- **ERROR**: Erros de banco de dados, exceções não tratadas
- **DEBUG**: Informações detalhadas (apenas em modo debug)

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `APP_NAME` | Nome da aplicação | FastAPI RBAC |
| `DEBUG` | Modo debug | false |
| `SECRET_KEY` | Chave secreta para JWT | (gerado) |
| `ALGORITHM` | Algoritmo JWT | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token | 30 |
| `DATABASE_URL` | URL de conexão do banco | sqlite:///./rbac.db |

## Melhorias Futuras

- [ ] Refresh tokens para sessões longas
- [ ] Permissões granulares por recurso
- [ ] Auditoria de acessos e mudanças
- [ ] Suporte a PostgreSQL e MySQL
- [ ] Rate limiting por usuário/IP
- [ ] Testes unitários e de integração
- [ ] CI/CD com GitHub Actions
- [ ] Migrations com Alembic

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Autor

**Victor Gabriel Deon**
- GitHub: [@victorgabrieldeon](https://github.com/victorgabrieldeon)
- Email: victordeonroyale@gmail.com

## Agradecimentos

- FastAPI pela excelente documentação
- Comunidade Python pelo suporte
- Todos os contribuidores do projeto

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
