///////////////////////////////////////////////////////////////
// Instituto de Tecnología Microelectrónica (TiM)
//////////////////////////////////////////////////////////////

// Iker Valle Gallegos
//***********************************
// Salidas digitales: LEDs
const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int inters[3]={9,10,11};


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i=0; i<8; i++){
    pinMode(ledPins[i],OUTPUT);
    digitalWrite(ledPins[i],LOW);
  }
  for (int i=0; i<3; i++){
    pinMode(inters[i],INPUT);
  }

}

void loop() {
  int pantalla;
  int a;
  int b;
  int c;
  /////////////////ENCENDER LEDS MEDIANTE PUERTO SERIE//////////////////////
  if (Serial.available()){
    pantalla=Serial.read();
  if (pantalla=='1'){
    for (int i=0;i<8;i++){
      digitalWrite(ledPins[i],1);}
  }
  if (pantalla=='2'){
     for (int i=0;i<8;i++){
      digitalWrite(ledPins[i],0);}
  }}
  //////////////////////////////////////////////////////////////////////////
  /////////////////NOTIFICAR INTERRUPTOR////////////////////////////////////
  a=digitalRead(inters[0]);
  b=digitalRead(inters[1]);
  c=digitalRead(inters[2]);
  if ((a==0)||(b==0)||(c==0)){
    Serial.println("Se ha pulsado un interruptor");
  }
  delay(100);
  //////////////////////////////////////////////////////////////////////////
  
}
