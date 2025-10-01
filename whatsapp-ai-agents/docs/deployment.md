# Deployment em VPS
## Guia Completo para Implantação em Servidor Privado Virtual

### Requisitos do Sistema

#### Requisitos Mínimos
- 2 vCPUs ou mais
- 4GB RAM
- 20GB espaço em disco
- Ubuntu 20.04 LTS ou superior (recomendado)
- Python 3.8 a 3.10 (3.11+ pode ter compatibilidade limitada com algumas dependências)
- Acesso root ou sudo

#### Requisitos Recomendados
- 4 vCPUs
- 8GB RAM
- 50GB espaço em disco SSD
- Ubuntu 22.04 LTS
- Python 3.10
- Firewall configurado

### Preparação do Ambiente

#### 1. Atualização do Sistema
```bash
# Atualizar pacotes do sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências do sistema
sudo apt install -y python3 python3-pip python3-venv python3-dev git redis-server nginx supervisor build-essential

# Instalar dependências necessárias para Python (resolve o problema do distutils)
sudo apt install -y python3-distutils python3-setuptools

# Verificar versões instaladas
python3 --version
pip3 --version
```

#### 2. Configuração do Firewall
```bash
# Habilitar UFW (Uncomplicated Firewall)
sudo ufw enable

# Permitir acesso SSH
sudo ufw allow ssh

# Permitir acesso HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar status do firewall
sudo ufw status
```

#### 3. Configuração do Redis
```bash
# Iniciar e habilitar Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar status
sudo systemctl status redis-server
```

### Resolução de Problemas Comuns

#### Problema: ModuleNotFoundError: No module named 'distutils'
Este erro ocorre porque o Python 3.12+ não inclui o módulo distutils por padrão. Para resolver:

```bash
# Instalar pacotes necessários para Python 3.12+
sudo apt install -y python3-distutils python3-setuptools

# Ou se estiver usando Python 3.12+, instale:
sudo apt install -y python3-dev python3-wheel
```

#### Problema: Erros com setuptools
Se encontrar erros relacionados ao setuptools:

```bash
# Atualizar pip, setuptools e wheel
pip install --upgrade pip setuptools wheel

# Ou instalar versões específicas compatíveis
pip install "setuptools<66" "wheel<0.39"
```

### Implantação da Aplicação

#### 1. Clonar o Repositório
```bash
# Criar diretório para a aplicação
sudo mkdir -p /opt/whatsapp-ai-agents
sudo chown $USER:$USER /opt/whatsapp-ai-agents

# Clonar o repositório
cd /opt/whatsapp-ai-agents
git clone [URL_DO_SEU_REPOSITORIO] .

# Ou se estiver fazendo upload manual, copie os arquivos para este diretório
```

#### 2. Configurar Ambiente Virtual Python
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar pip, setuptools e wheel no ambiente virtual
pip install --upgrade pip setuptools wheel

# Instalar dependências
pip install -r requirements.txt

# Instalar Gunicorn para produção
pip install gunicorn
```

#### 3. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp src/config/.env.example src/config/.env

# Editar configurações
nano src/config/.env

# Configurações importantes:
# - OPENAI_API_KEY (obrigatório)
# - CHATWOOT_URL (URL da sua instância Chatwoot)
# - CHATWOOT_API_TOKEN (token de API do Chatwoot)
# - CHATWOOT_INBOX_ID (ID da inbox do WhatsApp)
# - REDIS_HOST (geralmente localhost)
# - REDIS_PORT (geralmente 6379)
```

### Configuração do Serviço com Systemd

#### 1. Criar Arquivo de Serviço
```bash
# Criar arquivo de serviço systemd
sudo nano /etc/systemd/system/whatsapp-ai-agents.service
```

#### 2. Conteúdo do Arquivo de Serviço
```ini
[Unit]
Description=WhatsApp AI Agents Service
After=network.target redis-server.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/whatsapp-ai-agents
Environment=PATH=/opt/whatsapp-ai-agents/venv/bin
ExecStart=/opt/whatsapp-ai-agents/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 src.main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. Iniciar e Habilitar o Serviço
```bash
# Recarregar configurações do systemd
sudo systemctl daemon-reload

# Iniciar o serviço
sudo systemctl start whatsapp-ai-agents

# Habilitar inicialização automática
sudo systemctl enable whatsapp-ai-agents

# Verificar status
sudo systemctl status whatsapp-ai-agents
```

### Configuração do Nginx (Proxy Reverso)

#### 1. Criar Arquivo de Configuração
```bash
# Criar arquivo de configuração do Nginx
sudo nano /etc/nginx/sites-available/whatsapp-ai-agents
```

#### 2. Conteúdo da Configuração
```nginx
server {
    listen 80;
    server_name seu-dominio.com;  # Substitua pelo seu domínio ou IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Configuração específica para webhooks do Chatwoot
    location /webhook {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Chatwoot-Token $http_x_chatwoot_token;
        
        # Aumentar timeouts para webhooks
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### 3. Habilitar o Site
```bash
# Criar link simbólico para habilitar o site
sudo ln -s /etc/nginx/sites-available/whatsapp-ai-agents /etc/nginx/sites-enabled/

# Testar configuração do Nginx
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

### Configuração de SSL (Opcional mas Recomendado)

#### 1. Instalar Certbot
```bash
sudo apt install certbot python3-certbot-nginx -y
```

#### 2. Obter Certificado SSL
```bash
sudo certbot --nginx -d seu-dominio.com
```

### Monitoramento e Logs

#### 1. Visualizar Logs do Serviço
```bash
# Visualizar logs em tempo real
sudo journalctl -u whatsapp-ai-agents -f

# Visualizar logs dos últimos 100 registros
sudo journalctl -u whatsapp-ai-agents -n 100

# Visualizar logs de hoje
sudo journalctl -u whatsapp-ai-agents --since today
```

#### 2. Configurar Rotação de Logs
```bash
# Criar arquivo de configuração para rotação de logs
sudo nano /etc/logrotate.d/whatsapp-ai-agents
```

```bash
/opt/whatsapp-ai-agents/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload whatsapp-ai-agents
    endscript
}
```

### Backup e Recuperação

#### 1. Script de Backup
```bash
# Criar script de backup
sudo nano /opt/whatsapp-ai-agents/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/whatsapp-ai-agents"
mkdir -p $BACKUP_DIR

# Backup de configurações
cp /opt/whatsapp-ai-agents/src/config/.env $BACKUP_DIR/env_backup_$DATE

# Backup do banco de dados Redis (se necessário)
redis-cli BGSAVE
cp -r /var/lib/redis/dump.rdb $BACKUP_DIR/redis_backup_$DATE.rdb

echo "Backup realizado em $DATE"
```

```bash
# Tornar o script executável
chmod +x /opt/whatsapp-ai-agents/backup.sh

# Configurar cron para backups diários
echo "0 2 * * * /opt/whatsapp-ai-agents/backup.sh" | crontab -
```

### Troubleshooting

#### Problemas Comuns e Soluções

1. **Serviço não inicia**
   ```bash
   # Verificar logs detalhados
   sudo journalctl -u whatsapp-ai-agents --no-pager
   
   # Verificar permissões
   ls -la /opt/whatsapp-ai-agents/
   ```

2. **Erro de conexão com Redis**
   ```bash
   # Verificar se Redis está rodando
   sudo systemctl status redis-server
   
   # Testar conexão com Redis
   redis-cli ping
   ```

3. **Webhook não é recebido**
   ```bash
   # Verificar se porta 80/443 está acessível
   sudo ufw status
   
   # Testar conectividade
   curl -I http://seu-dominio.com/health
   ```

4. **Erro de autenticação na API da OpenAI**
   ```bash
   # Verificar variáveis de ambiente
   cat /opt/whatsapp-ai-agents/src/config/.env
   
   # Reiniciar serviço após alterações
   sudo systemctl restart whatsapp-ai-agents
   ```

5. **Erro de distutils (ModuleNotFoundError)**
   ```bash
   # Instalar pacotes necessários
   sudo apt install -y python3-distutils python3-setuptools
   
   # Recriar ambiente virtual
   cd /opt/whatsapp-ai-agents
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   pip install gunicorn
   
   # Reiniciar serviço
   sudo systemctl restart whatsapp-ai-agents
   ```

6. **Erro de importação do Twilio**
   ```bash
   # Instalar pacote Twilio
   source venv/bin/activate
   pip install twilio
   
   # Ou adicionar ao requirements.txt e reinstalar
   echo "twilio>=8.0.0" >> requirements.txt
   pip install -r requirements.txt
   
   # Reiniciar serviço
   sudo systemctl restart whatsapp-ai-agents
   ```

### Atualização da Aplicação

#### 1. Processo de Atualização
```bash
# Parar o serviço
sudo systemctl stop whatsapp-ai-agents

# Fazer backup do ambiente atual
sudo cp -r /opt/whatsapp-ai-agents /opt/whatsapp-ai-agents.backup.$(date +%Y%m%d)

# Atualizar código (se usando git)
cd /opt/whatsapp-ai-agents
git pull

# Atualizar dependências
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Reiniciar o serviço
sudo systemctl start whatsapp-ai-agents

# Verificar status
sudo systemctl status whatsapp-ai-agents
```

### Segurança Adicional

#### 1. Configurar Fail2Ban
```bash
# Instalar Fail2Ban
sudo apt install fail2ban -y

# Criar configuração específica
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true

[nginx-badbots]
enabled = true

[nginx-botsearch]
enabled = true
```

#### 2. Configurar usuários e permissões
```bash
# Criar usuário específico para a aplicação
sudo useradd -r -s /bin/false whatsapp-ai

# Definir permissões adequadas
sudo chown -R www-data:www-data /opt/whatsapp-ai-agents
```

### Verificação Final

#### 1. Testar Todos os Componentes
```bash
# Verificar se todos os serviços estão rodando
sudo systemctl status whatsapp-ai-agents
sudo systemctl status redis-server
sudo systemctl status nginx

# Testar endpoint de health check
curl http://localhost:5000/health

# Testar acesso via Nginx
curl http://seu-dominio.com/health
```

Com este guia completo, você poderá implantar com sucesso o sistema de agentes de IA para WhatsApp na sua VPS. O sistema estará configurado para produção com monitoramento, segurança e facilidade de manutenção.