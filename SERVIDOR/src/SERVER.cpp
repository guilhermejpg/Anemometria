// Nome : Servidor anemômetria 

/* esse projeto é a criação de um servidor e um acess point(AP) a partir de um ESP32
O esp disponibilza uma rede e um servidor para enviar comandos para o tunel( alterar rotação) via TCP
O projeto trabalhara em conjunto ao script em python para enviar os comandos via Serial para o server, e o server 
enviar os comandos via TCP/IP.
O Processador 1 é dedicado a conexão, envio de dados e leitura Serial
O processador 0 está livre

 // IP SERVER 192.168.4.1
 // Ip do TUNEL 192.168.4.2


/*---------------------------------------*/
#include <Arduino.h>       // BIBLIOTECA PADRÃO
#include <WiFi.h>          // BIBLIOTECA  WIFI
#include <WiFiServer.h>    // BIBLIOTECA SERVER  
#define PERIODO 500        // Periodo de reconexao e update em ms



/*------------VARIAVEIS-GLOBAIS--------*/
static uint8_t taskCoreOne = 1;   // core 1 para tasks ()
static uint8_t taskCoreZero = 0;  // Core  0 para tasks ()
bool estadoled = 0;               // Estado do led para       
String recebido;                  // String para leitura da Serial
String leSerial(){                // FUNÇÃO PARA LER A SERIAL
  String conteudo = "";
  char caractere;
  
  // Enquanto receber algo pela serial
  while(Serial.available() > 0) {
    // Lê byte da serial
    caractere = Serial.read();
    // Ignora caractere de quebra de linha
    if (caractere != '\n'){
      // Concatena valores
      conteudo.concat(caractere);
    }
    // Aguarda buffer serial ler próximo caractere
    delay(10);
  }
  
  return conteudo;
}           
/*---------------------------------------*/


/*-------------PARAMENTROS WIFI--------*/                                   
const char* ssid = "gvento";          // Nome da rede
const char* senha =  "anemometria";   // Senha da rede
WiFiServer  Server(80);               // Porta do Servidor - (80)
WiFiClient  tunelClient;              // cliente direcionado ao tunel 
/*---------------------------------------*/


/*-------------FUNÇÕES--------*/
void setupWifi();   // Setup Servidor
void launchTasks();   // Inicia as tasks
/*---------------------------------------*/

/*-------------VOID-SETUP-------------*/
void setup() {
Serial.begin(115200);               // Iniciando o serial com baudrate de 115200
Serial.setTimeout(200);             // Limitando o delay de respota entre serial - esp
setupWifi();                        // Chamando a função de Setup do Wifi
launchTasks();                      // Chamando a função que Inicia as tasks
Server.begin();                     // Inicia o server
tunelClient = Server.available();   // disponibiliza o servidor para o cliente
pinMode(23,OUTPUT);     
digitalWrite(23, estadoled);
}
/*---------------------------------------*/


void loop() {
  if(tunelClient){
  if(tunelClient.connected()){ //SE  O CLIENTE ESTA CONECTADO            
      digitalWrite(23,HIGH);
      delay(150);
      digitalWrite(23,LOW);
      delay(150);
       recebido = leSerial();    // chama a função que le a serial e armazena na variavel
       tunelClient.print(recebido);   // print  e flush devem trabalhar em conjunto para escrever dados
       tunelClient.flush();
       delay(500);
       tunelClient.stop();
  }
  }
  if(!tunelClient){     // Server online aguardando cliente
  digitalWrite(23,HIGH);
  tunelClient = Server.available();
   }
delay(200);
  }


void setupWifi(){       // SETUP WIFI
  WiFi.mode(WIFI_AP);                 // Coloca este ESP como Access Point
  WiFi.softAP(ssid,senha);            // Login e senha da rede
}

void launchTasks(){     // Lança as taks
    delay(500);
}

