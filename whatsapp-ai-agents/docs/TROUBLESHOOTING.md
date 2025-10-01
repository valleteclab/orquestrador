# Solução para Erro de Instalação: ModuleNotFoundError distutils

## Problema
Ao instalar as dependências do projeto, você pode encontrar o seguinte erro:
```
ModuleNotFoundError: No module named 'distutils'
```

## Causa
Este erro ocorre porque versões mais recentes do Python (3.12+) não incluem o módulo `distutils` por padrão, que é necessário para compilar alguns pacotes Python.

## Soluções

### Solução 1: Instalar pacotes do sistema necessários
```bash
# Instalar pacotes necessários para Python
sudo apt update
sudo apt install -y python3-distutils python3-setuptools python3-dev build-essential

# Se estiver usando Python 3.12+, também instale:
sudo apt install -y python3-wheel
```

### Solução 2: Usar uma versão compatível do Python
Recomendamos usar Python 3.10 que tem melhor compatibilidade com as dependências do projeto:

```bash
# Instalar Python 3.10 (se não estiver disponível)
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Criar ambiente virtual com Python 3.10
python3.10 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip, setuptools e wheel
pip install --upgrade pip setuptools wheel
```

### Solução 3: Atualizar dependências do projeto
Se ainda encontrar problemas, atualize as dependências no `requirements.txt`:

```bash
# No ambiente virtual ativo
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Verificação
Após aplicar uma das soluções, verifique se o problema foi resolvido:

```bash
# Testar importação do distutils
python -c "import distutils; print('distutils importado com sucesso')"

# Testar instalação de pacotes
pip install flask
```

## Erro: No module named 'twilio'

### Problema
Ao executar a aplicação, você pode encontrar o seguinte erro:
```
ModuleNotFoundError: No module named 'twilio'
```

### Causa
Este erro ocorre porque a aplicação ainda referencia o módulo Twilio mesmo após a migração para Chatwoot.

### Solução
Instale o pacote Twilio mesmo que não seja usado diretamente:

```bash
# No ambiente virtual ativo
pip install twilio
```

Ou atualize o requirements.txt para incluir:
```
twilio>=8.0.0
```

## Erro: OPENAI_API_KEY não configurada

### Problema
Ao tentar usar os agentes de IA, você pode receber erros relacionados à autenticação da OpenAI.

### Solução
Certifique-se de configurar corretamente a chave da API da OpenAI no arquivo `.env`:

```bash
# No arquivo src/config/.env
OPENAI_API_KEY=sua_chave_api_aqui
```

## Erro: Conexão com Chatwoot

### Problema
Problemas ao conectar com a instância do Chatwoot.

### Soluções
1. Verifique se as credenciais estão corretas no `.env`:
   ```
   CHATWOOT_URL=https://chat.sisgov.app.br
   CHATWOOT_API_TOKEN=seu_token_aqui
   CHATWOOT_INBOX_ID=seu_inbox_id_aqui
   ```

2. Teste a conexão manualmente:
   ```bash
   curl -H "Authorization: Bearer seu_token_aqui" \
        https://chat.sisgov.app.br/api/v1/inboxes/seu_inbox_id_aqui
   ```

3. Verifique se o webhook está configurado corretamente no Chatwoot:
   - URL do webhook: `http://seu-dominio.com/webhook`
   - Token de verificação: `sua_chave_secreta_aqui`

Se nenhuma das soluções acima resolver, entre em contato com a equipe de suporte.