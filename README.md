# Sistema de monitoramento do ambiente - Fiware
<h2>Visão Geral do Projeto</h2>
Este projeto implementa um sistema de monitoramento de ambiente usando um ESP32 conectado a sensores de temperatura, umidade (DHT22) e luminosidade (LDR). Esses sensores monitoram as condições ambientais em tempo real e transmitem os dados via MQTT para uma plataforma FIWARE hospedada na nuvem. A plataforma FIWARE é responsável por gerenciar o fluxo de dados entre os sensores e os dashboards que exibem os dados.

<h2>Componentes do Sistema</h2>
<h3>Hardware</h3>
<img src="https://i.imgur.com/WSbIYba.png"/>

* DHT22: Sensor responsável por capturar dados de temperatura e umidade.
* LDR: Sensor de luminosidade que monitora a intensidade de luz ambiente.
* ESP32 Devkit V1: Controlador que coleta dados dos sensores e os transmite via MQTT para o broker Mosquitto.
* Breadboard (opcional): Para uma conexão menos concentrada dos sensores com o ESP32.

<h3>Software</h3>
O núcleo do projeto está hospedado em uma máquina virtual no Microsoft Azure, e utiliza a plataforma FIWARE, especificamente uma versão modificada chamada FIWARE Descomplicado, criada pelo professor Fábio Henrique Cabrini e sua equipe. Esta plataforma facilita a integração e gerenciamento de dispositivos IoT em um ambiente FIWARE, utilizando vários serviços contidos em diferentes contêineres Docker.
<p>Segue link da documentação detalhada da versão do Fiware utilizada:</p>
<p>https://github.com/fabiocabrini/fiware</p>
GitHub do criador (Fábio Henrique Cabrini):
<p>https://github.com/fabiocabrini/</p>
O projeto utiliza Docker e Docker Compose para gerenciar e orquestrar os serviços da plataforma FIWARE. O Docker permite a contêinerização dos aplicativos, garantindo que funcionem de forma consistente em diferentes ambientes. O Docker Compose simplifica o gerenciamento de múltiplos contêineres, permitindo que todos os serviços sejam definidos e executados a partir de um único arquivo de configuração.
os contêiners Docker inicializados através do Docker Compose são:

<h4>Iot Agent MQTT</h4>

Este contêiner atua como o intermediário entre o protocolo MQTT, utilizado pelos dispositivos IoT, e o formato NGSI. Ele converte as mensagens publicadas no broker MQTT em dados compatíveis com o Orion Context Broker, integrando os dados IoT no ambiente FIWARE.

<h4>Orion Context Broker</h4>

O contêiner do Orion gerencia todo o ciclo de vida das entidades no sistema, como o ESP32 e os sensores. Ele recebe atualizações em tempo real via NGSI, permitindo consultar e monitorar os dados dos sensores de forma instantânea. A comunicação com o MongoDB e o IoT Agent também é gerida por esse contêiner.

<h4>STH-Comet</h4>

O contêiner STH-Comet armazena dados históricos das entidades, permitindo a consulta de séries temporais das leituras dos sensores. Toda vez que os dados de um sensor são atualizados no Orion, o STH-Comet é notificado e armazena essas alterações no MongoDB.

<h4>MongoDb</h4>

MongoDB é o banco de dados utilizado pelo Orion Context Broker e pelo STH-Comet. Ele armazena tanto o estado atual das entidades (por exemplo, as leituras atuais dos sensores) quanto o histórico de todas as mudanças dos atributos, tornando os dados disponíveis para consulta posterior.

<h4>Mosquito + Broker MQTT</h4>
O contêiner Broker MQTT recebe as mensagens publicadas pelos sensores do ESP32. Ele gerencia a comunicação entre os dispositivos IoT e o IoT Agent MQTT, permitindo que os dados sejam transmitidos de forma eficiente no sistema.

<h4>Vamos ver um esquema do processo de envio/recebimento dos dados</h4>

### Esquema geral do fluxo

    ESP32 (sensores) ---> Mosquitto (MQTT Broker) --->  IoT Agent (MQTT to NGSI) ---> Orion Context Broker (Dados em tempo real)    
                                                                                   |
                                                                           STH-Comet (Dados históricos / recebe notificações)
                                                                                   |
                                                                                 MongoDB

<h3>Inicializando o projeto</h3>

O servidor utilizado para funcionamento da plataforma já está corretamente configurado pela nossa equipe, restando como tarefa para o usuário apenas a configuração do dispositivo, você sempre pode fazer um Health Check do servidor através da Collection do Postman, ou contatar a nossa equipe para verificar a integridade do servidor

<h4> Requisitos: </h4>

<h4>Postman</h4>
Para inicializar o projeto abra a Collection do postman no navegador de sua preferência ou pelo aplicativo Postman, dentro, primeiro é preciso executar as requisições 2, 3 e 4 da pasta Iot Agent MQTT, isto irá provisionar um grupo de serviço para o MQTT, um monitor de ambiente e registrar os comandos do monitor de ambiente (para ligar e desligar o Led OnBoard do ESP32), depois, para garantir a obtenção dos dados históricos, executar a requisição 2 da pasta STH-Comet

<h4>Wokwi</h4>

depois de ter configurado o dispositivo no Postman depois apenas basta inicializar o simulador Wokwi que os dados já deverão estar disponíveis para obtenção.
<p>Segue link do simulador Wokwi: https://wokwi.com/projects/411382500948043777</p>

<h4>Dashboard</h4>
O dashboard feito com <a href="https://dash.plotly.com/">Dash</a> exibe dados de luminosidade, temperatura e umidade de uma API usando STH-Comet. Ele faz requisições periódicas a cada 10 segundos para recuperar os dados mais recentes e os converte para o fuso horário de Lisboa. As informações são apresentadas em três gráficos interativos: um para cada tipo de dado. O código utiliza a biblioteca Plotly para criar os gráficos, e a lógica de atualização é gerenciada por callbacks, permitindo que os dados sejam atualizados automaticamente conforme chegam ao sistema.
Você pode acessar o dashboard depois de ter feito os passos anteriores.  

<p>Segue link do dashboard: http://20.206.249.58:8051/</p>

<h3>Vídeo explicativo</h3>
Você pode observar todo o processo visualmente além de ter uma explicação a mais sobre o projeto no vídeo feito por nós no Youtube a seguir:
<p>https://www.youtube.com/watch?v=M-Qa6xwlGOk</p>

<h4>Considerações Finais:</h4>

O sistema de monitoramento ambiental com FIWARE permite a coleta, o processamento e a visualização de dados em tempo real de maneira robusta e eficiente. O projeto foi desenvolvido pela equipe MindSync sob orientação do professor Fábio Henrique Cabrini. Para mais informações ou dúvidas, consulte a documentação ou entre em contato com a equipe.






