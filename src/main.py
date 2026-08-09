from machine import Pin, ADC, PWM, SoftI2C
from dht import DHT22
from time import sleep

# WIFI

from umqtt.simple import MQTTClient
import network
import ssl  # Necessário para habilitar a conexão segura (SSL/TLS)


# LCD 16x2 I2C — Driver embutido


class LCD16x2:
    """Driver minimalista para LCD 16x2 com módulo I2C PCF8574."""

    # Flags de controle do LCD
    LCD_CHR = 1  # Modo: dados
    LCD_CMD = 0  # Modo: comando

    LCD_BACKLIGHT = 0x08  # Backlight ligado
    ENABLE = 0b00000100   # Bit de Enable

    def __init__(self, i2c, addr=0x27, cols=16, rows=2): # executado ao criar o LCD, guarda as configurações e inicia o display
        self.i2c = i2c
        self.addr = addr
        self.cols = cols
        self.rows = rows
        self._init()

    def _write_byte(self, data): # envia um byte bruto pelo I2C para o LCD
        self.i2c.writeto(self.addr, bytes([data]))

    def _strobe(self, data): # dá um pulso no pino Enable para o LCD confirmar que recebeu o dado
        self._write_byte(data | self.ENABLE | self.LCD_BACKLIGHT)
        sleep(0.0005)
        self._write_byte((data & ~self.ENABLE) | self.LCD_BACKLIGHT)
        sleep(0.0001)

    def _write4bits(self, data): # envia apenas 4 bits de uma vez, que é o modo que esse LCD usa
        self._write_byte(data | self.LCD_BACKLIGHT)
        self._strobe(data)

    def _send(self, data, mode): # envia um byte completo em duas metades de 4 bits, mode indica se é comando ou caractere
        high = mode | (data & 0xF0) | self.LCD_BACKLIGHT
        low  = mode | ((data << 4) & 0xF0) | self.LCD_BACKLIGHT
        self._write_byte(high)
        self._strobe(high)
        self._write_byte(low)
        self._strobe(low)

    def _init(self): # sequência obrigatória de inicialização do LCD ao ligar, definida pelo fabricante
        sleep(0.05)
        self._write4bits(0x30)
        sleep(0.005)
        self._write4bits(0x30)
        sleep(0.001)
        self._write4bits(0x30)
        sleep(0.001)
        self._write4bits(0x20)  # Modo 4 bits
        sleep(0.001)
        self._send(0x28, self.LCD_CMD)  # 2 linhas, 5x8 dots
        self._send(0x0C, self.LCD_CMD)  # Display on, cursor off
        self._send(0x06, self.LCD_CMD)  # Incremento automático
        self.clear()

    def clear(self): # apaga tudo que está escrito na tela
        self._send(0x01, self.LCD_CMD)
        sleep(0.002)

    def set_cursor(self, col, row): # move o cursor para a coluna e linha indicadas antes de escrever
        row_offsets = [0x00, 0x40]
        self._send(0x80 | (col + row_offsets[row]), self.LCD_CMD)

    def print(self, text): # escreve um texto no LCD caractere por caractere a partir da posição atual do cursor
        for char in text:
            self._send(ord(char), self.LCD_CHR)

    def print_line(self, text, row, fill=True): # escreve uma linha inteira no LCD, completando com espaços para apagar o texto anterior
        """Imprime texto em uma linha, preenchendo com espaços se fill=True."""
        self.set_cursor(0, row)
        text = text[:self.cols]
        if fill:
            while len(text) < self.cols:
                text = text + " "
        self.print(text)



# I2C e LCD

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)

# Detecta automaticamente o endereço do LCD (0x27 ou 0x3F são os mais comuns)
devices = i2c.scan()
lcd_addr = 0x27  # padrão; ajuste para 0x3F se necessário
if devices:
    lcd_addr = devices[0]
    print(f"LCD encontrado no endereço: {hex(lcd_addr)}")
else:
    print("Aviso: nenhum dispositivo I2C detectado")

lcd = LCD16x2(i2c, addr=lcd_addr)

def lcd_show(linha1, linha2=""):
    """Atualiza as duas linhas do LCD com segurança."""
    lcd.print_line(linha1[:16], row=0)
    lcd.print_line(linha2[:16], row=1)


# SENSORES


dht = DHT22(Pin(15))

mq135 = ADC(Pin(34))
mq135.atten(ADC.ATTN_11DB)


# LEDS

led_vermelho = Pin(14, Pin.OUT)
led_verde    = Pin(12, Pin.OUT)
led_azul     = Pin(13, Pin.OUT)


# BUZZER


buzzer = PWM(Pin(23))
buzzer.duty(0)


# FUNÇÕES LED


def apagar_leds():
    led_vermelho.off()
    led_verde.off()
    led_azul.off()

def verde():
    apagar_leds()
    led_verde.on()

def amarelo():
    apagar_leds()
    led_vermelho.on()
    led_verde.on()

def vermelho():
    apagar_leds()
    led_vermelho.on()


# BUZZER


def buzzer_on():
    buzzer.freq(1000)
    buzzer.duty(512)

def buzzer_off():
    buzzer.duty(0)


# WIFI


wifi = network.WLAN(network.STA_IF)
wifi.active(True)

print("Conectando ao WiFi...")
lcd_show("Conectando", "ao WiFi...")

wifi.connect("Wokwi-GUEST", "")

while not wifi.isconnected():
    sleep(1)

print("WiFi conectado!")
print(wifi.ifconfig())
lcd_show("WiFi OK!", wifi.ifconfig()[0][:16])
sleep(2)


# MQTT


MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883

client = MQTTClient(
    client_id="airguard-esp32-WOKWI-SIMULADOR",
    server=MQTT_BROKER,
    port=MQTT_PORT
)

print("Conectando ao broker...")
lcd_show("Conectando", "MQTT broker...")

client.connect()
print("MQTT conectado com sucesso!")
lcd_show("MQTT OK!", "AirGuard pronto")
sleep(2)

# CHAVE SECRETA
CHAVE_SECRETA_PROJETO = "SEU_TOPICO_AQUI" #Escreve seu tópico para enviar ao Broker MQTT, depois configurar no node-red

TOPICO_TEMP   = f"{CHAVE_SECRETA_PROJETO}/temperatura"
TOPICO_UMID   = f"{CHAVE_SECRETA_PROJETO}/umidade"
TOPICO_AR     = f"{CHAVE_SECRETA_PROJETO}/qualidade_ar"
TOPICO_STATUS = f"{CHAVE_SECRETA_PROJETO}/status"


# LOOP PRINCIPAL


print("AirGuard iniciado")

# Contador para alternar entre telas no LCD
tela = 0

while True:

    try:
        dht.measure()

        temperatura = dht.temperature()
        umidade     = dht.humidity()

        adc = mq135.read()
        ppm = int((adc / 4095) * 5000)

        
        # LÓGICA DO SISTEMA
        

        if ppm < 1400 and temperatura < 30:
            status = "AR BOM"
            verde()
            buzzer_off()

        elif ppm < 3000 and temperatura < 35:
            status = "ATENCAO"
            amarelo()
            buzzer_off()

        else:
            status = "CRITICO"
            vermelho()
            buzzer_on()

        
        # LCD — alterna entre 2 telas
       
        # Tela 0: Temperatura e Umidade
        # Tela 1: PPM e Status

        if tela == 0:
            linha1 = f"Temp: {temperatura:.1f}C"
            linha2 = f"Umid: {umidade:.1f}%"
            lcd_show(linha1, linha2)
        else:
            linha1 = f"Ar: {ppm} ppm"
            linha2 = f"Status:{status}"
            lcd_show(linha1, linha2)

        tela = (tela + 1) % 2  # Alterna entre 0 e 1

       
        # PUBLICAR NA NUVEM
        
        client.publish(TOPICO_TEMP,   str(temperatura))
        client.publish(TOPICO_UMID,   str(umidade))
        client.publish(TOPICO_AR,     str(ppm))
        client.publish(TOPICO_STATUS, status)

        
        # SAÍDA SERIAL
        
        print("-------------------")
        print("Temp:", temperatura)
        print("Umid:", umidade)
        print("Ar:",   ppm)
        print("Status:", status)

        sleep(5)

    except Exception as erro:
        print("Erro:", erro)
        lcd_show("ERRO!", str(erro)[:16])
        sleep(5)