// Nome : Tunel anemômetria 

/* esse projeto é a criação de uma estação(Cliente) partir de um ESP32
O esp controlara a rotação do inversor de frequencia(Tunel) a partir de dados recebidos pelo servidor via TCP
O esp recebera comdandos como frases e valores numericos e fará a tarefa correspondente ao comando enviado.

O Processador 1 (loop) é dedicado a reconexão
O processador 0 é dedicado a receber os dados, e realizar as tarefas

 // IP SERVER 192.168.4.1
 // Ip do TUNEL 192.168.4.2
/*---------------------------------------*/


#include <Arduino.h>
#include <WiFi.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_MCP4725.h>
#include <MCP_DAC.h>

/*-----------------VARIAVEIS-E-OUTROS---------------------*/
#define TUNEL 17    // Pino que ligara o tunel
#define ledboard 2     // LED DO ESP
#define ledverde 25    // LED TESTE
#define BUFFERLEN 10   // Tamanho em bytes do buffer que armazena a mensagem recebida         
#define PORTA 80       // PORTA DO SERVER
#define PERIODO 1000   // Periodo de reconexao e update em ms
char mensagemTcpIn[64] = ""; //variavel global com a mensagem recebiada via TCP
char mensagemclean[64] = "   ";  // Limpando BUFFER apos receber msg
bool control = false;   // booleana de controle da rotação
int rpm_min = 201;      // velocidade minina(2m/s) - valor que o dac le 
int rpm;                // variavel que armazena a velociadde enviada
TickType_t taskDelay = 5 / portTICK_PERIOD_MS; // ciração do delay em ms para tasks
MCP4921 MCP;      //objeto direcioando ao DAC 
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
void rotacao();         // Altera rotação
/*---------------------------------------*/


/*----------------SETUP-----------------------*/
void setup() {
  MCP.selectVSPI();        // needs to be called before begin()
  MCP.begin(5);            // 5 for VSPI and 15 for HSPI
  Server.setTimeout(100);  // Tempo para considerar a conexão como perdida
  Serial.begin(115200);    // Iniciando a serial
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
  MCP.analogWrite(0, 0);

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
rpm = atoi(mensagemTcpIn);    // CHAR PARA INT

if(control == true) {rotacao();}  // CHAMA A FUNÇÃO DE TROCA DE ROTAÇÃO
  
if(strcmp(mensagemTcpIn,"run") == 0) {RPMStart();}  // QUANDO FOR RECEBIDO A MSG 'RUN' LIGA O TUNEL

if(strcmp(mensagemTcpIn,"stop") == 0) {RPMStop();}  // QUANDO FOR RECEBIDO A MSG 'STOP' DESLIGA O TUNEL
 }

void connectClient(){ // Conexão ao server
while (!Server.connect(WiFi.gatewayIP(), PORTA)) {return;}  // fica nesse loop até reconectar ao server
}

void RPMStart(){  // LIGA TUNEL
  Serial.println("TUNEL:ON");
            digitalWrite(ledverde,HIGH);
            MCP.analogWrite(rpm_min, 0);
            control = true;
  digitalWrite(TUNEL, HIGH);
}

void RPMStop(){   // DESLIGA TUNEL
   Serial.println("TUNEL:OFF");
   MCP.analogWrite(0, 0);
             control = false;
              delay(200);
              digitalWrite(ledverde,LOW);  
  digitalWrite(TUNEL, LOW);
  
}

void rotacao(){   // CONTROLA O DAC - ALTERA ROTAÇÃO
  if(rpm <= 201){
     rpm = 201;
   }
  Serial.println("CONTROLE DE ROTAÇÃO:ON");
  MCP.analogWrite(rpm, 0);
}
/*---------------------------------------*/
