void Vermelho() {
  digitalWrite(vermelho, HIGH);//Coloca vermelho em nível alto, ligando-o
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(vermelho, LOW);//Coloca vermelho em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
void Verde() {
  digitalWrite(verde, HIGH);//Coloca verde em nível alto
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(verde, LOW);//Coloca verde em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
void Azul() {
  digitalWrite(azul, HIGH);//Coloca azul em nível alto
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(azul, LOW);//Coloca azul em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
void Branco() {
  digitalWrite(azul, HIGH);//Coloca azul em nível alto
  digitalWrite(vermelho, HIGH);//Coloca vermelho em nível alto
  digitalWrite(verde, HIGH);//Coloca verde em nível alto, ligando-o
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(azul, LOW);//Coloca azul em nível baixo
  digitalWrite(vermelho, LOW);//Coloca vermelho em nível baixo
  digitalWrite(verde, LOW);//Coloca verde em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
void Magenta() {
  digitalWrite(azul, HIGH);//Coloca azul em nível alto
  digitalWrite(vermelho, HIGH);//Coloca vermelho em nível alto
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(azul, LOW);//Coloca azul em nível baixo
  digitalWrite(vermelho, LOW);//Coloca vermelho em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
void Amarelo() {
  digitalWrite(verde, HIGH);//Coloca verde em nível alto
  digitalWrite(vermelho, HIGH);//Coloca vermelho em nível alto
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(verde, LOW);//Coloca verde em nível baixo
  digitalWrite(vermelho, LOW);//Coloca vermelho em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
void Ciano() {
  digitalWrite(verde, HIGH);//Coloca verde em nível alto
  digitalWrite(azul, HIGH);//Coloca azul em nível baixo alto
  delay(1000);//Intervalo de 1 segundo
  digitalWrite(verde, LOW);//Coloca verde em nível baixo
  digitalWrite(azul, LOW);//Coloca azul  em nível baixo
  delay(1000);//Intervalo de 1 segundo
}
