const int trigPin = 12;
const int echoPin = 13;
const int buzzerPin = 8;  // Pino do buzzer
long duration;
int distance;
const int pinRed = 2;
const int pinGreen = 3;
const int pinBlue = 4;

void setup() {
  // Configura as portas como saídas
  pinMode(pinRed, OUTPUT);
  pinMode(pinGreen, OUTPUT);
  pinMode(pinBlue, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  // Inicializa a comunicação serial
  Serial.begin(9600);
}

void loop() {
  // Limpa o pino trig
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Envia um pulso de 10 microsegundos no pino trig
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Lê a duração do pulso no pino echo
  duration = pulseIn(echoPin, HIGH);

  // Calcula a distância em centímetros
  distance = duration * 0.034 / 2;

  // Exibe a distância no monitor serial
  Serial.print("Distancia: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance < 10) {
    // Menos de 10 cm: LED vermelho e buzzer rápido
    digitalWrite(pinRed, LOW);    // Vermelho ligado
    digitalWrite(pinGreen, HIGH); // Verde desligado
    digitalWrite(pinBlue, HIGH);  // Azul desligado
    tone(buzzerPin, 1000);        // Ativa o buzzer com 1000 Hz
  } 
  else if (distance < 20) {
    // Entre 10 e 20 cm: LED amarelo (vermelho + verde) e buzzer moderado
    digitalWrite(pinRed, LOW);    // Vermelho ligado
    digitalWrite(pinGreen, LOW);  // Verde ligado
    digitalWrite(pinBlue, HIGH);  // Azul desligado
    tone(buzzerPin, 500);         // Ativa o buzzer com 500 Hz
  } 
  else if (distance < 30) {
    // Entre 20 e 30 cm: LED verde e buzzer lento
    digitalWrite(pinRed, HIGH);   // Vermelho desligado
    digitalWrite(pinGreen, LOW);  // Verde ligado
    digitalWrite(pinBlue, HIGH);  // Azul desligado
    tone(buzzerPin, 250);         // Ativa o buzzer com 250 Hz
  } 
  else {
    // Maior que 30 cm: Desliga tudo
    digitalWrite(pinRed, HIGH);   // Vermelho desligado
    digitalWrite(pinGreen, HIGH); // Verde desligado
    digitalWrite(pinBlue, LOW);  // Azul desligado
    noTone(buzzerPin);            // Desativa o buzzer
  }

  // Aguarda um pouco antes de repetir a leitura
  delay(200);
}
