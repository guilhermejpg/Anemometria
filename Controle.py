import serial       # Biblioteca Comunicação Serial
import time         # biblioteca do tempo
import numpy as np  
import pandas as pd
import sys  
import threading    # Biblioteca para multi-threading(multitask)
import os
import nidaqmx      # Bibliotecas da placa da national
from nidaqmx.constants import AcquisitionType       
from nidaqmx.constants import TerminalConfiguration


#/------------------------------------VARIAVEIS GLOBAIS---------------------------------------------------#/

padraom =   []            # lista Media do mA - Principal
padraos =   []            # lista desvio mA - Principal
padraom2 =  []            # lista Media do mA - Secundario
padraos2 =  []            # lista desvio mA - Secundario
pressao =   []            # Lista para Pressão
jato =      []            # Lista para Media da Temperatura "Jato"
seco =      []            # Lista para Media da Temperatura "Seco"
umido =     []            # Lista para Media da Temperatura "Umido"
pulsosm =   []            # Lista para Media da Frequencia
pulsoss =   []            # Lista para Desvio da frequencia

variavel = ['mA', 'Desvio(mA)','Jato','Seco','Umido','Pressão(kPa)','Pulsos','Desvio(Pulsos)'] # Variaveis aquisitadas

rpm = [0,161,196,231,263,299,334,368,403,436,471,506,538,573]     # pontos da calibração
#/------------------------------------------------------------------------------------#/




#/------------------------------------FUNÇÕES--------------------------------------------------#/

def convert(rpm): #Função Conversão rpm para valor DAC
    return (rpm/1683)*4095

rampa = list(map(convert,rpm)) # Aplicando a função 'convert' em todos os rpm's (Pontos da calibração)

def temp(): # Função para ler temperatura dos sensores a partir do arquivo de texto
    
    j =[]   # lista que recebe os valores na parte do jato
    s =[]   # lista que recebe os valores na parte do seco
    u = []  # lista que recebe os valores na parte do umido
    
    arquivo = open("C:/Users/guilhermeas/Desktop/ko.txt", "r") #abrindo arquivo
    dados =arquivo.readlines()  # readlines le linha por linha e adiciona em uma lista / read le o arquivo todo 
    comp = len(dados)           # descobrindo o N de linhas( ou numero de elementos na lista)
    inicio = comp - 30          # Inicio da nossa faixa
    final = comp -1             # final da nossa faixa (penultima linha)
    faixa = (list(dados[inicio:final])) # Fatiando a faixa de linhas que desejamos e transformando em lista

    for linha in faixa:         # para cada linha dentro da faixa
        tr164 = linha[24:29]   
        tr163 = linha[34:39]   
        tr166 = linha[44:49]    
        j.append(format(float(tr164), '.1f'))
        s.append(format(float(tr163), '.1f'))
        u.append(format(float(tr166), '.1f'))
            
    else:
        tr164_array = np.array(j)
        tr163_array = np.array(s)
        tr166_array = np.array(u)
        tr164f = tr164_array.astype(float)
        tr163f = tr163_array.astype(float)
        tr166f = tr166_array.astype(float)
        jm = tr164f.mean()
        sm = tr163f.mean()
        um = tr166f.mean()
        jato.append(format(float(jm), '.1f'))
        seco.append(format(float(sm), '.1f'))
        umido.append(format(float(um), '.1f'))
        print('Jato: ' + str(format(jm, '.1f')))
        print('Seco: ' + str(format(sm, '.1f')))
        print('Umido: ' + str(format(um, '.1f')))
        arquivo.close()
           
def PA16(): # função para ler o barometro
    com = serial.Serial("COM5", timeout=3)

    def ler_ponto(com):
        valores = []
        while True:
            com.flushInput()
            com.write(b'PRR\r\n')
            x = com.readline()
            time.sleep(1)
            valores.append(float(x[2:9]))
            if len(valores) > 5: break
        return valores


    while True:
        valores = np.array(ler_ponto(com))
        valm = valores.mean()
        print("pressão: " + str(format(valm, '.3f')))
        pressao.append(str(format(valm, '.3f')))
        break

def ni(): # função para contar os pulsos
    freq = []        # Lista para Frequencia medida                 
    freqs =     []   # Lista para Desvio da frequencia
    freqm =     []   # Lista para Media da Frequencia
    ref = 5
    minimo = 3
    maximo = 9.9
    
    adcminimo = 0
    adcmaximo = 10
    while True:
        for j in range(3):
                print("Contando Pulsos...")
                with nidaqmx.Task() as task:
                        freq_aq = 4000
                        total_samples = 30*freq_aq
                        canal = task.ai_channels.add_ai_voltage_chan("Dev1/ai0", min_val=adcminimo, max_val=adcmaximo)
                        task.timing.cfg_samp_clk_timing(freq_aq,sample_mode = AcquisitionType.CONTINUOUS)
                        medicoes = task.read(number_of_samples_per_channel=total_samples, timeout=total_samples/freq_aq+10)
                        task.stop
	
                indices = []
                
                
                for i in range(len(medicoes)):
                        #print(medicoes[i])
                        if medicoes[i] < minimo:
                                medicoes[i]=minimo
                        if medicoes[i] > maximo:
                                medicoes[i]=maximo
                        if medicoes[i] >=ref and medicoes[i-1] < ref:
                                indices.append(i)
                tempo_final = (indices[-1] - indices[0])/freq_aq
                resultado=(len(indices)-1)/tempo_final
                freq.append(format(float(resultado), '.3f')) 
                #print(format(float(resultado), '.3f'))
                
        else:
                
                freqlist = np.array(freq)
                freqarray = freqlist.astype(float)
                freqm = freqarray.mean()
                freqs = freqarray.std()
                pulsosm.append(format(float(freqm), '.3f'))
                pulsoss.append(format(float(freqs), '.3f'))
                print(format(float(freqm), '.3f')+ " Hz")
                print(format(float(freqs), '.3f'))
                break
        
def druck(): # FUnção para ler o multimetro Principal
    tempo = 30

    com = serial.Serial("COM1", timeout=1)

    def ler_ponto(com):
        valores = []
        while True:
            com.flushInput()
            com.write(b'VAL?\n')
            x = com.readline()
            time.sleep(1)
            valores.append(float(x))
            if len(valores) > 29: break
        return valores


    while True:
        valores = np.array(ler_ponto(com))
        valm = valores.mean()
        vals = valores.std()
        print( "mA " + str(format(valm*1000, '.3f')) + " " + str(format(vals*1000, '.3f')) + "\n")
        padraom.append(format(valm*1000, '.3f'))
        padraos.append(format(vals*1000, '.3f'))
        break

def druck2(): #FUnção para ler o multimetro Secundario
    tempo = 30

    com = serial.Serial("COM19", timeout=1)

    def ler_ponto(com):
        valores = []
        while True:
            com.flushInput()
            com.write(b'VAL?\n')
            x = com.readline()
            time.sleep(1)
            valores.append(float(x))
            if len(valores) > 29: break
        return valores


    while True:
        valores = np.array(ler_ponto(com))
        valm = valores.mean()
        vals = valores.std()
        print(str(format(valm*1000, '.3f')) + "  " + str(format(vals*1000, '.3f')) + "\n")
        padraom2.append(format(valm*1000, '.3f'))
        padraos2.append(format(vals*1000, '.3f'))
        break

#/------------------------------------------------------------------------------------#/



#/-------------------------------INICIALIZAÇÃO-----------------------------------------#/   

print("Digite 'run' para ligar o tunel\n")
print("Digite 'stop' para desligar o tunel\n")
print("Digite 'copos' para iniciar a calibração de copos\n")

while True: #Loop para a conexão com o Arduino
    try:  #Tenta se conectar, se conseguir, o loop se encerra
        arduino = serial.Serial('COM3', 115200)
        print('Aguarde...')
        time.sleep(10)
        print('Tunel conectado!')
        break
    except:
        pass

 #/------------------------------------------------------------------------------------#/   

#/------------------------------------------------------------------------------------#/

while True: #Loop principal
    
    print('\n')   
    cmd = input('Digite:') #Pergunta ao usuário se ele deseja ligar ou desligar o le
       
    if( cmd == 'run'):       
        print('Tunel ligado!')
        arduino.write(cmd.encode())
        arduino.flush() #Limpa a comunicação
        
    if( cmd == 'stop'):     
        print('Tunel desligado!')
        arduino.write(cmd.encode())
        arduino.flush() #Limpa a comunicação
        
    if( cmd == 'druck'):    #Função para ler o druck
        druck()

    if(cmd == 'aqr'):   # Aquisitar tudo
        PA16()
        temp()
        druck()
        
    if(cmd == 'pulsos'):    # Aquisitar pulsos
        ni()

    if( cmd == 'pa'):    #Função para ler o barometro
        PA16()

    if( cmd == 'temp'):    #Função para ler a temperatura
        temp()

    if( cmd == 'embraport'):    
        threading.Thread(target=druck).start()

    if (cmd.isdigit()):     #Função para enviar rotação(valor numerico)
        value = int(cmd)
        value = (value/1683)*4095
        print('Rotação enviada!')
        print(round(value,0))
        arduino.write(str(round(value,0)).encode())
        arduino.flush() #Limpa a comunicação
        

    if( cmd == 'copos'):        # Função de calibração de copos
        try:
            os.remove('C:/Users/guilhermeas/Desktop/calibracao.xlsx')
        except OSError as e:
            print(f"Error:{ e.strerror}\n")
        padraom = []
        padraos = []    
        pressao = []
        jato = []
        seco = []
        umido = []
        freqs = []
        freqm = []
        pulsosm = []
        pulsoss = []
        liga = 'run'
        arduino.write(liga.encode())
        arduino.flush() #Limpa a comunicação
        print('Iniciando Calibração')
        time.sleep(3)
        
        for i in range(1,len(rampa)):   #Loop de troca de rotação e aquisição
            print("\nRealizando ponto:" + str(i))
            #print("RPM:" + str(rpm[i]))
            print('Ajustando velocidade...')
            arduino.write(str(round(rampa[i])).encode())
            arduino.flush() #Limpa a comunicação
            time.sleep(15)
            print('Estabilizando...')
            print('Medindo Ambiente')
            time.sleep(15)
            threading.Thread(target=PA16).start()
            threading.Thread(target=temp).start()
            print('Medindo Padrão...')
            time.sleep(1)
            threading.Thread(target=druck).start()
            ni()
            df = pd.DataFrame((zip(padraom, padraos,jato,seco,umido,pressao,pulsosm,pulsoss)), columns = ['mA', 'Desvio(mA)','Jato','Seco','Umido','Pressão(kPa)','Pulsos','Desvio(Pulsos)'])
            for coluna in variavel:

                df[coluna]     = df[coluna].astype(str)
                df[coluna]      =df[coluna].str.replace('.',',')
    
            else:
                df.to_excel('C:/Users/guilhermeas/Desktop/calibracao.xlsx', index = False)
                print(df)
        else:
            print('\nCalibração Finalizada\n')
            rpmmin = 0
            arduino.write(str(rpmmin).encode())
            arduino.flush() #Limpa a comunicação
            
