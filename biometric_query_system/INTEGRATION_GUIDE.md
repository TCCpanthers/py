# Guia de Integração com Sensor R307

Este guia explica como integrar o sistema Python de consulta biométrica com o sensor R307 e o sistema C++ existente.

## 🔌 Integração com Sistema C++

### 1. Protocolo de Comunicação

O sistema Python espera comandos no formato:
```
COMANDO:TEMPLATE_BASE64:TIPO_DEDO
```

**Exemplo de comando:**
```
QUERY:VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==:index_right
```

### 2. Código C++ para Integração

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>
#include <cstring>

class BiometricQueryInterface {
private:
    std::string pythonSystemPath;
    std::string unitCode;

public:
    BiometricQueryInterface(const std::string& path, const std::string& unit) 
        : pythonSystemPath(path), unitCode(unit) {}
    
    // Função para consultar biometria no sistema Python
    bool queryBiometric(const std::string& templateBase64, const std::string& finger) {
        // Construir comando para o sistema Python
        std::string command = "python " + pythonSystemPath + "/main.py --mode query";
        command += " --template \"" + templateBase64 + "\"";
        command += " --finger " + finger;
        command += " --unit " + unitCode;
        
        // Executar comando e capturar resultado
        FILE* pipe = popen(command.c_str(), "r");
        if (!pipe) {
            std::cerr << "Erro ao executar comando Python" << std::endl;
            return false;
        }
        
        char buffer[1024];
        std::string result;
        while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
            result += buffer;
        }
        pclose(pipe);
        
        // Verificar se o acesso foi liberado
        return result.find("Access granted: True") != std::string::npos;
    }
    
    // Função para enviar comando via serial (alternativa)
    bool queryBiometricSerial(const std::string& templateBase64, const std::string& finger) {
        // Construir comando serial
        std::string serialCommand = "QUERY:" + templateBase64 + ":" + finger;
        
        // Enviar comando via porta serial para o sistema Python
        // (implementar comunicação serial aqui)
        
        // Aguardar resposta "YES" ou "NO"
        std::string response = readSerialResponse();
        
        return response == "YES";
    }
    
private:
    std::string readSerialResponse() {
        // Implementar leitura da resposta serial
        // Retorna "YES" ou "NO"
        return "NO"; // Placeholder
    }
};

// Exemplo de uso
int main() {
    BiometricQueryInterface interface("/path/to/biometric_query_system", "ETEC01");
    
    // Template obtido do sensor R307
    std::string template64 = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==";
    std::string finger = "index_right";
    
    // Consultar biometria
    bool accessGranted = interface.queryBiometric(template64, finger);
    
    if (accessGranted) {
        std::cout << "Acesso liberado - Abrir catraca" << std::endl;
        // Código para abrir catraca
    } else {
        std::cout << "Acesso negado - Manter catraca fechada" << std::endl;
        // Código para manter catraca fechada
    }
    
    return 0;
}
```

### 3. Configuração do Sistema

#### 3.1 Configurar Variáveis de Ambiente

Criar arquivo `.env` no diretório do sistema Python:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/biometric_access_system
SENSOR_DEVICE=R307
SENSOR_PORT=/dev/ttyUSB0
SENSOR_BAUDRATE=57600
LOG_LEVEL=INFO
LOG_FILE=biometric_query.log
```

#### 3.2 Inicializar Sistema Python

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar conexão com banco
python main.py --mode test-db

# Iniciar modo listener (para comunicação serial)
python main.py --mode listener --unit ETEC01
```

## 🔄 Fluxos de Integração

### Fluxo 1: Integração via Linha de Comando

```
C++ → Executa comando Python → Recebe resultado → Controla catraca
```

**Vantagens:**
- Simples de implementar
- Não requer comunicação serial adicional
- Logs detalhados

**Desvantagens:**
- Overhead de inicialização do Python a cada consulta

### Fluxo 2: Integração via Comunicação Serial

```
C++ → Envia comando serial → Sistema Python → Resposta serial → C++
```

**Vantagens:**
- Sistema Python sempre ativo
- Resposta mais rápida
- Protocolo padronizado

**Desvantagens:**
- Requer configuração de porta serial adicional

### Fluxo 3: Integração via Socket/TCP

```cpp
// Exemplo de cliente TCP em C++
#include <sys/socket.h>
#include <arpa/inet.h>

class TCPBiometricClient {
private:
    int sock;
    struct sockaddr_in server;
    
public:
    bool connect(const std::string& host, int port) {
        sock = socket(AF_INET, SOCK_STREAM, 0);
        server.sin_addr.s_addr = inet_addr(host.c_str());
        server.sin_family = AF_INET;
        server.sin_port = htons(port);
        
        return ::connect(sock, (struct sockaddr*)&server, sizeof(server)) >= 0;
    }
    
    bool queryBiometric(const std::string& templateBase64, const std::string& finger) {
        std::string query = "QUERY:" + templateBase64 + ":" + finger + "\\n";
        send(sock, query.c_str(), query.length(), 0);
        
        char response[10];
        recv(sock, response, sizeof(response), 0);
        
        return std::string(response).find("YES") != std::string::npos;
    }
};
```

## 📋 Tipos de Dedos Suportados

```cpp
enum FingerType {
    THUMB_RIGHT = "thumb_right",
    INDEX_RIGHT = "index_right",
    MIDDLE_RIGHT = "middle_right",
    RING_RIGHT = "ring_right",
    PINKY_RIGHT = "pinky_right",
    THUMB_LEFT = "thumb_left",
    INDEX_LEFT = "index_left",
    MIDDLE_LEFT = "middle_left",
    RING_LEFT = "ring_left",
    PINKY_LEFT = "pinky_left"
};
```

## 🔧 Configuração do Sensor R307

### Parâmetros de Comunicação

```cpp
// Configurações do sensor R307
#define SENSOR_BAUDRATE 57600
#define SENSOR_PORT "/dev/ttyUSB0"
#define SENSOR_TIMEOUT 5000  // 5 segundos

// Comandos do sensor
#define CMD_GET_TEMPLATE 0x01
#define CMD_VERIFY_TEMPLATE 0x02
#define CMD_SEARCH_TEMPLATE 0x04
```

### Exemplo de Captura de Template

```cpp
std::string captureTemplate(int fingerId) {
    // 1. Capturar imagem do dedo
    if (!sensor.captureImage()) {
        return "";
    }
    
    // 2. Gerar template
    std::vector<uint8_t> templateData;
    if (!sensor.generateTemplate(templateData)) {
        return "";
    }
    
    // 3. Converter para base64
    return base64Encode(templateData);
}
```

## 🚨 Tratamento de Erros

### Códigos de Erro Comuns

```cpp
enum BiometricError {
    SUCCESS = 0,
    TEMPLATE_INVALID = 1,
    FINGER_INVALID = 2,
    DATABASE_ERROR = 3,
    SENSOR_ERROR = 4,
    COMMUNICATION_ERROR = 5
};

std::string getErrorMessage(BiometricError error) {
    switch (error) {
        case TEMPLATE_INVALID:
            return "Template biométrico inválido";
        case FINGER_INVALID:
            return "Tipo de dedo inválido";
        case DATABASE_ERROR:
            return "Erro de conexão com banco de dados";
        case SENSOR_ERROR:
            return "Erro de comunicação com sensor";
        case COMMUNICATION_ERROR:
            return "Erro de comunicação com sistema Python";
        default:
            return "Erro desconhecido";
    }
}
```

## 📊 Monitoramento e Logs

### Verificar Logs do Sistema Python

```bash
# Ver logs em tempo real
tail -f biometric_query.log

# Verificar últimas consultas
grep "Processing biometric query" biometric_query.log | tail -10

# Verificar erros
grep "ERROR" biometric_query.log
```

### Logs no Sistema C++

```cpp
void logBiometricQuery(const std::string& template64, const std::string& finger, bool result) {
    std::ofstream logFile("biometric_cpp.log", std::ios::app);
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    
    logFile << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
    logFile << " - Finger: " << finger;
    logFile << " - Template: " << template64.substr(0, 20) << "...";
    logFile << " - Result: " << (result ? "GRANTED" : "DENIED") << std::endl;
}
```

## 🔒 Segurança

### Validações Importantes

1. **Validar template antes de enviar:**
```cpp
bool isValidTemplate(const std::string& template64) {
    // Verificar se é base64 válido
    // Verificar tamanho mínimo/máximo
    // Verificar formato do template
    return true; // Implementar validação
}
```

2. **Timeout para consultas:**
```cpp
bool queryWithTimeout(const std::string& template64, const std::string& finger, int timeoutMs) {
    auto start = std::chrono::steady_clock::now();
    
    // Executar consulta
    bool result = queryBiometric(template64, finger);
    
    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    if (duration.count() > timeoutMs) {
        std::cerr << "Timeout na consulta biométrica" << std::endl;
        return false;
    }
    
    return result;
}
```

## 🧪 Testes de Integração

### Script de Teste C++

```cpp
void runIntegrationTests() {
    BiometricQueryInterface interface("/path/to/biometric_query_system", "ETEC01");
    
    // Teste 1: Template válido
    assert(interface.queryBiometric("VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==", "index_right") == true);
    
    // Teste 2: Template inválido
    assert(interface.queryBiometric("SW52YWxpZCB0ZW1wbGF0ZQ==", "index_right") == false);
    
    // Teste 3: Dedo inválido
    assert(interface.queryBiometric("VGVzdA==", "invalid_finger") == false);
    
    std::cout << "Todos os testes de integração passaram!" << std::endl;
}
```

---

**Desenvolvido por**: Arthur Roberto Weege Pontes  
**Versão**: 1.0.0  
**Data**: 2025-09-11  
**Compatível com**: Sensor R307, Sistema C++, PostgreSQL

