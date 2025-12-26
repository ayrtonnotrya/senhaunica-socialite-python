# Senha Única Socialite Python

**Versão da Documentação:** 1.0.0
**Status:** *Draft / Specification*
**Compatibilidade:** Python 3.14.2 | Django 5.2.9 | Poetry

## 1. Introdução

O pacote `senhaunica-socialite-python` é uma re-implementação idiomática para o ecossistema Python da biblioteca PHP [uspdev/senhaunica-socialite](https://github.com/uspdev/senhaunica-socialite).

Esta biblioteca abstrai a complexidade do protocolo **OAuth 1.0a (RFC 5849)** utilizado pelo sistema de autenticação corporativa da Universidade de São Paulo (USP). Seu objetivo principal é fornecer um Backend de Autenticação *plug-and-play* para aplicações Django, permitindo que usuários façam login utilizando suas credenciais institucionais (Número USP).

### Importância Institucional
A padronização da autenticação é crucial para a segurança dos dados da universidade. Este pacote garante:
1.  **Conformidade:** Implementação estrita do *handshake* OAuth 1.0 exigido pela STI-USP.
2.  **Manutenibilidade:** Reduz a duplicidade de código de autenticação em diversos sistemas Python da universidade.
3.  **Interoperabilidade:** Facilita a migração de sistemas legados (PHP) para arquiteturas modernas (Python/Django) mantendo a mesma lógica de negócio.

---

## 2. Guia de Instalação

Utilizamos o **Poetry** para gestão de dependências e empacotamento. Certifique-se de que seu ambiente possui o Python 3.14.2 ativo.

### Instalação via Poetry

No diretório raiz do seu projeto Django, execute:

```bash
poetry add git+ssh://git@github.com/ayrtonnotrya/senhaunica-socialite-python.git

# Ou via HTTPS
poetry add git+https://github.com/ayrtonnotrya/senhaunica-socialite-python.git
```

### Dependências Core
O pacote instalará automaticamente as seguintes dependências críticas:
*   `Authlib`: Para implementação robusta do cliente OAuth 1.0.
*   `SQLAlchemy`: Para persistência agnóstica de logs de auditoria e mapeamento de usuários (caso opte por não usar o ORM do Django exclusivamente).
*   `Requests`: Para chamadas HTTP aos endpoints da USP.

---

## 3. Configuração de Ambiente

Seguindo a filosofia *The Twelve-Factor App* e mantendo a paridade com a biblioteca original em PHP, as configurações devem ser injetadas via variáveis de ambiente.

Crie ou atualize seu arquivo `.env` com as chaves abaixo. As chaves devem ser solicitadas à STI ou geradas no portal da USP Digital para o ambiente de homologação/produção.

| Variável | Descrição | Exemplo |
| :--- | :--- | :--- |
| `SENHAUNICA_KEY` | *Consumer Key* fornecida pela USP. | `ff8a...` |
| `SENHAUNICA_SECRET` | *Consumer Secret* fornecida pela USP. | `a1b2...` |
| `SENHAUNICA_CALLBACK_ID` | ID de callback registrado junto à STI. **Obrigatório**. Define para onde a USP redirecionará o usuário. | `88` |
| `SENHAUNICA_ENV` | Define os endpoints (`dev` ou `prod`). | `prod` |


> **Nota Técnica:** Diferente do OAuth 2.0, o OAuth 1.0a assina as requisições usando o *Secret*. Nunca comite este arquivo no controle de versão.

---

## 4. Implementação no Django

A integração ocorre através de um *Custom Authentication Backend*.

### 4.1. Registrar o Backend e Apps

No arquivo `settings.py` do seu projeto Django:

```python
# settings.py

INSTALLED_APPS = [
    # ... apps nativos
    'senhaunica_socialite',  # Nosso pacote
]

AUTHENTICATION_BACKENDS = [
    'senhaunica_socialite.backends.SenhaUnicaBackend', # Backend Customizado
    'django.contrib.auth.backends.ModelBackend',       # Fallback (opcional)
]

# Configurações do SQLAlchemy (se utilizado para persistência híbrida)
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
```

### 4.2. Configuração de Rotas (URLconf)

Você precisa expor as rotas que iniciam o fluxo OAuth e recebem o callback. No `urls.py`:

```python
# urls.py
from django.urls import path
from senhaunica_socialite import views

urlpatterns = [
    # Rota que redireciona o usuário para a tela de login da USP
    path('login/usp/', views.login_init, name='login_usp'),
    
    # Rota de retorno (Callback) que processa o token e cria a sessão
    path('callback/', views.login_callback, name='callback_usp'),
]
```

### 4.3. Fluxo de Funcionamento (Resumo Técnico)

1.  **Login Init:** A view `login_init` utiliza `Authlib` para solicitar um *Request Token* temporário à USP e redireciona o usuário para `uspdigital.usp.br`.
2.  **Autorização:** O usuário digita a senha única.
3.  **Callback:** A USP redireciona para `/callback/` com um `oauth_verifier`.
4.  **Troca de Token:** O pacote troca o *Request Token* + *Verifier* pelo *Access Token*.
5.  **Obtenção de Dados:** O pacote consulta o endpoint `/wsusuario/oauth/usuariousp`.
    *   Mapeamento Automático:
        *   `loginUsuario` (ou `codpes`) -> `User.username`
        *   `nomeUsuario` (ou `nompes`) -> `User.first_name`
        *   `emailPrincipalUsuario` -> `User.email`
6.  **User Binding:** O `SenhaUnicaBackend` cria ou atualiza o usuário no Django e inicia a sessão.

---
