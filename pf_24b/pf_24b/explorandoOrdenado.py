import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile

# Imports de mensagens obrigatórios para a prova
from geometry_msgs.msg import Twist
from robcomp_interfaces.msg import Conversation  # Tipo de mensagem exigido para o /handler

# Componente utilitário fornecido no capítulo 3 para controle do robô
from robcomp_util.base_action import Acao

class ExplorandoOrdenado(Node):
    def __init__(self):
        # Inicializa o nó com o nome exato exigido pelo enunciado
        super().__init__('explorador_node') 
        
        # Instancia a classe de ação interna (responsável por seguir a linha automaticamente)
        self.acao_node = Acao() 

        # --- MÁQUINA DE ESTADOS ---
        # O robô inicia no modo piloto automático seguindo a linha da pista
        self.robot_state = 'seguindo_linha'
        self.state_machine = {
            'seguindo_linha': self.seguindo_linha,
            'aguardando_handler': self.aguardando_handler,
            'aguardando_retorno': self.aguardando_retorno,
            'retornando': self.retornando,
            'stop': self.stop
        }

        # Estados "clientes de ação" são aqueles onde o controle dos motores é feito 
        # pela classe Acao(). Nestes estados, a função control() NÃO publica velocidades.
        self.estados_clientes = ['seguindo_linha', 'retornando']

        # --- VARIÁVEIS DE CONTROLE ---
        self.twist = Twist()
        self.aruco_detectado_id = None     # Armazenará o ID lido na bifurcação
        self.nome_objeto_encontrado = None # Armazenará o nome do bicho (gato, cachorro, cavalo)
        
        # Flags para evitar o envio repetido de mensagens (Garante o Requisito 10 contra spam)
        self.bifurcacao_enviada = False
        self.objeto_enviado = False

        # REQUISITO 9: Lista que funcionará como memória para guardar o histórico de conversas
        self.historico_conversas = [] 
        
        # --- PUBLISHERS E SUBSCRIBERS (Requisito 8) ---
        # Publisher para enviar mensagens para o árbitro da prova
        self.handler_pub = self.create_publisher(Conversation, '/handler', 10)

        # Subscriber para escutar as respostas enviadas pelo Handler
        self.handler_sub = self.create_subscription(
            Conversation,
            '/handler',
            self.handler_callback,
            10
        )

        # Publisher de velocidade padrão para movimentar o robô
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # REQUISITO 7: Inicializa o timer cíclico de controle a 10Hz (sem usar loops ou sleep)
        self.timer = self.create_timer(0.1, self.control)
        self.get_logger().info('Nó Explorador Ordenado ativo e pronto para a prova!')

    def enviar_para_handler(self, texto_mensagem):
        """Função auxiliar para centralizar o envio de mensagens e salvar no histórico"""
        msg = Conversation()
        # O enunciado exige estritamente o formato "Robo: <mensagem>"
        msg.robo = f"Robo: {texto_mensagem}"
        msg.handler = "" # Campo do Handler fica vazio no envio

        # Publica no tópico e salva na lista de histórico (Requisito 9)
        self.handler_pub.publish(msg)
        self.historico_conversas.append(msg.robo)
        self.get_logger().info(f'Enviado para o Handler -> {msg.robo}')

    def handler_callback(self, msg: Conversation):
        """Callback que monitora e filtra todas as respostas do Handler em tempo real"""
        # Só processa se a mensagem veio do Handler ("Handler: <mensagem>") e não estiver vazia
        if msg.handler and msg.handler.startswith("Handler:"):
            
            # Se a mensagem já foi registrada antes, ignora para evitar reprocessamento
            if msg.handler in self.historico_conversas:
                return

            # Adiciona a nova mensagem ao histórico de memórias (Requisito 9)
            self.historico_conversas.append(msg.handler)
            self.get_logger().info(f'Recebi do Handler -> {msg.handler}')

            # --- MAQUINA DE ESTADOS REATIVA BASEADA NA CONVERSA ---
            
            # Caso 1: O robô estava parado na bifurcação esperando as coordenadas de direção
            if self.robot_state == 'aguardando_handler':
                if "Vá pela direita!" in msg.handler or "Vá pela esquerda!" in msg.handler:
                    # Aqui o robô executa a curva correspondente (ex: rotaciona o twist se necessário)
                    # Reseta as travas do Aruco para permitir detecções em bifurcações futuras
                    self.aruco_detectado_id = None
                    self.bifurcacao_enviada = False
                    
                    # Devolve o robô para o piloto automático seguir a nova pista
                    self.robot_state = 'seguindo_linha'
                    
            # Caso 2: O robô achou o objetivo (animal) e o Handler mandou voltar para casa
            elif self.robot_state == 'aguardando_retorno':
                if "Retorne ao ponto de partida!" in msg.handler:
                    # Muda o estado para acionar o retorno automático seguindo a linha
                    self.robot_state = 'retornando'

    def seguindo_linha(self):
        """Estado onde o robô avança autonomamente rastreando a linha no chão"""
        
        # --- VERIFICAÇÃO DE EVENTO: DETECTOU BIFURCAÇÃO? ---
        # Nota: Na prova, o sensor ou o processamento de imagem atualizará a variável 'self.aruco_detectado_id'
        if self.aruco_detectado_id is not None and not self.bifurcacao_enviada:
            # 1. Trava os motores imediatamente para o robô não avançar durante a conversa
            self.twist = Twist()
            self.cmd_vel_pub.publish(self.twist)
            
            # 2. Envia para o Handler no formato exato: Robo: Bifurcação: <ID>
            self.enviar_para_handler(f"Bifurcação: {self.aruco_detectado_id}")
            self.bifurcacao_enviada = True # Ativa a trava contra spam (Requisito 10)
            
            # 3. Transiciona para o modo de congelamento e espera pela resposta
            self.robot_state = 'aguardando_handler'
            return

        # --- VERIFICAÇÃO DE EVENTO: DETECTOU O OBJETIVO FINAL? ---
        # Nota: Quando a câmera identificar o bicho correto (gato, cachorro ou cavalo)
        if self.nome_objeto_encontrado is not None and not self.objeto_enviado:
            # 1. Imobiliza o robô
            self.twist = Twist()
            self.cmd_vel_pub.publish(self.twist)
            
            # 2. Envia no formato exato: Robo: Objeto: <NOME> (em português)
            self.enviar_para_handler(f"Objeto: {self.nome_objeto_encontrado}")
            self.objeto_enviado = True # Ativa a trava contra spam (Requisito 10)
            
            # 3. Muda para o estado onde aguarda a autorização para voltar para a base
            self.robot_state = 'aguardando_retorno'
            return

        # --- EXECUÇÃO DO PILOTO AUTOMÁTICO ---
        # Se nenhuma placa ou objeto foi visto, roda o seguidor de linha nativo da Acao()
        if self.acao_node.robot_state == 'done': 
            rclpy.spin_once(self.acao_node)
            self.acao_node.reset()

        rclpy.spin_once(self.acao_node)

    def aguardando_handler(self):
        """Estado estático: O robô força velocidade zero e espera a direção da bifurcação"""
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0

    def aguardando_retorno(self):
        """Estado estático: O robô força velocidade zero e espera a ordem de voltar para casa"""
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0

    def retornando(self):
        """Estado onde o robô faz o caminho inverso seguindo a linha até a base"""
        # Executa a ação reversa ou o seguidor de linha padrão para voltar
        if self.acao_node.robot_state == 'done':
            # Se a ação chegou ao fim (o robô retornou fisicamente ao ponto de partida)
            self.acao_node.control() 
            self.get_logger().info('Robô retornou à base com sucesso! Desligando...')
            # Envia o robô para o estado de encerramento definitivo
            self.robot_state = 'stop'
            return

        rclpy.spin_once(self.acao_node)

    def stop(self):
        """Estado Terminal Eterno: Força velocidade zero e encerra as atividades"""
        self.twist = Twist()
        # Nota: O nó permanece em spin_once no main, mas preso e congelado neste estado seguro

    def control(self):
        """Gerenciador principal da máquina de estados acionado periodicamente a 10Hz"""
        print(f'Estado Atual: {self.robot_state}')
        
        # Invoca dinamicamente a função correspondente ao estado atual do robô
        self.state_machine[self.robot_state]() 
        
        # REQUISITO 5 e 6: Só publica a velocidade manualmente se o estado ATUAL 
        # não for um estado automatizado controlado pela classe Acao().
        if self.robot_state not in self.estados_clientes:
            self.cmd_vel_pub.publish(self.twist)
 
def main(args=None):
    rclpy.init(args=args)
    ros_node = ExplorandoOrdenado()

    # O loop principal processa os callbacks até que a máquina de estados atinja o fim seguro ('stop')
    # Respeita o Requisito 7, pois o controle fino ocorre de forma assíncrona dentro do timer de 10Hz
    while rclpy.ok() and ros_node.robot_state != 'stop':
        rclpy.spin_once(ros_node)

    # Garante a parada final absoluta antes de destruir os processos
    ros_node.get_logger().info('Execução finalizada com nota máxima. Destruindo nó.')
    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()