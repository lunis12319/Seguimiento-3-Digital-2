from machine import Pin, ADC, Timer
import time

# CONFIGURACIÓN ADC 
sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)
sensor.width(ADC.WIDTH_12BIT)

led = Pin(2, Pin.OUT)

# VARIABLES 
Fs = 50
Ts = int(1000 / Fs)

ultima_lectura = 0
temperatura = 0
filtrado = 0

# Control del sistema
activo = True

# Filtros
usar_promedio = False
usar_mediana = False
usar_exponencial = False

lecturas = []
N = 5
alpha = 0.1
y_exp = 0  

# Archivo
archivo = open("datos.txt", "w")
archivo.write("Temperatura;Filtrada\n")

# FILTROS 

def promedio_movil(x):
    lecturas.append(x)
    if len(lecturas) > N:
        lecturas.pop(0)
    return sum(lecturas) / len(lecturas)

def filtro_mediana(x):
    temp = lecturas + [x]
    temp.sort()
    return temp[len(temp)//2]

def filtro_exponencial(x):
    global y_exp
    y_exp = alpha * x + (1 - alpha) * y_exp
    return y_exp

def aplicar_filtros(x):
    y = x
    
    if usar_promedio:
        y = promedio_movil(y)
    
    if usar_mediana:
        y = filtro_mediana(y)
    
    if usar_exponencial:
        y = filtro_exponencial(y)
    
    return y

# CONFIGURACIÓN

print("\n--- CONFIGURACIÓN ---")

Fs = int(input("Frecuencia de muestreo (Hz): "))
Ts = int(1000 / Fs)

print("\nSeleccione filtros:")
print("1: Promedio")
print("2: Mediana")
print("3: Exponencial")
print("4: Promedio + Mediana")
print("5: Promedio + Exponencial")
print("6: Mediana + Exponencial")
print("7: Todos")
print("0: Ninguno")

opcion = int(input("Opción: "))

if opcion == 1:
    usar_promedio = True
elif opcion == 2:
    usar_mediana = True
elif opcion == 3:
    usar_exponencial = True
elif opcion == 4:
    usar_promedio = True
    usar_mediana = True
elif opcion == 5:
    usar_promedio = True
    usar_exponencial = True
elif opcion == 6:
    usar_mediana = True
    usar_exponencial = True
elif opcion == 7:
    usar_promedio = True
    usar_mediana = True
    usar_exponencial = True

# TIMER

def muestrear(t):
    global ultima_lectura, temperatura, filtrado, activo, y_exp
    
    if not activo:
        return
    
    try:
        ultima_lectura = sensor.read()
        
        voltaje = ultima_lectura * (3.3 / 4095)
        temperatura = voltaje * 100


        if y_exp == 0:
            y_exp = temperatura
        
        filtrado = aplicar_filtros(temperatura)
        
        print("Temp:", round(temperatura,2), "Filtrada:", round(filtrado,2))
        
        
        linea = "{:.2f};{:.2f}\n".format(temperatura, filtrado)
        linea = linea.replace('.', ',')
        
        archivo.write(linea)
    
    except:
        pass

# INICIO 

led.value(1)

timer = Timer(0)
timer.init(period=Ts, mode=Timer.PERIODIC, callback=muestrear)

print("Sistema iniciado... Ctrl+C para detener")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Deteniendo sistema...")
    
    activo = False
    timer.deinit()
    time.sleep(0.1)
    
    archivo.close()
    
    led.value(0)
    
    print("Datos guardados correctamente")