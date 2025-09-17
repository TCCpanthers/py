# Guia de Implantação - Sistema de Consulta Biométrica

Este guia fornece instruções detalhadas para implantar o sistema Python de consulta biométrica em ambiente de produção.

## 🚀 Pré-requisitos

### Sistema Operacional
- Ubuntu 20.04+ ou CentOS 7+
- Python 3.11+
- PostgreSQL 12+
- Acesso à porta serial (para sensor R307)

### Hardware
- Sensor biométrico R307
- Cabo USB-Serial ou interface serial
- Servidor/computador com porta USB disponível

## 📦 Instalação

### 1. Preparação do Ambiente

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Instalar PostgreSQL (se não estiver instalado)
sudo apt install postgresql postgresql-contrib -y

# Instalar dependências do sistema
sudo apt install build-essential libpq-dev -y
```

### 2. Configuração do Usuário

```bash
# Criar usuário para o sistema biométrico
sudo useradd -m -s /bin/bash biometric
sudo usermod -aG dialout biometric  # Acesso à porta serial

# Mudar para o usuário biométrico
sudo su - biometric
```

### 3. Instalação do Sistema

```bash
# Criar diretório de instalação
mkdir -p /home/biometric/biometric_system
cd /home/biometric/biometric_system

# Extrair arquivos do sistema (assumindo que você tem o ZIP)
unzip biometric_query_system.zip
cd biometric_query_system

# Criar ambiente virtual Python
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configuração do Banco de Dados

```bash
# Conectar ao PostgreSQL como superusuário
sudo -u postgres psql

-- Criar banco de dados
CREATE DATABASE biometric_access_system;

-- Criar usuário
CREATE USER biometric_user WITH PASSWORD 'sua_senha_segura';

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE biometric_access_system TO biometric_user;

-- Sair do PostgreSQL
\\q
```

### 5. Configuração do Sistema

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar configurações
nano .env
```

**Configurar o arquivo `.env`:**

```env
# Configuração do banco de dados
DATABASE_URL=postgresql://biometric_user:sua_senha_segura@localhost:5432/biometric_access_system

# Configuração do sensor
SENSOR_DEVICE=R307
SENSOR_PORT=/dev/ttyUSB0
SENSOR_BAUDRATE=57600

# Configuração de logs
LOG_LEVEL=INFO
LOG_FILE=/home/biometric/logs/biometric_query.log
```

### 6. Configuração de Logs

```bash
# Criar diretório de logs
mkdir -p /home/biometric/logs

# Configurar rotação de logs
sudo nano /etc/logrotate.d/biometric
```

**Conteúdo do arquivo de rotação:**

```
/home/biometric/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 biometric biometric
    postrotate
        systemctl reload biometric-query
    endscript
}
```

## 🔧 Configuração como Serviço

### 1. Criar Arquivo de Serviço

```bash
sudo nano /etc/systemd/system/biometric-query.service
```

**Conteúdo do arquivo de serviço:**

```ini
[Unit]
Description=Biometric Query Service
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=biometric
Group=biometric
WorkingDirectory=/home/biometric/biometric_system/biometric_query_system
Environment=PATH=/home/biometric/biometric_system/biometric_query_system/venv/bin
ExecStart=/home/biometric/biometric_system/biometric_query_system/venv/bin/python main.py --mode listener --unit ETEC01
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Configurações de segurança
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/biometric/logs /home/biometric/biometric_system

[Install]
WantedBy=multi-user.target
```

### 2. Ativar e Iniciar Serviço

```bash
# Recarregar configurações do systemd
sudo systemctl daemon-reload

# Ativar serviço para iniciar automaticamente
sudo systemctl enable biometric-query

# Iniciar serviço
sudo systemctl start biometric-query

# Verificar status
sudo systemctl status biometric-query
```

## 🔍 Monitoramento

### 1. Verificar Logs do Serviço

```bash
# Logs do systemd
sudo journalctl -u biometric-query -f

# Logs da aplicação
tail -f /home/biometric/logs/biometric_query.log

# Verificar últimas consultas
grep "Processing biometric query" /home/biometric/logs/biometric_query.log | tail -20
```

### 2. Script de Monitoramento

```bash
# Criar script de monitoramento
nano /home/biometric/monitor_biometric.sh
```

**Conteúdo do script:**

```bash
#!/bin/bash

LOG_FILE="/home/biometric/logs/biometric_query.log"
SERVICE_NAME="biometric-query"

# Verificar se o serviço está rodando
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): ERRO - Serviço $SERVICE_NAME não está rodando" >> $LOG_FILE
    systemctl restart $SERVICE_NAME
fi

# Verificar se há erros recentes nos logs
ERROR_COUNT=$(grep "ERROR" $LOG_FILE | grep "$(date +%Y-%m-%d)" | wc -l)
if [ $ERROR_COUNT -gt 10 ]; then
    echo "$(date): ALERTA - Muitos erros detectados hoje: $ERROR_COUNT" >> $LOG_FILE
fi

# Verificar espaço em disco
DISK_USAGE=$(df /home/biometric | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): ALERTA - Espaço em disco baixo: $DISK_USAGE%" >> $LOG_FILE
fi
```

```bash
# Tornar executável
chmod +x /home/biometric/monitor_biometric.sh

# Adicionar ao crontab
crontab -e
```

**Adicionar linha ao crontab:**

```
*/5 * * * * /home/biometric/monitor_biometric.sh
```

## 🔒 Configurações de Segurança

### 1. Firewall

```bash
# Configurar UFW (se usado)
sudo ufw allow from 192.168.1.0/24 to any port 5432  # PostgreSQL (apenas rede local)
sudo ufw deny 5432  # Negar acesso externo ao PostgreSQL
```

### 2. Permissões de Arquivos

```bash
# Definir permissões corretas
chmod 600 /home/biometric/biometric_system/biometric_query_system/.env
chmod 755 /home/biometric/biometric_system/biometric_query_system/*.py
chmod 644 /home/biometric/biometric_system/biometric_query_system/README.md
```

### 3. Backup Automático

```bash
# Criar script de backup
nano /home/biometric/backup_biometric.sh
```

**Conteúdo do script de backup:**

```bash
#!/bin/bash

BACKUP_DIR="/home/biometric/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
pg_dump -h localhost -U biometric_user biometric_access_system > $BACKUP_DIR/db_backup_$DATE.sql

# Backup dos logs
tar -czf $BACKUP_DIR/logs_backup_$DATE.tar.gz /home/biometric/logs/

# Backup da configuração
cp /home/biometric/biometric_system/biometric_query_system/.env $BACKUP_DIR/config_backup_$DATE.env

# Remover backups antigos (manter apenas 7 dias)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.env" -mtime +7 -delete

echo "$(date): Backup concluído" >> /home/biometric/logs/backup.log
```

```bash
# Tornar executável
chmod +x /home/biometric/backup_biometric.sh

# Adicionar ao crontab (backup diário às 2h)
crontab -e
```

**Adicionar ao crontab:**

```
0 2 * * * /home/biometric/backup_biometric.sh
```

## 🧪 Testes de Produção

### 1. Teste de Conectividade

```bash
# Testar conexão com banco
cd /home/biometric/biometric_system/biometric_query_system
source venv/bin/activate
python main.py --mode test-db
```

### 2. Teste de Simulação

```bash
# Executar simulação completa
python main.py --mode simulation --unit ETEC01
```

### 3. Teste de Consulta Individual

```bash
# Testar consulta específica
python main.py --mode query --template "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==" --finger index_right --unit ETEC01
```

## 📊 Configuração de Múltiplas Unidades

### Para múltiplas escolas/unidades:

```bash
# Criar configuração para cada unidade
cp .env .env.etec01
cp .env .env.fatec02

# Editar cada arquivo com código da unidade específica
nano .env.etec01  # Configurar UNIT_CODE=ETEC01
nano .env.fatec02  # Configurar UNIT_CODE=FATEC02

# Criar serviços separados
sudo cp /etc/systemd/system/biometric-query.service /etc/systemd/system/biometric-query-etec01.service
sudo cp /etc/systemd/system/biometric-query.service /etc/systemd/system/biometric-query-fatec02.service

# Editar cada serviço para usar a configuração correta
sudo nano /etc/systemd/system/biometric-query-etec01.service
# Alterar ExecStart para incluir --unit ETEC01

sudo nano /etc/systemd/system/biometric-query-fatec02.service
# Alterar ExecStart para incluir --unit FATEC02
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de Permissão na Porta Serial

```bash
# Verificar permissões
ls -l /dev/ttyUSB0

# Adicionar usuário ao grupo dialout
sudo usermod -aG dialout biometric

# Reiniciar sessão ou sistema
```

#### 2. Erro de Conexão com Banco

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão manual
psql -h localhost -U biometric_user -d biometric_access_system
```

#### 3. Serviço Não Inicia

```bash
# Verificar logs detalhados
sudo journalctl -u biometric-query -n 50

# Verificar configurações
sudo systemctl cat biometric-query

# Testar manualmente
sudo -u biometric /home/biometric/biometric_system/biometric_query_system/venv/bin/python /home/biometric/biometric_system/biometric_query_system/main.py --mode info
```

## 📈 Otimização de Performance

### 1. Configuração do PostgreSQL

```sql
-- Otimizações para consultas biométricas
CREATE INDEX idx_biometric_template ON "Biometric" USING hash (template);
CREATE INDEX idx_biometric_finger ON "Biometric" (finger);
CREATE INDEX idx_people_biometrics_person ON "PeopleBiometrics" (person_id);
CREATE INDEX idx_access_log_person_time ON "AccessLog" (person_id, access_time);
```

### 2. Configuração do Sistema

```bash
# Aumentar limites do sistema
echo "biometric soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "biometric hard nofile 65536" | sudo tee -a /etc/security/limits.conf
```

## 🔄 Atualizações

### Processo de Atualização

```bash
# 1. Parar serviço
sudo systemctl stop biometric-query

# 2. Backup da versão atual
cp -r /home/biometric/biometric_system /home/biometric/biometric_system_backup_$(date +%Y%m%d)

# 3. Atualizar código
cd /home/biometric/biometric_system/biometric_query_system
# Substituir arquivos pela nova versão

# 4. Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# 5. Testar nova versão
python main.py --mode test-db

# 6. Reiniciar serviço
sudo systemctl start biometric-query

# 7. Verificar funcionamento
sudo systemctl status biometric-query
```

---

**Desenvolvido por**: Arthur Roberto Weege Pontes  
**Versão**: 1.0.0  
**Data**: 2025-09-11  
**Ambiente**: Produção Linux/PostgreSQL

