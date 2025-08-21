#include "painlessMesh.h"
#include <LittleFS.h>
#include <vector>
#include <algorithm>

#define   MESH_PREFIX     "RED_MESH_SOLAR"
#define   MESH_PASSWORD   "solar1234"
#define   MESH_PORT       5555

Scheduler userScheduler; // to control your personal task
const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int luz=4;
const int Vt[2]={5,6};
painlessMesh  mesh;
String letra="B";
const int string =1;
const int modulo=1;

double luminosidad(){
  double vluz=analogRead(luz);
  double vluz1=analogRead(luz);
  return (vluz1)/0.00646;
}
/**
Método que calcula la temperatura
*/
double temp(){
  double Vp=analogRead(Vt[0]);
  double Vn=analogRead(Vt[1]);
  double deltaV=-(Vp-Vn)*pow(10.0,-3.0);
  double rt=100.0*(0.5-(deltaV/3.3))/(0.5+(deltaV/3.3));
  double T=(1.0/(298.0)+(1.0/(4550))*log(rt/100.0));
  T=(1.0/T)-273.0;
  return T;
}

void receivedCallback(uint32_t from, String &msg){
  if(msg.startsWith("LETRA")){
    String respuesta="RLETRA: "+letra;
    mesh.sendSingle(from,respuesta);
  }
  else{
    double temperatura;
    double lum;
    switch(getCommandCode(msg)){
        case 1:{
          temperatura=temp();
          mesh.sendSingle(from,String(temperatura));
          break;}
        case 2:{
          lum=luminosidad();
          mesh.sendSingle(from,String(lum));
          break;}
        case 3:{
            File file = LittleFS.open("/IVizq.txt", "r");
              String fileContentizq = "";
              if (!file) {
              }
              else{
              while (file.available()) {
                fileContentizq += (char)file.read();
              }
              }
              file.close();
              file = LittleFS.open("/IVder.txt", "r");
              String fileContentder="";
              if (!file) {
                
              }
              else{
              while (file.available()) {
                fileContentder += (char)file.read();
              }
              }
              file.close();
              mesh.sendSingle(from,fileContentizq+fileContentder);
              break;}
        case 4:{
              mesh.sendSingle(from,String(modulo)+","+String(string));
              break;}
        case 5:{
              File file = LittleFS.open("/IVizq.txt", "r");
              String IVizqcorregida="";
              if (!file) {Serial.println("HOLA");
              }
              else{
              String fileContentizq = "";
              std::vector<double> Vmlistizq;
              std::vector<double> Imlistizq;
              int i=0;
              while (file.available()){
                fileContentizq = file.readStringUntil('\n');
                int coma=fileContentizq.indexOf(",");
                double Vmizq=fileContentizq.substring(0,coma).toDouble();
                double Imizq=fileContentizq.substring(coma+1,fileContentizq.length()).toDouble();
                if (i==0){
                  Vmlistizq.push_back(Vmizq);
                  Imlistizq.push_back(Imizq);}
                else{
                  if(Vmizq!=Vmlistizq.back()){
                    Vmlistizq.push_back(Vmizq);
                    Imlistizq.push_back(Imizq);}
                }
              }
              IVizqcorregida=algoritmo(Vmlistizq,Imlistizq,0.165,true);
              }
              file.close();

              file = LittleFS.open("/IVder.txt", "r");
              String IVdercorregida="";
              if (!file) {
              }
              else{
              String fileContent = "";
              std::vector<double> Vmlistder;
              std::vector<double> Imlistder;
              int i=0;
              while (file.available()) {
                fileContent = file.readStringUntil('\n');
                int coma=fileContent.indexOf(",");
                double Vmder=fileContent.substring(0,coma).toDouble();
                double Imder=fileContent.substring(coma+1,fileContent.length()).toDouble();
                if (i==0){
                  Vmlistder.push_back(Vmder);
                  Imlistder.push_back(Imder);}
                else{
                  if(Vmder!=Vmlistder.back()){
                    Vmlistder.push_back(Vmder);
                    Imlistder.push_back(Imder);}
                }
              }
              IVdercorregida=algoritmo(Vmlistder,Imlistder,0.165,false);
              }
              file.close();
              Serial.println(IVizqcorregida+IVdercorregida);
              mesh.sendSingle(from,IVizqcorregida+IVdercorregida);
              break;
            }

            case 6:{
              File file = LittleFS.open("/IVizq.txt", "r");
              String IVizqcorregida="";
              if (!file){}
              else{
              String fileContentizq = "";
              String oppoint = file.readStringUntil('\n');
              mesh.sendSingle(from,oppoint);
              }
              }
          }

  }
}
void setup() {
  Serial.begin(115200);
  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE ); // all types on
  //mesh.setDebugMsgTypes( ERROR | STARTUP | CONNECTION);  // set before init() so that you can see startup messages
  mesh.init( MESH_PREFIX, MESH_PASSWORD, &userScheduler, MESH_PORT );
  mesh.onReceive(&receivedCallback);
  if (!LittleFS.begin(true)) {
    Serial.println("Error al montar LITTLEFS");}
}

void loop() {
  // it will run the user scheduler as well
  mesh.update();
}


int getCommandCode(String cmd) {
    if (cmd == "temperatura") return 1;
    if (cmd == "luminosidad") return 2;
    if (cmd == "histeresis") return 3;
    if (cmd == "getij") return 4;
    if (cmd == "IV") return 5;
    if (cmd=="OP") return 6;
    return -1;  // Default case
}

String algoritmo(const std::vector<double>& Vmlist, const std::vector<double>& Imlist,double Rs,bool corte){
  //tenemos que dividir la curva en 2 curvas
  //para el caso de Corte (T2)---> se separan cuando Vm llega a su mínimo
  //el caso de circuito abierto (T3)---> se separan cuando Vm llega a su valor máximo
  size_t ind = 0;  // declarada antes
  size_t j=0;
  double epsilon=0.05;
  if (corte){
    auto minVm = std::min_element(Vmlist.begin(), Vmlist.end());
    ind = std::distance(Vmlist.begin(), minVm);
    j=ind;
    while(fabs(Imlist.at(ind)-Imlist.at(j))<=epsilon){
    j=j+1;}
    }
  else{
    auto maxVm = std::max_element(Vmlist.begin(), Vmlist.end());
    ind = std::distance(Vmlist.begin(), maxVm);
    j=ind;
    while(fabs(Imlist.at(ind)-Imlist.at(j))<=epsilon){
      j=j+1;}}
  j=j-ind;
  std::vector<double> Vrev(Vmlist.begin(), Vmlist.begin() + ind-1);
  std::vector<double> Vfw(Vmlist.begin() + ind-1, Vmlist.end());
  std::vector<double> Irev(Imlist.begin(), Imlist.begin() + ind-1);
  std::vector<double> Ifw(Imlist.begin() + ind-1, Imlist.end());

  std::vector<double> Vjrev;
  std::vector<double> Vjfw;

  //Calculo Vj=Rs*Im+Vm
  for (size_t i=0; i<Vrev.size();i++){
    Vjrev.push_back(Rs*Irev[i]+Vrev[i]);
    
  }
  for (size_t i=0; i<Vfw.size();i++){
    Vjfw.push_back(Rs*Ifw.at(i)+Vfw.at(i));
  }

  //Calculo la derivada (numerica primer orden) de Vjrev y Vjfw
  //las esquinas (-3*f_0+4*f_1-f_2)/(2*h)
  //(f_(n-2)-4f_(n-1)+3*f_n)/(2*h)
  //las demás : (f(n+1)-f(n-1))/2h)
  std::vector<double> dVjrev;
  std::vector<double> dVjfw;
  double h=35*pow(10.0,-6.0);
  for(size_t i=0; i<Vjrev.size(); i++){
    if(i==0){
      double numerador = (-3*Vjrev.at(i)+4*Vjrev.at(i+1)-Vjrev.at(i+2));
      dVjrev.push_back(numerador/(2*h));
    }
    else if(i==Vjrev.size()-1){
      dVjrev.push_back((3*Vjrev.at(i)-4*Vjrev.at(i-1)+Vjrev.at(i-2))/(2*h));
    }
    else{
      double numerador = (Vjrev.at(i+1)-Vjrev.at(i-1));
      dVjrev.push_back(numerador/(2*h));
    }
  }
  for(size_t i=0; i<Vjfw.size(); i++){
    if(i==0){
      double numerador=(-3*Vjfw.at(i)+4*Vjfw.at(i+1)-Vjfw.at(i+2));
      dVjfw.push_back(numerador/(2*h));
    }
    else if(i==Vjfw.size()-1){
      dVjfw.push_back((3*Vjfw.at(i)-4*Vjfw.at(i-1)+Vjfw.at(i-2))/(2*h));
    }
    else{
      double numerador = (Vjfw.at(i+1)-Vjfw.at(i-1));
      dVjfw.push_back(numerador/(2*h));
    }
  }

  /*
  double sumaC=0;
  double c=0;
  int numero=0;
  for(size_t i=0;i<Vjfw.size();i++){
    size_t k=findVm(Vjrev,Vjfw.at(i));
    //(Vjfw.at(i)<(Vjrev.at(0)-0.1))
    if ((fabs(Vfw.at(i)-Vrev.at(0))>0.3)&&((dVjfw.at(i)-dVjrev.at(k))!=0)){
      c=fabs((Irev.at(k)-Ifw.at(i))/(dVjfw.at(i)-dVjrev.at(k)));
      numero=numero+1;
      sumaC=sumaC+c;}
  }
  double Cavg=sumaC/numero;
  Serial.println(Cavg,14);
  */

  std::vector<double> Clist;
  double c=0;
  for(size_t i=0;i<Vjfw.size();i++){
    size_t k = findVm(Vjrev,Vjfw.at(i));
    if ((dVjfw.at(i)-dVjrev.at(k))!=0){
      c=fabs((Irev.at(k)-Ifw.at(i))/(dVjfw.at(i)-dVjrev.at(k)));
      Clist.push_back(c);
    }
    else{Clist.push_back(0);}
  }
  String curvaIV="";
  for(size_t i=0;i<Ifw.size();i++){
    double I=Ifw.at(i)+Clist.at(i)*dVjfw.at(i);
    if(fabs(Vfw.at(i)-Vrev.at(0))>0.3){curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(I,7)+"\n";}
    else{curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(Ifw.at(i),7)+"\n";}
  }
  return curvaIV;


  /*
  String curvaIV="";

  for(size_t i=0;i<Ifw.size();i++){
    if(i>j){
      double I=Ifw.at(i)+Cavg*dVjfw.at(i);
      if (fabs(Vfw.at(i)-Vrev.at(0))>0.3){
        if(I<=Irev.at(0)+0.3){
          curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(I,7)+"\n";}
        else{curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(Irev.at(0)+0.3,7)+"\n";}}
      else{curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(Ifw.at(i),7)+"\n";}
  }
    else if(corte){
      curvaIV=curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(Ifw.at(i),7)+"\n";
    }
  
  
  }
  return curvaIV;
  */



}


size_t findVm(const std::vector<double>& lista, double Vm){ 
  if (lista.empty()) return -1;
  size_t indiceCercano = 0;
  double diferenciaMin = fabs(lista[0] - Vm);
  for (size_t i = 1; i < lista.size(); i++) {
    double diferencia = fabs(lista[i] - Vm);
    if (diferencia < diferenciaMin) {
      diferenciaMin = diferencia;
      indiceCercano = i;
    }
  }
  return indiceCercano;
}


