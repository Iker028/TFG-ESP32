#include <LittleFS.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <vector>
#include <algorithm>
const int ledPins[8] = {42,41,40,39,38,37,36,35};
const int luz=4;
const int Vt[2]={5,6};
bool a=true;
const String IP="192.168.4.1";
int httpCode=0;

const int string =1;
const int modulo=1;


double luminosidad(){
  double vluz=analogRead(luz);
  double vluz1=analogRead(luz);
  double Iph=vluz1/6.8;
  double L=pow(10.0,log10(Iph)/1.3059)*2535.12;
  return L;
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
          double temperatura;
          double lum;
          switch(getCommandCode(comando)){
            case 1:{
              temperatura=temp();
              responsecode=httpPost.POST(String(temperatura));
              break;}
            case 2:{
              lum=luminosidad();
              responsecode=httpPost.POST(String(lum));
              break;}
            case 3:{
              File file = LittleFS.open("/IV.txt", "r");
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
              break;}
            case 4:{
              responsecode=httpPost.POST(String(modulo)+","+String(string));break;}
              
            case 5:{
              File file = LittleFS.open("/IV.txt", "r");
              if (!file) {
                httpPost.POST("Error: no se ha encontrado archivo en memoria SPIFFS");
              }
              else{
              String fileContent = "";
              std::vector<double> Vmlist;
              std::vector<double> Imlist;
              int i=0;
              while (file.available()) {
                fileContent = file.readStringUntil('\n');
                int coma=fileContent.indexOf(",");
                double Vm=fileContent.substring(0,coma).toDouble();
                double Im=fileContent.substring(coma+1,fileContent.length()).toDouble();
                if (i==0){
                  Vmlist.push_back(Vm);
                  Imlist.push_back(Im);}
                else{
                  if(Vm!=Vmlist.back()){
                    Vmlist.push_back(Vm);
                    Imlist.push_back(Im);}
                }
              }
              String IVcorregida=algoritmo(Vmlist,Imlist,0.165,true);
              httpPost.POST(IVcorregida);
              break;
              }
              file.close();
              
              
            } 

              }
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
    if (cmd == "histeresis") return 3;
    if (cmd == "getij") return 4;
    if (cmd == "IV") return 5;
    return -1;  // Default case
}

String algoritmo(const std::vector<double>& Vmlist, const std::vector<double>& Imlist,double Rs,bool corte){
  //tenemos que dividir la curva en 2 curvas
  //para el caso de Corte (T2)---> se separan cuando Vm llega a su mínimo
  //el caso de circuito abierto (T3)---> se separan cuando Vm llega a su valor máximo
  size_t ind = 0;  // declarada antes
  if (corte){
    auto minVm = std::min_element(Vmlist.begin(), Vmlist.end());
    ind = std::distance(Vmlist.begin(), minVm);}
  else{
    auto maxVm = std::max_element(Vmlist.begin(), Vmlist.end());
    ind = std::distance(Vmlist.begin(), maxVm);}
  std::vector<double> Vrev(Vmlist.begin(), Vmlist.begin() + ind);
  std::vector<double> Vfw(Vmlist.begin() + ind, Vmlist.end());
  std::vector<double> Irev(Imlist.begin(), Imlist.begin() + ind);
  std::vector<double> Ifw(Imlist.begin() + ind, Imlist.end());

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


  double sumaC=0;
  double c=0;
  for(size_t i=0;i<Vjfw.size();i++){
    if (Vjfw.at(i)<(Vjrev.at(0)-0.1)){
      size_t k=findVm(Vjrev,Vjfw.at(i));
      c=fabs((Irev.at(k)-Ifw.at(i))/(dVjfw.at(i)-dVjrev.at(k)));
      sumaC=sumaC+c;}
  }
  double Cavg=sumaC/(Vjfw.size());

  String curvaIV="";

  for(size_t i=0;i<Ifw.size();i++){
    if (Vjfw.at(i)<(Vjrev.at(0)-0.1)){
      double I=Ifw.at(i)+Cavg*dVjfw.at(i);
      curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(I,7)+"\n";}
    else{curvaIV=curvaIV+String(Vfw.at(i),7)+","+String(Ifw.at(i),7)+"\n";}
  }
  return curvaIV;
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

