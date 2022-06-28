import serial #Importa a biblioteca
import time     #biblioteca do tempo
import numpy as np
import pandas as pd
import sys
import nidaqmx
import threading
import os
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import TerminalConfiguration

padraom = []            # lista mA
padraos = []            # lista desvio mA
padraom2 = []            # lista mA - secundario
padraos2 = []            # lista desvio mA - secundario
pressao = []
jato = []
seco = []
umido = []
freqs = []
freqm = []
pulsosm = []
pulsoss = []
variavel = ['mA', 'Desvio(mA)','Jato','Seco','Umido','Pressão(kPa)','Pulsos','Desvio(Pulsos)']
variavel2 = ['mA', 'Desvio(mA)','Jato','Seco','Umido','Pressão(kPa)','mA2', 'Desvio(mA2)']

rpm = [0,161,198,231,264,301,335,369,404,438,470,507,542,574]     # pontos da calibração - Copos(Pulsos)
rpm2 = [0,195,200,228,263,298,330,364,398,433,466,499,533,569]     # pontos da calibração - Copos(mA)

def convert(rpm):
    return (rpm/1683)*4095
rampa = list(map(convert,rpm))


def convert(rpm2):
    return (rpm2/1683)*4095
rampa2 = list(map(convert,rpm2))


rpm3 = [0,]     # pontos da calibração - EXTRA

def convert(rpm3):
    return (rpm3/1683)*4095
rampa3 = list(map(convert,rpm3))

def young():
    vel = []
    dire = []
    arquivo = open("C:/Users/guilhermeas/Desktop/teraterm.log", "r")
    dados =arquivo.readlines()
    comp = len(dados)
    inicio = comp - 30
    final = comp - 1
    faixa = (list(dados[inicio:final]))

    for linha in faixa:
        valor = linha[2:6]
        grau = linha[7:10]
        vel.append(format(float(valor), '.1f'))
        dire.append(format(float(grau), '.1f'))

            

    else:
        valor_array = np.array(vel)
        dire_array = np.array(dire)
        valorf = valor_array.astype(float)
        diref = dire_array.astype(float)
        direm = diref.mean()
        dire_desv = diref.std()
        valorm = valorf.mean()
        desv = valorf.std()
        #print(vel)
        print('Velocidade: ' + str(format(valorm, '.2f'))+ ' '+ str(format(desv, '.2f')))
        print('Direção: ' + str(format(direm, '.2f'))+ ' '+ str(format(dire_desv, '.2f')))
        arquivo.close()



def temp():
    j =[]
    s =[]
    u = []
    arquivo = open("C:/Users/guilhermeas/Desktop/ko.txt", "r")
    dados =arquivo.readlines()
    comp = len(dados)
    inicio = comp - 30 
    final = comp -1
    faixa = (list(dados[inicio:final]))

    for linha in faixa:
        
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
           
def PA16():
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

def ni():
    freq = []
    ref = 5
    minimo = 3
    maximo = 9.9
    
    adcminimo = 0
    adcmaximo = 10
    while True:
        for j in range(30):
                print("Contando Pulsos...")
                with nidaqmx.Task() as task:
                        freq_aq = 4000
                        total_samples = 5*freq_aq
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


        
def druck():
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

def druck2():
    tempo = 30

    com = serial.Serial("COM6", timeout=1)

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

    
print("Digite 'run' para ligar o tunel\n")
print("Digite 'stop' para desligar o tunel\n")
print("Digite 'copos' para iniciar a calibração de copos - Pulsos\n")
print("Digite 'copos2' para iniciar a calibração de copos - mA\n")
print("Digite 'aqr' para aquisitar temperatura,pressão e mA\n")
print("Digite 'pa'  para aquisitar pressão\n")
print("Digite 'temp' para aquisitar temperatura\n")
print("Digite 'pulsos' para aquisitar pulsos\n")
print("Digite 'druck' para aquisitar o multimetro Principal\n")
print("Digite 'druck2' para aquisitar o multimetro Secundario\n")
print("Digite 'young' para aquisitar o ultrasonico young\n")



while True: #Loop para a conexão com o Arduino
    try:  #Tenta se conectar, se conseguir, o loop se encerra
        arduino = serial.Serial('COM3', 115200)
        print('Aguarde...')
        time.sleep(10)
        print('Tunel conectado!')
        break
    except:
        pass

    
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

    if( cmd == 'druck2'):    #Função para ler o druck
        druck2()

    if( cmd == 'young'):    #Função para ler o druck
        young()

    if(cmd == 'aqr'):
        druck()
        threading.Thread(target=PA16).start()
        threading.Thread(target=temp).start()
       
        
    if(cmd == 'pulsos'):
        ni()

    if( cmd == 'pa'):    #Função para ler o druck
        PA16()

    if( cmd == 'temp'):    #Função para ler o druck
        temp()

    if( cmd == 'copos2'):  #Calibração de Copos - mA   
        try:
            os.remove('C:/Users/guilhermeas/Desktop/calibracao.xlsx')
        except OSError as e:
            print(f"Error:{ e.strerror}\n")
        padraom = []
        padraos = []
        padraom2 = []
        padraos2 = []  
        pressao = []
        jato = []
        seco = []
        umido = []
        liga = 'run'
        arduino.write(liga.encode())
        arduino.flush() #Limpa a comunicação
        print('Iniciando Calibração')
        time.sleep(3)
        
        for i in range(1,len(rampa2)):   #Loop de troca de rotação e aquisição
            print("\nRealizando ponto:" + str(i))
            print('Ajustando velocidade...')
            arduino.write(str(round(rampa2[i])).encode())
            arduino.flush() #Limpa a comunicação
            time.sleep(15)
            print('Estabilizando...')
            print('Medindo Ambiente')
            time.sleep(15)
            print('Medindo Padrão...')
            threading.Thread(target=druck2).start()
            PA16()
            temp()
            druck()
            
            df = pd.DataFrame((zip(padraom, padraos,jato,seco,umido,pressao,padraom2,padraos2)), columns = ['mA', 'Desvio(mA)','Jato','Seco','Umido','Pressão(kPa)','mA2', 'Desvio(mA2)'])

            for coluna in variave2l:

                df[coluna]     = df[coluna].astype(str)
                df[coluna]      = df[coluna].str.replace('.',',')
    
            else:
                df.to_excel('C:/Users/guilhermeas/Desktop/calibracao.xlsx', index = False)
                print(df)
                time.sleep(2)
        else:
            print('\nCalibração Finalizada\n')
            rpmmin = 0
            arduino.write(str(rpmmin).encode())
            arduino.flush() #Limpa a comunicação
            


    if (cmd.isdigit()):     #Função para enviar rotação(valor numerico)
        value = int(cmd)
        value = (value/1683)*4095
        print('Rotação enviada!')
        print(round(value,0))
        arduino.write(str(round(value,0)).encode())
        arduino.flush() #Limpa a comunicação
        

    if( cmd == 'copos'):        # Calibração de Copos - Pulsos
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
            time.sleep(1)
            df = pd.DataFrame((zip(padraom, padraos,jato,seco,umido,pressao,pulsosm,pulsoss)), columns = ['mA', 'Desvio(mA)','Jato','Seco','Umido','Pressão(kPa)','Pulsos','Desvio(Pulsos)'])
            for coluna in variavel:

                df[coluna]     = df[coluna].astype(str)
                df[coluna]     = df[coluna].str.replace('.',',')
    
            else:
                df.to_excel('C:/Users/guilhermeas/Desktop/calibracao.xlsx', index = False)
                print(df)
                time.sleep(2)
        else:
            print('\nCalibração Finalizada\n')
            rpmmin = 0
            arduino.write(str(rpmmin).encode())
            arduino.flush() #Limpa a comunicação

            
