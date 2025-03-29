//Iker Valle Gallegos
//PROGRAMOS EL STA: - hay que hacer que busque REDS de la forma SOLAR_MAC
//                  - que guarde en memoria los datos .csv
//                  - que mida Temperatura y Luminosidad al recibir orden de AP

//PARA GUARDAR UN ARCHIVO EN MEMORIA (CARPETA DATOS): Ctr+Shift+P pico...

/*
En este programa se ha creado una STA que:
-busca REDS de la forma SOLAR_MAC (se conecta a la primera que ve)
-Se definen dos funciones que se pueden llamar para medir Temperatura y Funcion desde el AP
-Se define otra función medir() que devuelve un archivo guardado en memoria de la STA
*/

#include <WiFi.h>
//#include <SPIFFS.h>
//#include <ESPAsyncWebServer.h>
#include <WebServer.h>
#include <LittleFS.h>


const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int luz=4;
const int Vt[2]={5,6};
WebServer server(80);
bool a=true;

const String macaddress= WiFi.macAddress();

/**
Método que calcula la luminosidad
*/
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

/**
Método que envía al AP el valor de TEMPERATURA medido en forma de STRING
*/
void handletemp(){
  server.send(200,"text/plain",String(temp()));}

/**
Método que envía al AP el valor de LUMINOSIDAD medido en forma de STRING
*/
void handlelum(){
  server.send(200,"text/plain",String(luminosidad()));}

/**
Método que envía al AP los datos del archivo de memoria del ESP32
*/
void handlemedir(){
  
  File file = LittleFS.open("/Libro1.csv", "r");
    if (!file) {
        server.send(404, "text/plain", "Archivo no encontrado");
        return;
    }
    server.sendHeader("Content-Disposition", "attachment; filename=Libro1.csv");
    server.streamFile(file, "text/csv");
    file.close();
  
  
  ;}


void setup() {
  pinMode(luz,INPUT);
  pinMode(Vt[0],INPUT);
  pinMode(Vt[1],INPUT);
  for (int i=0; i<8; i++){pinMode(ledPins[i], OUTPUT);}
  Serial.begin(9600);

  WiFi.mode(WIFI_STA); //modo STA (en posteriores CAMBIAR)
  while(WiFi.status()!=WL_CONNECTED){buscar();}
 
  Serial.print("\n");
  Serial.println(WiFi.localIP()); //OBTENEMOS IP UTIL PARA EL SERVIDOR (del STA asignado por AP)  

  if (!LittleFS.begin(true)) {
        Serial.println("Error al montar LITTLEFS");
    }

  server.on("/temperatura",HTTP_GET,handletemp);
  server.on("/luminosidad",HTTP_GET,handlelum);
  server.on("/medir",HTTP_GET,handlemedir);
  server.begin();

  
}

void loop() {
  if(WiFi.status() != WL_CONNECTED) {
    buscar();
  }
  else{server.handleClient();} 
  
  delay(250);
}







/**
Método: escanea redes WIFI y se conecta al primero que empieza por SOLAR_...
      -Mientras está buscando los LEDs parpadean
      -Una vez está conectado los LEDS se quedan encendidos
*/
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


