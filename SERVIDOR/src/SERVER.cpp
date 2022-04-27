#include <Arduino.h>
#include <WiFi.h>
#include <WebSockets.h>
#include <WebSocketsClient.h>
#include <WebSocketsServer.h>
#include <WebSocketsVersion.h>

#define PERIODO 1000 //periodo de reconexao e update em ms



/*------------VARIAVEIS-GLOBAIS--------*/
bool estadoled = 0;      
const char* ssid = "gvento";    //Nome da rede
const char* senha =  "anemometria";   // Senha da i
String valor_recebido;          // String para valor recebido via Serial                           
/*---------------------------------------*/


/*-------------PARAMENTROS WIFI--------*/                                   
WiFiServer server(80);  // porta do servidor, padrão 80
IPAddress local_IP(192,168,4,169);  //wireless
IPAddress gateway(192, 168, 0, 1);  //wireless
IPAddress subnet(255, 255, 0, 0);   //wireless
/*---------------------------------------*/

/*-------------VOID PADRÃO WEBSOCKET--------*/

/*---------------------------------------*/

/*-------------FUNÇÕES--------*/
void setupServer();   // Setup Servidor
void openServer();    // Abrindo servidor para conexão
void launchTasks();   // inicia as tasks
void CheckSerial();   // Monitora a serial
/*---------------------------------------*/



/*-------------TASKS--------*/
TaskHandle_t taskClient;
void taskCheckClient(void * parameters);  //Checa periodicamente o wifi e verifica se tem atualização
/*---------------------------------------*/



/*-------------OUTROS--------*/
int const coreTask = 0; //Core onde rodarão as tasks nao relacionadas a comunicação (controle do pot/saidas digitais no caso)
/*---------------------------------------*/



/*-------------VOID-SETUP-------------*/
void setup() {
Serial.begin(115200);   // Iniciando o serial com baudrate de 115200
Serial.setTimeout(200); // Limitando o delay de respota entre serial - esp
setupServer();          // chamando a função 
launchTasks();          // chamando a função 
pinMode(23,OUTPUT); 
digitalWrite(23, estadoled);
}
/*---------------------------------------*/





void loop() {
  CheckSerial();
  //vTaskDelete(NULL); //não utiliza o void loop. As tasks lançadas no launchTasks. 
}

void setupServer(){  //Configuração do Incial do servidor
  if(!WiFi.softAPConfig(local_IP,gateway,subnet)){}             //configura o ip estatico
  WiFi.mode(WIFI_AP); // MODO ESTACÃO/PONTO DE ACESSO
  WiFi.softAP(ssid,senha);  // login e senha da rede
  server.begin(); // inicia o server
  Serial.println("Configurando servidor");
  delay(100);
  openServer(); // CHAMANDO A FUNÇÃO
  
}

void openServer(){  //Abrindo o servidor 
  WiFiClient client = server.available();
  Serial.println("Abrindo Servidor");
  Serial.println(WiFi.localIP());
  delay(200);
   Serial.println("Servidor Online");
}

void launchTasks(){ // lança as taks
  delay(2000);
  xTaskCreatePinnedToCore(taskCheckClient,"SERVIDOR",5000,NULL,1,&taskClient,CONFIG_ARDUINO_RUNNING_CORE);
}

void taskCheckClient (void * parameters) {   // CHECA SE TEM CLIENTE E DISPONIBILZA O SERVER
  for (;;) {
    WiFiClient client = server.available();
  if (client) {
    if (client.connected()) {
      Serial.println("Connected to client");
    }
      vTaskDelay(PERIODO/portTICK_PERIOD_MS);
  
}
  }
}

void CheckSerial(){   // LE DADOS DA SERIAL 

if(Serial.available()>0){    // SE TIVER ALGUM DADO NA SERIAL
    
    /*CONVERSÃO STRING PARA CHAR*/
    valor_recebido = Serial.readString();
    int valor_len = valor_recebido.length() + 1;
    char valor_array[valor_len];
    valor_recebido.toCharArray(valor_array,valor_len);
    /*--------------------------------*/
    
       Serial.print(valor_array);
       if(strcmp(valor_array,"ligar")==0){
        estadoled =! estadoled;
        digitalWrite(23,estadoled);
      }
        

}

}