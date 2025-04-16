//Iker Valle Gallegos

//Vamos a crear un AP que actue como servidor

#include <LittleFS.h>
#include <WiFi.h> 
#include <WebServer.h>
#include <esp_wifi.h>

const int ledPins[8] = {42,41,40,39,38,37,36,35};
bool a=true;
WebServer server(80);
String command;


void setup() {
  Serial.begin(9600);
  for (int i=0; i<8; i++)
  {pinMode(ledPins[i], OUTPUT);}
  for(int led:ledPins){digitalWrite(led,HIGH);}
  WiFi.mode(WIFI_MODE_AP);
  delay(1000);
  String MAC=WiFi.softAPmacAddress();
  MAC.replace(":","");
  String ssid="SOLAR_"+MAC;
  WiFi.softAP(ssid.c_str());
  Serial.printf("IP de AP: %s",WiFi.softAPIP().toString());
  if (!LittleFS.begin(true)) {
        Serial.println("Error al montar LITTLEFS");
    }
  server.on("/postable", HTTP_GET, handlepostable);
  server.on("/post", HTTP_POST, handlePost);

  server.begin();
}

void loop(){
  server.handleClient();
  if(WiFi.softAPgetStationNum()>0){
    for(int led:ledPins){digitalWrite(led,LOW);}
    if(Serial.available()){
      command=Serial.readStringUntil('\n');
      if(command=="macs"){
       get_connectedev();
      }
    }
    else{}
   
}
else{for(int led:ledPins){digitalWrite(led,HIGH);}}
}

void handlePost(){
  if (server.hasArg("plain")){
    String data= server.arg("plain");
    Serial.println(data,12);
    server.send(200, "text/plain", "POST recibido");
    command="";
  }
}
void handlepostable(){
    //command=Serial.readStringUntil('\n');
    server.send(200,"text/plain",command);
}

void get_connectedev(){
    wifi_sta_list_t stationList;
    if (esp_wifi_ap_get_sta_list(&stationList) == ESP_OK) {
        for (int i = 0; i < stationList.num; i++) {
            Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X\n",
                          stationList.sta[i].mac[0], stationList.sta[i].mac[1], stationList.sta[i].mac[2],
                          stationList.sta[i].mac[3], stationList.sta[i].mac[4], stationList.sta[i].mac[5]);
        }
    } else {
        Serial.println("Error obteniendo la lista de dispositivos conectados.");
    }
}
