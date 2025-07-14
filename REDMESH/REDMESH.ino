
#include "painlessMesh.h"

#define   MESH_PREFIX     "RED_MESH_SOLAR"
#define   MESH_PASSWORD   "solar1234"
#define   MESH_PORT       5555

Scheduler userScheduler; // to control your personal task
painlessMesh  mesh;
String letra="E";

void receivedCallback(uint32_t from, String &msg){
  if(msg.startsWith("LETRA")){
    String respuesta="RLETRA: "+letra;
    mesh.sendSingle(from,respuesta);
  }
}
void setup() {
  Serial.begin(115200);
  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  //mesh.setDebugMsgTypes( ERROR | STARTUP | CONNECTION);  // set before init() so that you can see startup messages
  mesh.init( MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT );
  mesh.onReceive(&receivedCallback);
}

void loop() {
  // it will run the user scheduler as well
  mesh.update();
}
