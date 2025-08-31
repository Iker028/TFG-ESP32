#include <LittleFS.h>

//Iker Valle Gallegos

//Programa para wifi: queremos que una sea AP(access point) y la otra sea STA (station)
//CREAMOS EL AP: detectaremos si hay o no algo conectado mediante los LEDS
#include <WiFi.h> //IMPORTAMOS LIBRERIA WIFI
#include <HTTPClient.h>
#include <WiFiServer.h>
#include <WiFiClient.h>
const int ledPins[8] = {42,41,40,39,38,37,36,35};
const char* sta_ip = "192.168.4.2";
bool a=true;
WiFiServer server(80); 



void setup() {
  Serial.begin(9600);
  for (int i=0; i<8; i++)
  {pinMode(ledPins[i], OUTPUT);}

  WiFi.mode(WIFI_MODE_AP);
  delay(1000);
  String MAC=WiFi.softAPmacAddress();
  MAC.replace(":","");
  String ssid="SOLAR_"+MAC;
  WiFi.softAP(ssid.c_str());
  if (!LittleFS.begin(true)) {
        Serial.println("Error al montar LITTLEFS");
    }

}

void loop() {
  // put your main code here, to run repeatedly:
  if(WiFi.softAPgetStationNum()>0){
    if(a){for(int led:ledPins){digitalWrite(led,LOW);}a=false;}
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.toLowerCase();
        //Serial.println("Mandando la instrucción: " + command);

        HTTPClient http;
        String url = "http://" + String(sta_ip) + "/" + command;
        http.begin(url);
        //Serial.println(url);
        int httpCode = http.GET();
        
        if (httpCode > 0) {
          if (command=="medir"){
            WiFiClient stream = http.getStream();
            byte buffer[128];  // Buffer to hold incoming data
            // Read the stream in chunks
            while (stream.available()) {
              int len = stream.read(buffer, sizeof(buffer));
              Serial.write(buffer, len);}
        
              ;}
          else{
            Serial.println(http.getString());}
        } else {
            Serial.println("HTTP Request Failed.");
        }

        
        http.end();
    }}
  else{for(int led:ledPins){digitalWrite(led,led&1);}
      a=true;}

}
