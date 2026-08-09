# smart-city-iot-airguard
# AirGuard IoT

Sistema IoT de monitoramento ambiental desenvolvido com **ESP32**, **MicroPython**, **MQTT** e **Node-RED**.

O AirGuard realiza a leitura de temperatura, umidade e qualidade do ar, processa os dados localmente no ESP32 e classifica as condições do ambiente em diferentes níveis de status. As informações são transmitidas via MQTT e apresentadas em um dashboard desenvolvido no Node-RED.

---

## 📌 Sobre o projeto

O projeto foi desenvolvido como uma solução de monitoramento para um cenário de **Smart Cities**, utilizando sensores conectados a um ESP32 para coletar informações ambientais.

O dispositivo realiza o processamento das leituras e fornece feedback local através de um display LCD, LEDs e buzzer. Paralelamente, os dados são publicados via MQTT para um fluxo no Node-RED, permitindo seu acompanhamento através de um dashboard.

---

## ⚙️ Funcionalidades

- Monitoramento de temperatura
- Monitoramento de umidade
- Monitoramento da qualidade do ar
- Classificação do ambiente em diferentes níveis de status
- Exibição das informações em LCD 16x2
- Indicação visual através de LED RGB
- Alerta sonoro em situações críticas
- Conexão do ESP32 à rede Wi-Fi
- Comunicação utilizando o protocolo MQTT
- Visualização dos dados através do Node-RED

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| **ESP32** | Microcontrolador do sistema |
| **MicroPython** | Desenvolvimento do software embarcado |
| **Wokwi** | Simulação do circuito |
| **DHT22** | Medição de temperatura e umidade |
| **Sensor de gás** | Leitura utilizada para estimar a qualidade do ar |
| **LCD 16x2** | Exibição local das informações |
| **LED RGB** | Indicação visual do status |
| **Buzzer** | Alerta sonoro |
| **MQTT** | Comunicação entre o ESP32 e o sistema de monitoramento |
| **HiveMQ** | Broker MQTT |
| **Node-RED** | Processamento e visualização dos dados |

---

## 🏗️ Arquitetura

```text
                 ┌─────────────────────┐
                 │        ESP32        │
                 │     MicroPython     │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
          DHT22        Sensor de gás    Interface
             │              │          local
             │              │       ┌────┼────┐
             │              │       │    │    │
             │              │      LCD  LED  Buzzer
             └──────────────┴──────────┬──────┘
                                      │
                                    Wi-Fi
                                      │
                                      ▼
                              ┌───────────────┐
                              │ MQTT / HiveMQ │
                              └───────┬───────┘
                                      │
                                      ▼
                               ┌─────────────┐
                               │  Node-RED   │
                               └──────┬──────┘
                                      │
                                      ▼
                                 Dashboard