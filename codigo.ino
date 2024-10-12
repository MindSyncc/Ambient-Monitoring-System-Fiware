#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"

// Definição dos pinos e tipo do sensor DHT
#define DHTPIN 4   // Pino conectado ao DHT22
#define DHTTYPE DHT22 // Tipo do sensor DHT
#define D4 2 // Pino do LED onboard

DHT dht(DHTPIN, DHTTYPE); // Instância do sensor DHT

// Configurações de Wi-Fi e MQTT
const char* SSID = "Wokwi-GUEST"; // Rede Wi-Fi
const char* PASSWORD = ""; // Senha do Wi-Fi
const char* BROKER_MQTT = "20.206.249.58"; // IP do Broker MQTT
const int BROKER_PORT = 1883; // Porta do Broker MQTT
// Tópicos MQTT
const char* TOPICO_SUBSCRIBE = "/TEF/lamp002/cmd"; 
const char* TOPICO_PUBLISH_1 = "/TEF/lamp002/attrs"; 
const char* TOPICO_PUBLISH_2 = "/TEF/lamp002/attrs/l"; 
const char* TOPICO_PUBLISH_3 = "/TEF/lamp002/attrs/t"; 
const char* TOPICO_PUBLISH_4 = "/TEF/lamp002/attrs/h"; 
const char* ID_MQTT = "fiware_002"; // ID do cliente MQTT

WiFiClient espClient;
PubSubClient MQTT(espClient);
char EstadoSaida = '0'; // Estado da saída do LED

void setup() {
    Serial.begin(115200); // Inicializa a comunicação serial
    pinMode(D4, OUTPUT); // Configura o pino do LED como saída
    dht.begin(); // Inicializa o sensor DHT
    connectToWiFi(); // Conecta ao Wi-Fi
    connectToMQTT(); // Conecta ao Broker MQTT
    delay(5000);
    MQTT.publish(TOPICO_PUBLISH_1, "s|on"); // Publica o estado inicial do LED
}

void loop() {
    checkConnections(); // Verifica se as conexões Wi-Fi e MQTT estão ativas
    sendOutputState(); // Envia o estado atual do LED
    handleLuminosity(); // Lê e envia os dados do sensor de luminosidade
    handleDHT(); // Lê e envia os dados do sensor DHT (temperatura e umidade)
    MQTT.loop(); // Mantém a comunicação MQTT ativa
}

void connectToWiFi() {
    Serial.println("------ Conectando ao Wi-Fi ------");
    WiFi.begin(SSID, PASSWORD); // Inicia a conexão Wi-Fi
    while (WiFi.status() != WL_CONNECTED) { // Aguarda até conectar
        delay(100);
        Serial.print(".");
    }
    Serial.println("\nConectado: " + String(WiFi.localIP())); // Exibe o IP do dispositivo
    digitalWrite(D4, LOW); // Garante que o LED inicie desligado
}

void connectToMQTT() {
    MQTT.setServer(BROKER_MQTT, BROKER_PORT); // Define o servidor MQTT
    MQTT.setCallback(mqttCallback); // Define a função de callback
    while (!MQTT.connected()) { // Tenta conectar ao Broker MQTT
        Serial.print("* Tentando conectar ao Broker MQTT: ");
        Serial.println(BROKER_MQTT);
        if (MQTT.connect(ID_MQTT)) { // Se conectar com sucesso
            Serial.println("Conectado ao broker MQTT!");
            MQTT.subscribe(TOPICO_SUBSCRIBE); // Inscreve-se no tópico
        } else { // Caso a conexão falhe
            Serial.print("Falha ao conectar, nova tentativa em 2s. Código de erro: ");
            Serial.println(MQTT.state());
            delay(2000);
        }
    }
}

void checkConnections() {
    // Re-conecta ao MQTT se desconectar
    if (!MQTT.connected()) {
        connectToMQTT();
    }
    // Re-conecta ao Wi-Fi se necessário
    if (WiFi.status() != WL_CONNECTED) {
        connectToWiFi();
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Converte a mensagem recebida em string
    String msg((char*)payload, length);
    Serial.print("- Mensagem recebida: ");
    Serial.println(msg);
    
    // Controle do LED de acordo com a mensagem recebida
    if (msg.equals(String("lamp002@on|"))) {
        digitalWrite(D4, HIGH); // Liga o LED
        EstadoSaida = '1'; // Atualiza o estado
    } else if (msg.equals(String("lamp002@off|"))) {
        digitalWrite(D4, LOW); // Desliga o LED
        EstadoSaida = '0'; // Atualiza o estado
    }
}

void sendOutputState() {
    // Publica o estado atual do LED (ligado/desligado)
    const char* estado = (EstadoSaida == '1') ? "s|on" : "s|off";
    MQTT.publish(TOPICO_PUBLISH_1, estado);
    Serial.println("Estado dos Leds: " + String(estado));
    delay(1000); // Aguarda 1 segundo
}

void handleLuminosity() {
    // Lê o valor do sensor de luminosidade (LDR)
    int luminosity = map(analogRead(34), 4095, 0, 0, 100); // Converte o valor para uma escala de 0 a 100
    Serial.print("Luminosidade: ");
    Serial.println(luminosity);
    MQTT.publish(TOPICO_PUBLISH_2, String(luminosity).c_str()); // Publica o valor de luminosidade
}

void handleDHT() {
    // Lê os valores de temperatura e umidade do sensor DHT
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    // Exibe os valores no monitor serial
    Serial.printf("Temperatura: %.1f°C, Umidade: %.1f%%\n", temperature, humidity);
    // Publica os valores no MQTT
    MQTT.publish(TOPICO_PUBLISH_3, String(temperature).c_str());
    MQTT.publish(TOPICO_PUBLISH_4, String(humidity).c_str());
}
