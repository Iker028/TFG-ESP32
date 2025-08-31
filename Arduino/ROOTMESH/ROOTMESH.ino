
#include "painlessMesh.h"
#include "ArduinoJson.h"
#include "WiFi.h"

#define   MESH_PREFIX     "RED_MESH_SOLAR"
#define   MESH_PASSWORD   "solar1234"
#define   MESH_PORT       5555

Scheduler userScheduler; // to control your personal task
painlessMesh  mesh;
String letra="A";
String serial;
uint32_t id;

Task taskletra( TASK_SECOND * 10 , TASK_ONCE, []() {
  mesh.sendBroadcast("LETRA");
});


void receivedCallback(uint32_t from, String &msg){
  if(msg.startsWith("RLETRA")){
    Serial.println(String(from)+" "+msg.substring(msg.length()-1));
  }
  else{
    Serial.println(msg);
  }
}
void setup() {
  Serial.begin(115200);

  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  //mesh.setDebugMsgTypes( ERROR | STARTUP | CONNECTION);  // set before init() so that you can see startup messages

  mesh.init(MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT );
  mesh.setRoot(true);
  mesh.setContainsRoot(true);
  WiFi.setTxPower(WIFI_POWER_19_5dBm);
  mesh.onReceive(&receivedCallback);
  userScheduler.addTask(taskletra);
}


void loop() {
  // it will run the user scheduler as well
  mesh.update();
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "ARBOL") {
      painlessmesh::protocol::NodeTree tree = mesh.asNodeTree();
      printTree(tree,0);
    }
    else if (cmd == "LETRA"){
      Serial.println(String(mesh.getNodeId())+" "+letra);
      taskletra.restart();
      taskletra.enable();
    }
    else if (cmd=="MACS"){
      mesh.sendBroadcast(cmd);
    }
    else{
      int index=cmd.indexOf('/');
      String ssid=cmd.substring(0, index);
      uint32_t id = strtoul(ssid.c_str(), NULL, 10);
      String comando= cmd.substring(index+1);
      serial=comando;
      mesh.sendSingle(id,serial);
    }
    
  }
  
}

void printTree(painlessmesh::protocol::NodeTree tree, uint32_t fatherId){
  Serial.print("Nodo: "+String(tree.nodeId)+" ");
  Serial.print("Padre: "+String(fatherId)+ " ");
  String Hijos="";
  if(!tree.subs.empty()){
  for(auto subtree:tree.subs){
    Hijos=Hijos+String(subtree.nodeId)+",";
  }
  Hijos.remove(Hijos.length() - 1);
  Serial.print("Hijos: "+Hijos+"\n");
  for(auto child:tree.subs){
    printTree(child, tree.nodeId);
  }}
  else{Serial.println("Hijos: 0");}
}