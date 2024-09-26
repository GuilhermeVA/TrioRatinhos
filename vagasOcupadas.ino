const int trigPin1 = 12;
const int echoPin1 = 13;
const int trigPin2 = 2;
const int echoPin2 = 15;
const int trigPin3 = 18;
const int echoPin3 = 5;
long duration;
int distance;
long duration2;
int distance2;
long duration3;
int distance3;

void setup() {
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);
  pinMode(trigPin3, OUTPUT);
  pinMode(echoPin3, INPUT);
  
  // Inicializa a comunicação serial
  Serial.begin(115200);
}

void loop() {
  // Leitura do sensor 1
  digitalWrite(trigPin1, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin1, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin1, LOW);
  duration = pulseIn(echoPin1, HIGH);
  distance = duration * 0.034 / 2;

  // Leitura do sensor 2
  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);
  duration2 = pulseIn(echoPin2, HIGH);
  distance2 = duration2 * 0.034 / 2;

  // Leitura do sensor 3
  digitalWrite(trigPin3, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin3, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin3, LOW);
  duration3 = pulseIn(echoPin3, HIGH);
  distance3 = duration3 * 0.034 / 2;

  // Verifica se a vaga 1 está ocupada
  Serial.print("Vaga 1: ");
  if (distance < 10) {
    Serial.println("Ocupada");
  } else {
    Serial.println("Livre");
  }

  // Verifica se a vaga 2 está ocupada
  Serial.print("Vaga 2: ");
  if (distance2 < 10) {
    Serial.println("Ocupada");
  } else {
    Serial.println("Livre");
  }

  // Verifica se a vaga 3 está ocupada
  Serial.print("Vaga 3: ");
  if (distance3 < 10) {
    Serial.println("Ocupada");
  } else {
    Serial.println("Livre");
  }

  // Aguarda um pouco antes de repetir a leitura
  delay(5000);
}
