import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile

# --- GUIA DE IMPORTS (Descomente o que for usar na questão) ---
from geometry_msgs.msg import Twist, Point
# from sensor_msgs.msg import LaserScan     # Se a questão usar Laser/LiDAR
# from nav_msgs.msg import Odometry          # Se a questão usar Posição/Odometria
# from sensor_msgs.msg import Image         # Se a questão usar Imagem/Câmera da massa
# from cv_bridge import CvBridge             # Se a questão usar OpenCV para processar imagem

# Import do componente utilitário padrão do Insper
from robcomp_util import Acao

class NomeDaClasseDaProva(Node):
    def __init__(self):
        #Mude o nome do nó conforme o enunciado exigir
        super().__init__('nome_do_node_exigido') 
        
        # Instancia a ação padrão (se for usar o seguidor de linha nativo)
        self.acao_node = Acao() 

        # --- MÁQUINA DE ESTADOS (Mude os nomes conforme a sua lógica) ---
        self.robot_state = 'estado_inicial'
        self.state_machine = {
            'estado_inicial': self.estado_inicial,
            'estado_intermediario': self.estado_intermediario,
            'done': self.done
        }

        # Coloque aqui os estados onde a classe Acao() controla os motores por completo.
        # Nos estados listados aqui, o control() NÃO vai publicar velocidade manualmente.
        self.estados_clientes = ['coloque_aqui_estados_de_piloto_automatico'] 

        # --- VARIÁVEIS DE CONTROLE E SENSORES (Coringa) ---
        self.twist = Twist()
        
        # Variáveis de Odometria (se precisar rastrear posição)
        self.x_atual = 0.0
        self.y_atual = 0.0
        
        # Variáveis de Laser (se precisar rastrear distâncias)
        self.laser_frontal = float('inf')
        
        # Variável de Visão Computacional (se precisar usar OpenCV)
        # self.bridge = CvBridge()

        # --- SUBSCRIBERS (Ative apenas os que a questão pedir) ---
        
        # Exemplo Laser (LiDAR): Configurado com QoS Best Effort para não travar no Gazebo
        # self.laser_sub = self.create_subscription(
        #     LaserScan,
        #     '/scan',
        #     self.laser_callback,
        #     QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        # )

        # Exemplo Odometria:
        # self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)

        # Exemplo Câmera:
        # self.image_sub = self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

        # --- PUBLISHERS ---
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # TODO: Adicione aqui outros publishers se a questão pedir (ex: /handler da prova anterior)

        # ---  TIMER CÍCLICO (10Hz) ---
        self.timer = self.create_timer(0.1, self.control)
        self.get_logger().info('Nó Coringa Inicializado com Sucesso!')

    # ---  CALLBACKS DOS SENSORES (Preencha se for usar) ---

    def odom_callback(self, msg):
        """Atualiza a posição do robô no mapa"""
        self.x_atual = msg.pose.pose.position.x
        self.y_atual = msg.pose.pose.position.y

    def laser_callback(self, msg):
        """Atualiza os dados de distância do laser"""
        ranges_limpos = [x if not np.isnan(x) and not np.isinf(x) else 10.0 for x in msg.ranges]
        self.laser_frontal = ranges_limpos[0] # 0 graus = frente

    def image_callback(self, msg):
        """Processa a imagem da câmera usando OpenCV (Filtro de Cor HSV, etc)"""
        # cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        # TODO: Sua lógica de processamento de imagem entra aqui
        pass

    # ---  LÓGICA DA MÁQUINA DE ESTADOS ---

    def estado_inicial(self):
        """Primeiro comportamento do robô"""
        # TODO: Escreva o que o robô faz aqui
        # Exemplo: andar para frente se o laser frontal estiver limpo
        if self.laser_frontal > 0.5:
            self.twist.linear.x = 0.2
            self.twist.angular.z = 0.0
        else:
            # Condição de troca de estado
            self.twist.linear.x = 0.0
            self.robot_state = 'estado_intermediario'

    def estado_intermediario(self):
        """Segundo comportamento do robô"""
        # TODO: Escreva a lógica do próximo passo aqui
        pass

    def done(self):
        """Estado final seguro para imobilizar o robô"""
        self.twist = Twist()

    # --- GERENCIADOR DE CONTROLE (Não mexer!) ---
    def control(self): 
        # Mostra o estado atual no terminal para te ajudar no debug durante a prova
        print(f'Estado Atual: {self.robot_state}')
        
        # Executa a função associada ao estado atual
        self.state_machine[self.robot_state]() 
        
        # Só publica a velocidade se o estado não pertencer aos estados controlados pela Acao()
        if self.robot_state not in self.estados_clientes:
            self.cmd_vel_pub.publish(self.twist)
 
# ---  EXECUÇÃO PRINCIPAL ---
def main(args=None):
    rclpy.init(args=args)
    ros_node = NomeDaClasseDaProva()

    # O loop roda processando os dados até a máquina chegar no estado final 'done'
    while rclpy.ok() and ros_node.robot_state != 'done':
        rclpy.spin_once(ros_node)

    # Garante parada total física antes de encerrar o processo de vez
    parada_segura = Twist()
    ros_node.cmd_vel_pub.publish(parada_segura)

    ros_node.get_logger().info('Nó encerrado com segurança.')
    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()