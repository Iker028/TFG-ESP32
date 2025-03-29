///////////////////////////////////////////////////////////////
// Instituto de Tecnología Microelectrónica (TiM)
//////////////////////////////////////////////////////////////

//***********************************
// Salidas digitales: LEDs
const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int inters[3]={9,10,11};
int control;
//***********************************

void setup() {
  Serial.begin(9600);
  // Inicio LEDs
  for (int i=0; i<8; i++)
  {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], (i & 1));
    //digitalWrite(ledPins[i], 1);
  }
  pinMode(inters[1],INPUT);
  control=0;
}

void loop() {
  //Serial.println(digitalRead(inters[1]));
  if (digitalRead(inters[1])==LOW){
    if (control==0){
      for (int i=0; i<8; i++){
      digitalWrite(ledPins[i],(i & 1));
      control=1;
      }
    }
    for (int i=0; i<8; i++)
  {
    // LEDs intermitentes
      digitalWrite(ledPins[i], !digitalRead(ledPins[i]));
  }
  delay (1000);}
  else {
      for (int i=0; i<8; i++)
  {
    // LEDs intermitentes
    digitalWrite(ledPins[i], LOW);
  }
   control=0; 
  }
  }
