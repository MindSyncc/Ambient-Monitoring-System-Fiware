# Sistema de monitoramento do ambiente - Fiware
<h2>Visão Geral do Projeto</h2>
Este projeto implementa um sistema de monitoramento de ambiente usando um ESP32 conectado a sensores de temperatura, umidade (DHT22) e luminosidade (LDR). Esses sensores monitoram as condições ambientais em tempo real e transmitem os dados via MQTT para uma plataforma FIWARE hospedada na nuvem. A plataforma FIWARE é responsável por gerenciar o fluxo de dados entre os sensores e os dashboards que exibem os dados.

<h2>Componentes do Sistema</h2>
<h3>Hardware</h3>

* DHT22: Sensor responsável por capturar dados de temperatura e umidade.
* LDR: Sensor de luminosidade que monitora a intensidade de luz ambiente.
* ESP32 Devkit V1: Controlador que coleta dados dos sensores e os transmite via MQTT para o broker Mosquitto.
* Breadboard (opcional): Para uma conexão menos concentrada dos sensores com o ESP32.

<h3>Software</h3>
O software do projeto executa-se em uma máquina virtual do Microsoft Azure, e é orquestrado pela plataforma Fiware, mais especificamente, uma versão modificada do Fiware, o Fiware Descomplicado, elaborada pelo nosso Professor Fábio Henrique Cabrini e sua equipe, segue link da documentação detalhada da versão do Fiware utilizada:
<p>https://github.com/fabiocabrini/fiware</p>
GitHub do criador (Fábio Henrique Cabrini):
<p>https://github.com/fabiocabrini/</p>
os contêiners Docker inicializados através do Docker Compose são os responsáveis pela execução da plataforma através dos contêiners, estes são:

<h4>Iot Agent MQTT</h4>

Este contêiner atua como o intermediário entre o protocolo MQTT, utilizado pelos dispositivos IoT, e o formato NGSI. Ele converte as mensagens publicadas no broker MQTT em dados compatíveis com o Orion Context Broker, integrando os dados IoT no ambiente FIWARE.

<h4>Orion Context Broker</h4>

O contêiner do Orion gerencia todo o ciclo de vida das entidades no sistema, como o ESP32 e os sensores. Ele recebe atualizações em tempo real via NGSI, permitindo consultar e monitorar os dados dos sensores de forma instantânea. A comunicação com o MongoDB e o IoT Agent também é gerida por esse contêiner.

<h4>STH-Comet</h4>

O contêiner STH-Comet armazena dados históricos das entidades, permitindo a consulta de séries temporais das leituras dos sensores. Toda vez que os dados de um sensor são atualizados no Orion, o STH-Comet é notificado e armazena essas alterações no MongoDB.

<h4>Mongo Db</h4>

MongoDB é o banco de dados utilizado pelo Orion Context Broker e pelo STH-Comet. Ele armazena tanto o estado atual das entidades (por exemplo, as leituras atuais dos sensores) quanto o histórico de todas as mudanças dos atributos, tornando os dados disponíveis para consulta posterior.

<h4>Mosquito + Broker MQTT</h4>
O contêiner Broker MQTT recebe as mensagens publicadas pelos sensores do ESP32. Ele gerencia a comunicação entre os dispositivos IoT e o IoT Agent MQTT, permitindo que os dados sejam transmitidos de forma eficiente no sistema.

<h4>Vamos ver um esquema do processo de envio/recebimento dos dados</h4>
Esquema geral do fluxo

    ESP32 (sensores) ---> Mosquitto (MQTT Broker) --->  IoT Agent (MQTT to NGSI) ---> Orion Context Broker (Dados em tempo real)    
                                                                                   |
                                                                           STH-Comet (Dados históricos / recebe notificações)
                                                                                   |
                                                                                 MongoDB

<img src=''>




