///////////////////////////////////////////////////////////////
// Instituto de Tecnología Microelectrónica (TiM)
//////////////////////////////////////////////////////////////

// Iker Valle Gallegos
//***********************************
// Salidas digitales: LEDs
const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int inters[3]={9,10,11};
const int luz=4;
const int Vt[2]={5,6};

float vluz,Vp,Vn,Iph,L,deltaV,T,rt;
int pantalla;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  for (int i=0; i<8; i++){
    pinMode(ledPins[i],OUTPUT);
    digitalWrite(ledPins[i],HIGH);
  }
  for (int i=0; i<3; i++){
    pinMode(inters[i],INPUT);
  }
 pinMode(luz,INPUT);
 pinMode(Vt[0],INPUT);
 pinMode(Vt[1],INPUT);
}


void loop() {
  vluz=analogRead(luz);
  Vp=analogRead(Vt[0]);
  Vn=analogRead(Vt[1]);
  //Medimos mediante puerto serie
  if (Serial.available()){
    pantalla=Serial.read();
  if (pantalla=='1'){
    Iph=vluz/6.8;
    L=pow(10.0,log10(Iph)/1.3059)*2535.12;
    Serial.println(L);
  }
  if (pantalla=='2'){
    deltaV=-(Vp-Vn)*pow(10.0,-3.0);
    rt=100.0*(0.5-(deltaV/3.3))/(0.5+(deltaV/3.3));
    T=(1.0/(298.0)+(1.0/(4550))*log(rt/100.0));
    T=(1.0/T)-273.0;
    Serial.println(T,2);
  }
}}


