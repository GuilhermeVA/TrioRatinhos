const int trigPin = 12;
const int echoPin = 13;
const int buzzerPin = 8;  // Pino do buzzer
long duration;
int distance;

void setup() {
  // Define os pinos como entrada e saída
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

    for (int i = 0; i < 8; i++) { 
      digitalWrite(buzzerPin, HIGH);  // Ativa o buzzer
      delay(50);                     // Aguarda 100ms
      digitalWrite(buzzerPin, LOW);   // Desativa o buzzer
      delay(100);                     // Aguarda 100ms
    }
  } else {
    digitalWrite(buzzerPin, LOW);   // Desativa o buzzer se a distância for maior que 20 cm
  }
   
  if (distance < 20) {

    for (int i = 0; i < 5; i++) { 
      digitalWrite(buzzerPin, HIGH);  // Ativa o buzzer
      delay(100);                     // Aguarda 100ms
      digitalWrite(buzzerPin, LOW);   // Desativa o buzzer
      delay(100);                     // Aguarda 100ms
    }
  } else {
    digitalWrite(buzzerPin, LOW);   // Desativa o buzzer se a distância for maior que 20 cm
  } 
  if (distance < 30) {

    for (int i = 0; i < 2; i++) { 
      digitalWrite(buzzerPin, HIGH);  // Ativa o buzzer
      delay(100);                     // Aguarda 100ms
      digitalWrite(buzzerPin, LOW);   // Desativa o buzzer
      delay(100);                     // Aguarda 100ms
    }
  } else {
    digitalWrite(buzzerPin, LOW);   // Desativa o buzzer se a distância for maior que 20 cm
  }

  // Aguarda um pouco antes de repetir a leitura
  delay(300);
}
