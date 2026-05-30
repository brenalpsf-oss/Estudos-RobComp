import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile
from geometry_msgs.msg import Twist, Point
# Importar a classe da acao do arquivo, como por exemplo
#from robcomp_util.base_action import Acao
from robcomp_interfaces.msg import GameStatus


class Jogador(Node): 
    def __init__(self):
        super().__init__('jogador_node') 

        #maquina de estados
        self.robot_state = 'INITIALIZING'
        self.state_machine = {
            'INITIALIZING': self.inicializando,
            'IN_PROGRESS': self.jogando,
            'WIN': self.vitoria,
            'LOST': self.derrota}

        # Inicialização de variáveis
        self.twist = Twist()
        self.current_word = "" # Salva a palavra falada pela boneca (ex: "ba", "ta", "ti", "3")
        self.current_status = "" # Salva o status atual do jogo (ex: READY, IN_PROGRESS, WIN, LOST)

        # Configuração de QoS para os tópicos de jogo(padrão sempre que a questão exige um "arbitro")
        game_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)

        
        # Subscribers
        # Regra 8: Se inscrever no tópico /young_hee
        self.status_sub = self.create_subscription(
            GameStatus,
            '/young_hee',
            self.game_status_callback,
            game_qos
        )

        # Publishers
        #passar o game_qos para garantir que o contrato de publicação seja idêntico ao de inscrição
        self.young_hee_pub = self.create_publisher(GameStatus, '/young_hee', game_qos)
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        ## Por fim, inicialize o timer
        self.timer = self.create_timer(0.1, self.control)

        #print
        self.get_logger().info('Nó Jogador Inicializado')
    
    def game_status_callback(self, msg):
        #armazena os dados vindos do tópico utilizando os campos reais da mensagem
        self.current_status = msg.status
        self.current_word = msg.current_word

        #Se o jogo começou e o robo ainda estava esperando, muda para ação principal
        if self.current_status == "IN_PROGRESS" and self.robot_state == "INNITIALIZING":
            self.get_logger.info('O jogo começou! Mudando para o estado: IN_PROGRESS')
            self.robot_state = "IN_PROGRESS"
        
        #se a boneca decretar 
        elif self.current_status == "LOST":
            self.robot_state = "LOST"
        elif self.current_status == "WIN":
            self.robot_state = "WIN"


        """
        if msg.status == "IN_PROGRESS":
            if self.robot_state == 'ready': # Só aceitamos se estivermos esperando
                self.lado_L = msg.lado
                self.angulo_theta = msg.theta
                self.robot_state = 'executar'
                self.get_logger().info(f"Recebi ordem! L={self.lado_L}, Theta={self.angulo_theta}")
            
        elif msg.status == "FEEDBACK" and self.robot_state == 'esperando_feedback':
            self.get_logger().info(f"DERIVA RECEBIDA: {msg.drift_m}m")

            self.formas_concluidas += 1

            #parar após a segunda forma(requsito 4)
            if self.formas_concluidas >= 2:
                self.robot_state = 'done'
            else:
                self.robot_state = 'ready'
        """
        pass 
    def control(self): # Controla a máquina de estados - eh chamado pelo timer
        #print(f'Estado Atual: {self.robot_state}')
        self.state_machine[self.robot_state]() # Chama o método do estado atual 
        #if self.robot_state not in self.estados_clientes: # Se o estado atual não é um estado "cliente de ação"
        #    self.cmd_vel_pub.publish(self.twist) # Publica a velocidade

    def inicializando(self):
        # Vamos apenas printar para ver o timer funcionando
        self.get_logger().info('Executando estado: INITIALIZING', throttle_duration_sec=2.0)

        # 1. Cria o objeto da mensagem da prova
        msg = GameStatus()
        
        # 2. Preenche os dados solicitados pelo enunciado
        msg.status = "READY"
        msg.nome = "Brena" # Descomente e ajuste com o nome correto do campo que o terminal te mostrar

        # 3. Publica no tópico para avisar a boneca Young-Hee
        self.young_hee_pub.publish(msg)
        self.get_logger().info('Mensagem READY enviada! Aguardando início do jogo...')

        # 4. Transição de Estado de Segurança:
        # Para o robô não ficar floodando o comando READY a 10Hz, vamos criar um estado temporário
        # de espera, ou simplesmente checar se a boneca já mudou o status no callback.
    
    def jogando(self):
        pass

    def vitoria(self):
        pass

    def derrota(self):
        pass


    """
    def acao(self):
        if self.acao_node.robot_state == 'done': # Se a ação NÂO FOI INICIADA
            print("\nIniciando [ACAO]...")
            rclpy.spin_once(self.acao_node) # Processa as callbacks uma vez
            self.acao_node.reset() # Reseta o nó para iniciar a ação

        rclpy.spin_once(self.acao_node) # Processa os callbacks e o timer

        if self.acao_node.robot_state == 'done': # Se a ação FOI FINALIZADA
            self.acao_node.control() # Garante que o robo é parado antes de finalizar a ação
            print("[ACAO] Finalizada.")
            self.robot_state = 'done' # Muda para o próximo estado da máquina de estados

    def done(self):
        self.twist = Twist()
    """
def main(args=None):
    rclpy.init(args=args) # Inicia o ROS2
    ros_node = Jogador() # Cria o nó

    while not ros_node.robot_state == 'done': # Enquanto o robô não estiver parado
        rclpy.spin_once(ros_node) # Processa os callbacks e o timer

    ros_node.destroy_node() # Destroi o nó
    rclpy.shutdown() # Encerra o ROS2

if __name__ == '__main__':
    main()