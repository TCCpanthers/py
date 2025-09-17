# Sistema de Consulta Biométrica Python

Sistema Python para consulta de biometria integrado ao sistema de controle de acesso escolar. Desenvolvido para trabalhar em conjunto com o sensor biométrico R307 e o sistema TypeScript existente.

## 📋 Visão Geral

Este sistema foi desenvolvido para complementar o sistema de controle biométrico escolar existente, fornecendo:

- **Consulta de biometria**: Verifica se uma biometria existe no banco de dados
- **Integração com sensor R307**: Comunicação serial com o sensor biométrico
- **Resposta em tempo real**: Retorna SIM/NÃO para o sensor para controle de catraca
- **Log de acessos**: Registra todas as tentativas de acesso no banco de dados
- **Modo de simulação**: Permite testes sem hardware físico

## 🏗️ Arquitetura

```
biometric_query_system/
├── config.py              # Configurações do sistema
├── database.py             # Gerenciador de banco de dados
├── biometric_service.py    # Serviço principal de consulta biométrica
├── sensor_interface.py     # Interface com sensor R307
├── main.py                 # Ponto de entrada principal
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
└── README.md              # Esta documentação
```

## 🚀 Instalação

### 1. Pré-requisitos

- Python 3.11+
- PostgreSQL (mesmo banco do sistema TypeScript)
- Sensor R307 (para modo produção)
- Porta serial disponível (para comunicação com sensor)

### 2. Instalação das dependências

```bash
pip install -r requirements.txt
```

### 3. Configuração do ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
# Configuração do banco de dados (mesmo do sistema TypeScript)
DATABASE_URL=postgresql://username:password@localhost:5432/biometric_access_system

# Configuração do sensor
SENSOR_DEVICE=R307
SENSOR_PORT=/dev/ttyUSB0
SENSOR_BAUDRATE=57600

# Configuração de logs
LOG_LEVEL=INFO
LOG_FILE=biometric_query.log
```

## 🎯 Modos de Operação

### 1. Modo Listener (Produção)

Para uso com sensor R307 real:

```bash
python main.py --mode listener --unit ETEC01
```

### 2. Modo Simulação (Testes)

Para testes sem hardware físico:

```bash
python main.py --mode simulation --unit ETEC01
```

### 3. Consulta Única (Debug)

Para testar uma consulta específica:

```bash
python main.py --mode query --template "VGVzdCBiaW9tZXRyaWMgZGF0YQ==" --finger index_right --unit ETEC01
```

### 4. Teste de Conexão

Para verificar conectividade com o banco:

```bash
python main.py --mode test-db
```

### 5. Informações do Sistema

Para ver configurações atuais:

```bash
python main.py --mode info
```

## 🔧 Integração com Sensor R307

### Protocolo de Comunicação

O sistema espera comandos do sensor no formato:

```
COMANDO:TEMPLATE_BASE64:TIPO_DEDO
```

Exemplo:
```
QUERY:VGVzdCBiaW9tZXRyaWMgZGF0YQ==:index_right
```

### Resposta para o Sensor

O sistema responde com:
- `YES` - Acesso liberado (biometria encontrada)
- `NO` - Acesso negado (biometria não encontrada ou erro)

### Tipos de Dedos Suportados

- `thumb_right`, `thumb_left`
- `index_right`, `index_left`
- `middle_right`, `middle_left`
- `ring_right`, `ring_left`
- `pinky_right`, `pinky_left`

## 📊 Estrutura do Banco de Dados

O sistema utiliza as mesmas tabelas do sistema TypeScript:

- **Biometric**: Armazena templates biométricos
- **Person**: Informações das pessoas cadastradas
- **PeopleBiometrics**: Relaciona pessoas com suas biometrias
- **AccessLog**: Log de tentativas de acesso
- **Unit**: Unidades escolares

## 🧪 Testes e Simulação

### Executar Simulação Completa

```bash
python main.py --mode simulation --unit ETEC01
```

### Testar Conexão com Banco

```bash
python main.py --mode test-db
```

### Logs Detalhados

```bash
python main.py --mode simulation --unit ETEC01 --verbose
```

## 🔍 Exemplo de Uso

### 1. Inicializar o sistema

```python
from biometric_service import BiometricQueryService

# Inicializar serviço para unidade ETEC01
service = BiometricQueryService("ETEC01")

# Testar conexão
if service.test_database_connection():
    print("✅ Sistema pronto!")
```

### 2. Processar consulta biométrica

```python
# Template em base64 (recebido do sensor)
template = "VGVzdCBiaW9tZXRyaWMgZGF0YQ=="
finger = "index_right"

# Processar consulta
result = service.process_biometric_query(template, finger)

# Verificar resultado
if result['access_granted']:
    print(f"✅ Acesso liberado para: {result['person']['name']}")
else:
    print("❌ Acesso negado")
```

### 3. Integração com sensor

```python
from sensor_interface import SensorInterface

# Inicializar interface
interface = SensorInterface("ETEC01", "/dev/ttyUSB0")

# Conectar ao sensor
if interface.connect_sensor():
    # Iniciar escuta de comandos
    interface.listen_for_commands()
```

## 📝 Logs e Monitoramento

### Níveis de Log

- `DEBUG`: Informações detalhadas para desenvolvimento
- `INFO`: Informações gerais de operação
- `WARNING`: Avisos sobre situações anômalas
- `ERROR`: Erros que impedem operação normal

### Exemplo de Log

```
2025-09-11 10:30:15 - biometric_service - INFO - Processing biometric query for finger: index_right
2025-09-11 10:30:15 - database - INFO - Biometric match found for person: João Silva (CPF: 123.456.789-00)
2025-09-11 10:30:15 - biometric_service - INFO - Access GRANTED for João Silva (CPF: 123.456.789-00)
2025-09-11 10:30:15 - sensor_interface - INFO - Response sent to sensor: YES
```

## 🔒 Segurança

### Medidas Implementadas

- **Validação de entrada**: Todos os dados são validados antes do processamento
- **Log de auditoria**: Todas as tentativas de acesso são registradas
- **Tratamento de erros**: Erros são capturados e logados sem expor informações sensíveis
- **Conexão segura**: Uso de conexões parametrizadas para evitar SQL injection

### Dados Sensíveis

- Templates biométricos são armazenados como dados binários
- CPFs e informações pessoais são protegidos por validação de acesso
- Logs não expõem templates biométricos completos

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Erro de conexão com banco de dados

```
❌ Database connection failed
```

**Solução**: Verificar `DATABASE_URL` no arquivo `.env`

#### 2. Sensor não conecta

```
❌ Failed to connect to R307 sensor
```

**Soluções**:
- Verificar se a porta serial está correta
- Verificar permissões de acesso à porta (`sudo chmod 666 /dev/ttyUSB0`)
- Verificar se o sensor está conectado e ligado

#### 3. Template inválido

```
❌ Invalid base64 template format
```

**Solução**: Verificar se o template está em formato base64 válido

### Debug Avançado

Para debug detalhado:

```bash
python main.py --mode simulation --unit ETEC01 --verbose
```

## 🤝 Integração com Sistema TypeScript

Este sistema Python complementa o sistema TypeScript existente:

- **TypeScript**: Cadastro de biometrias (CreateBiometricService)
- **Python**: Consulta de biometrias (BiometricQueryService)
- **Banco compartilhado**: Ambos usam o mesmo PostgreSQL
- **Sensor R307**: Comunica com ambos os sistemas

### Fluxo de Dados

1. **Cadastro** (TypeScript):
   - Sensor → Sistema TypeScript → Banco de dados

2. **Consulta** (Python):
   - Sensor → Sistema Python → Banco de dados → Resposta para sensor

## 📞 Suporte

Para dúvidas ou problemas:

1. Verificar logs do sistema
2. Executar modo de simulação para testes
3. Verificar configurações no arquivo `.env`
4. Consultar esta documentação

---

**Desenvolvido por**: Arthur Roberto Weege Pontes  
**Versão**: 1.0.0  
**Data**: 2025-09-11  
**Compatível com**: Sistema de Controle Biométrico Escolar TypeScript

