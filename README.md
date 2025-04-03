# 🚀 FastAPI RBAC Example 🔐

**📜 Descrição:** API em ⚡ FastAPI com controle de acesso 🔑 baseado em funções (RBAC) usando 🐍 SQLAlchemy e gerenciada com 🛠️ PDM.

Este projeto é um exemplo de como implementar **RBAC (Role-Based Access Control) 🔄** em uma API utilizando **FastAPI ⚡** e **SQLAlchemy 🐍**, além de ser gerenciado com **PDM 📦** e executado com **Docker Compose 🐳**.

## 🏗️ Tecnologias Utilizadas

- ⚡ **FastAPI** - Framework assíncrono para APIs em Python 🐍
- 🐍 **SQLAlchemy** - ORM para manipulação do banco de dados 💾
- 📦 **PDM** - Gerenciador de dependências e ambientes para Python 🚀
- 🐳 **Docker Compose** - Para orquestração de containers Docker 🏗️

## 🔎 O que é RBAC?

O **RBAC (Role-Based Access Control) 🔑** é um modelo de controle de acesso baseado em funções 🎭. Ele permite que permissões sejam atribuídas a funções específicas 🎟️, em vez de diretamente a usuários 👤. Isso facilita a administração de permissões em sistemas complexos 💡.

### 🎯 Vantagens do RBAC:
1. 🔒 **Maior segurança** - Restringe o acesso a funcionalidades sensíveis apenas a usuários autorizados 🛡️.
2. ⚙️ **Facilidade de gerenciamento** - As permissões são definidas por função, tornando mais simples a concessão ou revogação de acessos 📋.
3. 📈 **Escalabilidade** - Ideal para sistemas grandes onde diferentes usuários têm níveis variados de acesso 🌍.

## 🚀 Como Executar o Projeto - PDM

### 1️⃣ Clonar o repositório:
```bash
🐙 git clone https://github.com/victorgabrieldeon/fastapi-RBAc.git
📂 cd fastapi-RBAc
```

### 2️⃣ Instalar dependências com PDM 📦:
```bash
📦 pdm install
```

### 3️⃣ Executar aplicação usando o PDM 🚀:
```bash
pdm start
```

## 🚀 Como Executar o Projeto - Docker

### 1️⃣ Rodar a aplicação com Docker Compose 🐳:
```bash
🐳 docker-compose up --build
```

🌍 A API estará disponível em: **http://127.0.0.1:8000**

## 🔑 Exemplo de Usuários e Roles 🎭

O sistema conta com 2 rotas `/public` `/protect`:
- `/public` Rota publica para todos os usuários.
- `/protect` Rota permitida apenas para quem tem o Role "admin".

## Observações 🔭
Ao iniciar a aplicação, será criado 2 usuários:
um será usuário comum, sem cargos ou grupo, 
e o outro será criado com o cargo de admin.

Será exibido o ID de ambos no terminal da aplicação, no qual será possivel testar nos endpoints.

## 📜 Licença 📄

Este projeto é distribuído sob a licença MIT 📃. Sinta-se à vontade para modificá-lo e usá-lo como base para seus projetos! 💡

---

### 📢 Contribuições 🤝
🐙 Pull requests são bem-vindos! Se tiver alguma sugestão, abra uma issue 🔥. 🚀

