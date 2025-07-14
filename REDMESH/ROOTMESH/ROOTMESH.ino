
#include "painlessMesh.h"
#include "ArduinoJson.h"

#define   MESH_PREFIX     "RED_MESH_SOLAR"
#define   MESH_PASSWORD   "solar1234"
#define   MESH_PORT       5555

Scheduler userScheduler; // to control your personal task
painlessMesh  mesh;
String letra="A";
Task taskletra( TASK_SECOND * 10 , TASK_ONCE, []() {
  mesh.sendBroadcast("LETRA");
});

void receivedCallback(uint32_t from, String &msg){
  if(msg.startsWith("RLETRA")){
    Serial.println(String(from)+" "+msg.substring(msg.length()-1));
  }
}
void setup() {
  Serial.begin(115200);

  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  //mesh.setDebugMsgTypes( ERROR | STARTUP | CONNECTION);  // set before init() so that you can see startup messages

  mesh.init( MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT );
  mesh.setRoot(true);
  mesh.setContainsRoot(true);
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
    if (cmd == "LETRA"){
      Serial.println(String(mesh.getNodeId())+" "+letra);
      taskletra.restart();
      taskletra.enable();
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