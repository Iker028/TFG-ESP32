#include <LittleFS.h>
#include <WiFi.h>
#include <HTTPClient.h>

const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int luz=4;
const int Vt[2]={5,6};
bool a=true;
const String IP="192.168.4.1";
int httpCode=0;

const int string =1;
const int modulo=1;


float luminosidad(){
  float vluz=analogRead(luz);
  float Iph=vluz/6.8;
  float L=pow(10.0,log10(Iph)/1.3059)*2535.12;
  return L;
}

/**
Método que calcula la temperatura
*/
float temp(){
  float Vp=analogRead(Vt[0]);
  float Vn=analogRead(Vt[1]);
  float deltaV=-(Vp-Vn)*pow(10.0,-3.0);
  float rt=100.0*(0.5-(deltaV/3.3))/(0.5+(deltaV/3.3));
  float T=(1.0/(298.0)+(1.0/(4550))*log(rt/100.0));
  T=(1.0/T)-273.0;
  return T;
}

void setup() {
  Serial.begin(9600);
  pinMode(Vt[0],INPUT);
  pinMode(Vt[1],INPUT);
  pinMode(luz,INPUT);
  for (int i=0; i<8; i++){pinMode(ledPins[i], OUTPUT);}
  if (!LittleFS.begin(true)) {
      Serial.println("Error al montar LITTLEFS");}
  while(WiFi.status()!=WL_CONNECTED){buscar();}

}

void loop() {
  if(WiFi.status() != WL_CONNECTED) {
    buscar();
  }
  else{
    String macSTA=WiFi.macAddress();
    HTTPClient http;
    String url= "http://"+IP+"/postable";
    http.begin(url);
    httpCode=http.GET();
    if(httpCode==200){
      String payload=http.getString();
      if(payload!=""){
        int index=payload.indexOf('/');
        String MAC=payload.substring(0, index);
        String comando= payload.substring(index+1);
        if(MAC==macSTA){
          http.end();
          HTTPClient httpPost;
          httpPost.begin("http://"+IP+"/post");
          httpPost.addHeader("Content-Type", "text/plain");
          int responsecode=0;
          float temperatura;
          float lum;
          switch(getCommandCode(comando)){
            case 1:
              temperatura=temp();
              responsecode=httpPost.POST(String(temperatura));
              break;
            case 2:
              lum=luminosidad();
              responsecode=httpPost.POST(String(lum));
              break;
            case 3:
              File file = LittleFS.open("/Libro1.csv", "r");
              if (!file) {
                httpPost.POST("Error: no se ha encontrado archivo en memoria SPIFFS");
              }
              else{
              String fileContent = "";
              while (file.available()) {
                fileContent += (char)file.read();
              }
              responsecode=httpPost.POST(fileContent);
              }
              file.close();
              break;
            case 4:
              responsecode=httpPost.POST(String(modulo)+","+String(string));break;}
          httpPost.end();
          }
        }
      }
      http.end();
    }
  }




//función que busca redes WIFI que empiecen por SOLAR y se conecta a la primera que encuentra
void buscar(){
  WiFi.disconnect();   //limpia los settings wifi anteriores
  int numNetworks = WiFi.scanNetworks(); //escaneo las redes posibles

  String targetSSID = ""; 
  
  for (int i = 0; i < numNetworks; i++){
    String ssid = WiFi.SSID(i);
    if(ssid.startsWith("SOLAR_")){
      targetSSID=ssid;
      WiFi.begin(targetSSID.c_str());
      break;
    ;}}

  //ESPERAMOS A QUE SE CONECTE
  int intento=0;
  while(WiFi.status()!=WL_CONNECTED && intento<20){
    if(a){
      for (int led:ledPins){
        digitalWrite(led,LOW)
        ;}}
    else{for(int led:ledPins){digitalWrite(led,HIGH);}}
    a=!a;
    intento++;
    delay(500);}
  if(WiFi.status()==WL_CONNECTED){
    for(int led:ledPins){digitalWrite(led,LOW);}
  }
  else{for(int led:ledPins){digitalWrite(led,HIGH);}}
  //WiFi.scanDelete();//libera espacio de memoria de num devices (no se si esto afecta al AP)
  }

int getCommandCode(String cmd) {
    if (cmd == "temperatura") return 1;
    if (cmd == "luminosidad") return 2;
    if (cmd == "IV") return 3;
    if (cmd == "getij") return 4;
    return -1;  // Default case
}


