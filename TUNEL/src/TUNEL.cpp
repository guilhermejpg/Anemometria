// Nome : Tunel anemômetria 

/* esse projeto é a criação de uma estação(Cliente) partir de um ESP32
O esp controlara a rotação do inversor de frequencia(Tunel) a partir de dados recebidos pelo servidor via TCP
O esp recebera comdandos como frases e valores numericos e fará a tarefa correspondente ao comando enviado.

O Processador 1 (loop) é dedicado a reconexão
O processador 0 é dedicado a receber os dados e administrar o buffer

 // IP SERVER 192.168.4.1
 // Ip do TUNEL 192.168.4.2
/*---------------------------------------*/


#include <Arduino.h>
#include <WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_MCP4725.h>


/*-----------------VARIAVEIS-E-OUTROS---------------------*/
#define TUNEL 17    // Pino que ligara o tunel
#define ledboard 2     // LED DO ESP
#define ledverde 25    // LED TESTE
#define BUFFERLEN 10   // Tamanho em bytes do buffer que armazena a mensagem recebida         
#define PORTA 80       // PORTA DO SERVER
#define PERIODO 1000   // Periodo de reconexao e update em ms
Adafruit_MCP4725 DAC;
char mensagemTcpIn[64] = ""; //variavel global com a mensagem recebiada via TCP
char mensagemclean[64] = "   ";  // Limpando BUFFER apos receber msg
TickType_t taskDelay = 5 / portTICK_PERIOD_MS; // ciração do delay em ms para tasks
/*---------------------------------------*/



/*-------------PARAMENTROS WIFI--------*/       
const char* SSID = "gvento";    //Nome da rede
const char* PASS =  "anemometria";  // Senha da rede
WiFiClient Server;                  // CLIENTE NOMEADO COMO SERVER PARA FACILITAR A LEITURA
/*---------------------------------------*/


/*------------------TASKS---------------------*/
void taskTcpCode(void * parameter); // faz a comunicação via socket
/*---------------------------------------*/


/*-----------------FUNÇOES----------------------*/
void setupPins();       // inicialização das saidas digitais e do SPI
void setupWireless();   // inicialização do wireless 
void launchTasks();     // Dispara as tasks.
void checkValue();      // avalia a mensagem recebida via tcp e ajusata as saidas
void connectClient();   // Inicialização da conexão ao Server
void RPMStart();        // Liga tunel
void RPMStop();         // Desliga tunel
/*---------------------------------------*/


/*----------------SETUP-----------------------*/
void setup() {
  Server.setTimeout(100);  // Tempo para considerar a conexão como perdida
  Serial.begin(115200);    // Iniciando a serial
  DAC.begin(0x60);         // Iniciando o DAC ( 0 - 4095)
  setupPins();             // Chamando a função dos parametros dos pinos
  setupWireless();         // Chamando a função dos parametros do Wiriless 
  connectClient();         // Chamando a função de conexão ao server
  launchTasks();           // Lançando as tasks
}
/*---------------------------------------*/




/*-----------------LOOP----------------------*/
void loop() { // Responsavel por reconetar o wifi e parar a comunicação com o server quando a conexão cair
  
  if(WiFi.status() != WL_CONNECTED){
    setupWireless();
    Server.stop();
    }
 if(WiFi.status() == WL_CONNECTED){
     digitalWrite(ledboard,HIGH); 
 }
delay(100);
}
/*---------------------------------------*/



/*----------------TASKS-----------------------*/
void taskTcpCode(void * parameters) {   // LEITURA DOS DADOS RECEBIDOS DO SERVER
 while(true) {
        while(Server.connected()){  // Equanto estinver conectado
        if(Server.available()>0){   // se o servidor estiver mandando dados
        int buffersize = 0;    // tamanho do buffer              
        char bufferEntrada[BUFFERLEN] = ""; // BUFFER para mensagem recebida
        while(Server.available()>0){   //enquanto o servidor estiver mandando algo(loop que realiza a leitura)
        char mensagem = Server.read(); 
          bufferEntrada[buffersize] = mensagem;
            buffersize++;
        }
        strncpy(mensagemTcpIn,bufferEntrada,buffersize); // copiando o que foi recebido(buffer) a variavel de leitura
        checkValue();    // função que ira reconhecer a mensagem  
        strncpy(mensagemTcpIn,mensagemclean,buffersize); //Limpando buffer após realizar a tarefa
        }
        vTaskDelay(taskDelay); 
 }
 while(!Server.connected())  {               // Se não estiver conectado com o server, mandamos conectar
           connectClient();                  // Função de conexão ao server
        }
 vTaskDelay(taskDelay);
}
}
/*--------------------------------------------------*/


/*----------------FUNÇOES-----------------------*/
void setupPins(){ // PINAGEM
  pinMode(ledboard,OUTPUT);
  pinMode(ledverde,OUTPUT);
  pinMode(TUNEL,OUTPUT);
  digitalWrite(TUNEL, LOW);
  digitalWrite(ledverde, LOW);
  digitalWrite(ledboard,LOW);
  DAC.setVoltage(0, false);
}

void setupWireless(){   // Parametros Wireless
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(ledboard, HIGH);
    delay(100);
    digitalWrite(ledboard, LOW);
    delay(100); 
  }
}

void launchTasks(){   // Lançando as tasks
  xTaskCreatePinnedToCore(taskTcpCode,"TRAFEGO TCP",10000,NULL,1,NULL,0); // task de leitura TCP rodando no core 0
   delay(500);
}

void checkValue()   // Checa a mensagem e realiza tarefa
 {
   Serial.println(mensagemTcpIn);// PRINTAR VALOR
   if(strcmp(mensagemTcpIn,"ligar") ==0){
            DAC.setVoltage(4095, false);
            digitalWrite(ledverde,HIGH);
            RPMStart();
              }  
  if(strcmp(mensagemTcpIn,"desligar") ==0){
      RPMStop();
            DAC.setVoltage(0, false);
              digitalWrite(ledverde,LOW);  
        }
 }

void connectClient(){ // Conexão ao server
while (!Server.connect(WiFi.gatewayIP(), PORTA)) {return;}  // fica nesse loop até reconectar ao server
}

void RPMStart(){    // LIGA TUNEL
  digitalWrite(TUNEL, HIGH);
}

void RPMStop(){     // DESLIGA TUNEL
  digitalWrite(TUNEL, LOW);
}

/*---------------------------------------*/
