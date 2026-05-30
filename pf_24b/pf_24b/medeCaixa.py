import rclpy
import numpy as np
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile

# Imports de mensagens obrigatórios para movimentação e leitura de dados
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan     # Mensagem para ler o LiDAR (Laser)
from nav_msgs.msg import Odometry          # Mensagem para ler a posição (X, Y) do robô

# Componente utilitário fornecido no capítulo 3 para controle do robô
from robcomp_util.base_action import Acao

class MedirCaixa(Node):
    def __init__(self):
        # REQUISITO: Inicializa o nó com o nome exato exigido pelo enunciado
        super().__init__('medidor_node') 
        
        # Instancia a classe de ação interna fornecida
        self.acao_node = Acao() 

        # --- MÁQUINA DE ESTADOS ---
        self.robot_state = 'aproxima'
        self.state_machine = {
            'aproxima': self.aproxima,       # Vai reto até encontrar a caixa
            'alinha': self.alinha,           # Gira 90 graus para ficar de lado para a caixa
            'mede_lado1': self.mede_lado1,   # Anda raspando o lado 1 e mede a largura
            'gira_quina': self.gira_quina,   # Faz a curva de 90 graus na quina da caixa
            'mede_lado2': self.mede_lado2,   # Anda raspando o lado 2 e mede o comprimento
            'done': self.done                # Para os motores e encerra as atividades
        }

        # Estado 'acao' não é usado diretamente aqui pois controlamos o contorno de forma customizada via Laser
        self.estados_clientes = [] 

        # --- VARIÁVEIS DE MOVIMENTAÇÃO E SENSORES ---
        self.twist = Twist()
        self.x_atual = 0.0
        self.y_atual = 0.0
        
        # Leituras iniciais do Laser (iniciadas com infinito para segurança)
        self.laser_frontal = float('inf')
        self.laser_lateral_direito = float('inf')

        # --- MEMÓRIA DE COORDENADAS PARA MEDIÇÃO ---
        self.quina1 = None
        self.quina2 = None
        self.quina3 = None
        
        # Flags de controle para garantir que o cálculo e o print aconteçam apenas UMA vez
        self.largura_calculada = False
        self.comprimento_calculada = False

        # --- SUBSCRIBERS E PUBLISHERS ---
        # Subscriber do LaserScan configurado com QoS Best Effort (padrão do simulador para sensores)
        self.laser_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.laser_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )

        # Subscriber de Odometria para monitorar o deslocamento em metros no mapa
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Publisher de velocidade padrão
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # Inicializa o timer cíclico de controle rodando a 10Hz (0.1 segundos)
        self.timer = self.create_timer(0.1, self.control)
        self.get_logger().info('Nó Medidor de Caixa iniciado e operando de forma autônoma!')

    def odom_callback(self, msg: Odometry):
        """Atualiza a posição real (X, Y) do robô no mundo baseado nos encoders das rodas"""
        self.x_atual = msg.pose.pose.position.x
        self.y_atual = msg.pose.pose.position.y

    def laser_callback(self, msg: LaserScan):
        """Monitora as distâncias do robô até a caixa através do LiDAR"""
        # Trata leituras erráticas (NaN ou Inf) substituindo por um valor alto seguro
        ranges_limpos = [x if not np.isnan(x) and not np.isinf(x) else 10.0 for x in msg.ranges]
        
        # 0 graus é a leitura reta da frente do robô
        self.laser_frontal = ranges_limpos[0]
        
        # 270 graus é a leitura da lateral direita do robô
        self.laser_lateral_direito = ranges_limpos[270]

    def calcular_distancia(self, p1, p2):
        """Aplica a Fórmula da Distância Euclidiana entre dois pontos (X, Y)"""
        return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    # --- MÉTODOS DA MÁQUINA DE ESTADOS ---

    def aproxima(self):
        """Avança em linha reta em direção à origem até chegar perto da caixa"""
        if self.laser_frontal > 0.6:
            self.twist.linear.x = 0.2
            self.twist.angular.z = 0.0
        else:
            # Chegou perto da caixa! Para, grava a primeira quina e muda de estado
            self.twist.linear.x = 0.0
            self.quina1 = (self.x_atual, self.y_atual)
            self.get_logger().info(f'Caixa encontrada! Quina 1 gravada em: X={self.x_atual:.2f}, Y={self.y_atual:.2f}')
            self.robot_state = 'alinha'

    def alinha(self):
        """Gira o robô em 90 graus para deixar a lateral direita apontada para a parede da caixa"""
        # Como ele estava de frente, ao girar para a esquerda (angular positivo), 
        # a parede da caixa migra naturalmente para o sensor da direita (270 graus)
        if self.laser_lateral_direito > 0.8:
            self.twist.linear.x = 0.0
            self.twist.angular.z = 0.3  # Velocidade angular de rotação
        else:
            # Alinhamento concluído! O sensor da direita capturou a parede lateral da caixa
            self.twist.angular.z = 0.0
            self.robot_state = 'mede_lado1'

    def mede_lado1(self):
        """Navega raspando a primeira lateral da caixa até a leitura do laser saltar (fim da parede)"""
        # Se o laser da direita ler um valor baixo, significa que ele ainda está vendo a parede da caixa
        if self.laser_lateral_direito < 1.2:
            self.twist.linear.x = 0.15
            self.twist.angular.z = 0.0
        else:
            # O laser subiu abruptamente! Significa que passamos da quina e a parede acabou
            self.twist.linear.x = 0.0
            if not self.largura_calculada:
                self.quina2 = (self.x_atual, self.y_atual)
                largura = self.calcular_distancia(self.quina1, self.quina2)
                # REQUISITO EXIGIDO: Exibir o resultado usando obrigatoriamente o LOG do ROS 2
                self.get_logger().info(f'LARGURA DA CAIXA MEDIDA: {largura:.2f} metros')
                self.largura_calculada = True
            
            # Avança só um pouquinho para o eixo do robô passar da quina antes de girar
            self.robot_state = 'gira_quina'

    def gira_quina(self):
        """Faz o robô contornar a quina girando para a direita (em direção ao próximo lado)"""
        # Gira para a direita (angular negativo) até que o laser frontal limpe e a lateral ache a nova parede
        if self.laser_lateral_direito > 0.8:
            self.twist.linear.x = 0.05  # Anda bem devagar enquanto curva para não colidir
            self.twist.angular.z = -0.3 
        else:
            # Achou a segunda parede! Estabiliza e transiciona para medir o comprimento
            self.twist.angular.z = 0.0
            self.robot_state = 'mede_lado2'

    def mede_lado2(self):
        """Navega raspando a segunda lateral da caixa até o laser da direita perder a parede novamente"""
        if self.laser_lateral_direito < 1.2:
            self.twist.linear.x = 0.15
            self.twist.angular.z = 0.0
        else:
            # A parede acabou de novo! Chegamos ao fim do contorno exigido
            self.twist.linear.x = 0.0
            if not self.comprimento_calculada:
                self.quina3 = (self.x_atual, self.y_atual)
                comprimento = self.calcular_distancia(self.quina2, self.quina3)
                # REQUISITO EXIGIDO: Exibir o resultado usando obrigatoriamente o LOG do ROS 2
                self.get_logger().info(f'COMPRIMENTO DA CAIXA MEDIDO: {comprimento:.2f} metros')
                self.comprimento_calculada = True
            
            # Tarefa cumprida! Envia para o estado final seguro
            self.robot_state = 'done'

    def done(self):
        """Estado terminal seguro: Garante parada absoluta dos motores"""
        self.twist = Twist()

    def control(self):
        """Gerenciador cíclico executado a 10Hz pelo Timer"""
        print(f'Estado Atual: {self.robot_state} | Laser Frontal: {self.laser_frontal:.2f} | Laser Direito: {self.laser_lateral_direito:.2f}')
        
        # Invoca o método dinamicamente baseado no estado atual
        self.state_machine[self.robot_state]() 
        
        # Só publica a velocidade se não for um estado terceirizado (respeitando o base_control)
        if self.robot_state not in self.estados_clientes:
            self.cmd_vel_pub.publish(self.twist)
 
def main(args=None):
    rclpy.init(args=args)
    ros_node = MedirCaixa()

    # Executa o loop processando os callbacks de Odometria e Laser até a máquina atingir o estado 'done'
    while rclpy.ok() and ros_node.robot_state != 'done':
        rclpy.spin_once(ros_node)

    # Força uma última publicação de segurança com velocidade zero antes de fechar o programa
    parada_final = Twist()
    ros_node.cmd_vel_pub.publish(parada_final)

    ros_node.get_logger().info('Medições concluídas com sucesso. Destruindo nó...')
    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()