import json
import requests 
from zipfile import ZipFile
import urllib.request
import threading
import thingspeak
import time
#gauge
from tkinter import * # Import toate modulele
import tk_tools
#histograma
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import tkinter 
from tkinter import * 
from PIL import Image, ImageTk 
root = Tk() #window
root.geometry("680x1000+350+0")
map_medie={0:0,}
vect_an=[]
vect_medie=[]
lista_judete = ['Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud', 'Botoșani', 'Brăila', 'Brașov', 'Bucharest', 'Călărași', 'Caraș-Severin', 'Cluj',
                'Constanșa', 'Dâmbovița', 'Dolj', 'Giurgiu', 'Harghita', 'Hunedoara', 'Iași', 'Ilfov', 'Maramureș', 'Mureș', 'Olt',
                'Satu Mare', 'Sibiu', 'Suceava', 'Timiș', 'Tulcea', 'Vâlcea', 'Vaslui', 'Vrancea']
lista_orase = ['Campulung', 'Dobresti', 'Pitesti', 'Tigveni', 'Bacau', 'Margineni', 'Auseu', 'Oradea', 'Prundu Bargaului', 'Botosani', 'Trusesti',
               'Chiscani', 'Tichilesti', 'Beclean', 'Brasov', 'Municipiul Bucuresti', 'Tamadau Mare', 'Moldova Noua', 'Resita', 'Cluj-napoca',
               'Constanta', 'Mereni', 'Aninoasa', 'Mogosani', 'Malu Mare', 'Calugareni', 'Miercurea Ciuc', 'Hunedoara', 'Belcesti', 'Dobrovat',
               'Iasi', 'Miroslava', 'Rediu', 'Chiajna', 'Popesti Leordeni', 'Baia Sprie', 'Bogdan Voda', 'Ocna Sugatag', 'Bgaciu', 'Ganesti',
               'Targu Mures', 'Slatina', 'Ploiesti', 'Bixad', 'Cisnadie', 'Medias', 'Sibiu', 'Crucea', 'Dolhasca', 'Moara Nica', 'Ghiroda',
               'Sanandrei', 'Timisoara', 'Tulcea', 'Brezoi', 'Galicea', 'Lalosu', 'Ramnicu Valcea', 'Vaslui', 'Zorleni', 'Adjud','Dej' ]
#JUDET
judet_ok=True
judet = input('Introduceti un judet: ')
while(judet_ok):
    if judet in lista_judete:
        print('Judetul e bun')
        break
    else:
        judet = input('Introduceti alt judet: ')
        continue
#ORAS
oras_ok=True
oras = input('Introduceti un oras: ')
while(oras_ok):
    if oras in lista_orase:
        print('Orasul e bun')
        break
    else:
        oras = input('Introduceti alt oras: ')
        continue
r = requests.get('https://data.noise-planet.org/noisecapture/Romania.zip') #link-ul zip-ului; il descarca
file_name = "Romania.zip" #se deschide zip-ul
#se deschide zip-ul in modul citire
with ZipFile(file_name, 'r') as zip:
    zip.extractall(); #se extrag toate fisierele din acel zip
new_cmp = [] #se vor pune anii 

#afisare imagine 
image1 = Image.open("D:/Python/noise.png")
test = ImageTk.PhotoImage(image1)
label1 = tkinter.Label(image=test)
label1.place(x=0, y=240)

#try
try:
    with open('D:\Python\Romania_' + str(judet) +'_' + str(oras)+ '.points.geojson', 'r') as f:
        data = json.load(f) 
        lungime = len(data["features"])
        print("Numarul de inregistrari este: " + str(lungime))
        #trimite date in thingspeak
        URl='https://api.thingspeak.com/update?api_key=BPNVQXVOY2XT3GZQ&field1=0'
        KEY='BPNVQXVOY2XT3GZQ'
        gauge = tk_tools.Gauge(root, 400, 235, max_value=120.0,
                       label='noise level', unit='dB') 
        print("Sunt extrase si trimise spre Thingspeak 4 inregistrari\n")
        def thingspeak_post(n):
           for i in range(0, n):
               noise=data["features"][i]["properties"]["noise_level"]
               latitudine = data["features"][i]["geometry"]["coordinates"][0]
               longitudine = data["features"][i]["geometry"]["coordinates"][1]
               altitudine = data["features"][i]["geometry"]["coordinates"][2]
               HEADER='&field1={}&field2={}&field3={}&field4={}'.format(noise, latitudine, longitudine, altitudine)   
               NEW_URL = URl+KEY+HEADER
               #print(NEW_URL)
               data1=urllib.request.urlopen(NEW_URL)
               print("Noise: " + str(noise))
               print("Latitudine: " +str(latitudine))
               print("Longitudine: " +str(longitudine))
               print("Altitudine: " +str(altitudine))
               print('\n')
               gauge.set_value(noise)
               gauge.pack(side = TOP)
               time.sleep(20)
        x = threading.Thread(target = thingspeak_post, args = (4,))
        x.start()
        cmp = -1;
        for i in range(0, lungime):
            #altitudine = data["features"][i]["geometry"]["coordinates"][2]
            an = data["features"][i]["properties"]["time_ISO8601"][0:4]
            if cmp==an:
                continue
            else:
                cmp=an 
                if cmp not in new_cmp: 
                    new_cmp.append(cmp)
        print("Anii sunt: ")
        print(new_cmp)        
        print("\n")
        #parcurgem anii gasiti in fisier
        for an_cmp in new_cmp:
            media=0;
            suma=0
            nr_elm=0
            for j in range(0, lungime):
              an = data["features"][j]["properties"]["time_ISO8601"][0:4]
              noise=data["features"][j]["properties"]["noise_level"]
              if an_cmp== an:
                  suma+=noise
                  nr_elm+=1;
            media=suma/nr_elm
            map_medie[an_cmp]=media
            vect_medie.append(media)
            vect_an.append(an_cmp)
    map_medie.pop(0);
    print("\nMedia de zgomot pe ani este: ")
    print(map_medie)
    print("\n")
    #plot
    for x in range(0,len(vect_an)-1):
        for y in range(x,len(vect_an)):
            if vect_an[x]>vect_an[y]:
                aux=vect_an[x]
                vect_an[x]=vect_an[y]
                vect_an[y]=aux
                aux1=vect_medie[x]
                vect_medie[x]=vect_medie[y]
                vect_medie[y]=aux1
    plt.bar(vect_an,vect_medie,align='center') # bar chart
    plt.xlabel('An')
    plt.ylabel('Noise level')
    plt.show()
    root.mainloop()
except IOError:
    print('Nu s-a putut deschide fisierul/Fisier inexistent')   





 
       
  
