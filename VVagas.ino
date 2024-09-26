#include <WiFi.h>
#include <PubSubClient.h>

// Definições de pinos do HC-SR04
#define TRIG_PIN1 12
#define ECHO_PIN1 13
#define TRIG_PIN2 2
#define ECHO_PIN2 15
#define TRIG_PIN3 18
#define ECHO_PIN3 5

// Credenciais do Wi-Fi
const char* ssid = "Trio Rats";
const char* password = "rigelrats";

// Configuração do broker MQTT
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "estacionamento/vagas";

// Variáveis para o MQTT
WiFiClient espClient;
PubSubClient client(espClient);

long duration1, duration2, duration3;
float distance1, distance2, distance3;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando-se a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conectar ao MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("Conectado ao broker MQTT");
    } else {
      Serial.print("Falha ao conectar, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(2000);
    }
  }
}



void setup() {
  Serial.begin(9600);

  // Configurar os pinos dos sensores
  pinMode(TRIG_PIN1, OUTPUT);
  pinMode(ECHO_PIN1, INPUT);
  pinMode(TRIG_PIN2, OUTPUT);
  pinMode(ECHO_PIN2, INPUT);
  pinMode(TRIG_PIN3, OUTPUT);
  pinMode(ECHO_PIN3, INPUT);

  // Conectar ao Wi-Fi
  setup_wifi();

  // Configurar o cliente MQTT
  client.setServer(mqtt_server, mqtt_port);
}

void verificar_vaga(int trigPin, int echoPin, const char* vaga) {
  // Medição do sensor ultrassônico
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = duration * 0.034 / 2; // Distância em cm

  String statusVaga;

  if (distance < 10) {
    statusVaga = String(vaga) + ": Ocupada";
  } else {
    statusVaga = String(vaga) + ": Livre";
  }

  // Exibe o status da vaga no monitor serial
  Serial.println(statusVaga);

  // Publicar o status da vaga no tópico MQTT
  bool sucesso = client.publish(mqtt_topic, statusVaga.c_str());
  if (sucesso) {
    Serial.println("Mensagem publicada com sucesso no MQTT");
  } else {
    Serial.println("Falha ao publicar mensagem no MQTT");
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, tentando reconectar...");
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }else{
  client.loop();
  }
  // Verificar o estado de cada vaga
  verificar_vaga(TRIG_PIN1, ECHO_PIN1, "Vaga 1");
  verificar_vaga(TRIG_PIN2, ECHO_PIN2, "Vaga 2");
  verificar_vaga(TRIG_PIN3, ECHO_PIN3, "Vaga 3");

  delay(10000);
}
