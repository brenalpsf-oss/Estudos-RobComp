import rclpy
import numpy as np
import time
from rclpy.node import Node
from rclpy.qos import ReliabilityPolicy, QoSProfile

# Mensagens necessárias
from geometry_msgs.msg import Twist
from robcomp_interfaces.msg import MudaPista as MudaPistaMsg

# Módulo de utilitários do Insper
from robcomp_util.base_action import Acao

class MudaPista(Node):
    def __init__(self):
        # REQUISITO 3 e Rúbrica: Nome exato do nó e da classe
        super().__init__('muda_pista_node')
        self.acao_node = Acao()

        # --- MÁQUINA DE ESTADOS ---
        self.robot_state = 'aguardando_inicio'
        self.state_machine = {
            'aguardando_inicio': self.aguardando_inicio,
            'pista_vermelha': self.pista_vermelha,
            'pista_verde': self.pista_verde,
            'pista_azul': self.pista_azul,
            'ciclo_completo': self.ciclo_completo
        }

        # Estados delegados ao piloto automático (Acao)
        self.estados_clientes = ['pista_vermelha', 'pista_verde', 'pista_azul']

        self.twist = Twist()
        self.sentido_atual = None
        self.comando_recebido = False

        # --- COMUNICAÇÃO ---
        self.controle_pub = self.create_publisher(MudaPistaMsg, '/controle', 10)
        self.controle_sub = self.create_subscription(
            MudaPistaMsg,
            '/controle',
            self.controle_callback,
            10
        )
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        # REQUISITO: Avisar que está pronto ao iniciar enviando "READY"
        self.enviar_status("READY")

        # REQUISITO 7: Timer cíclico a 10Hz (sem usar sleep ou loops infinitos)
        self.timer = self.create_timer(0.1, self.control)
        self.get_logger().info('Nó Muda Pista ativo e aguardando ordens.')

    def enviar_status(self, string_status):
        """Função auxiliar para postar atualizações no tópico /controle"""
        msg = MudaPistaMsg()
        msg.status = string_status
        msg.nome = "Brena"
        msg.horario = str(time.strftime("%H:%M:%S"))
        self.controle_pub.publish(msg)

    def controle_callback(self, msg: MudaPistaMsg):
        """Monitora ordens do Orquestrador"""
        # Filtra para não ler a própria mensagem enviada
        if msg.nome == "Brena":
            return

        if msg.status in ["MUDAR_HORARIO", "MUDAR_ANTIHORARIO"]:
            self.sentido_atual = msg.status
            self.comando_recebido = True

    # --- FUNÇÕES DA MÁQUINA DE ESTADOS ---

    def aguardando_inicio(self):
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        if self.comando_recebido:
            self.comando_recebido = False
            self.robot_state = 'pista_vermelha'

    def pista_vermelha(self):
        if self.acao_node.robot_state == 'done':
            rclpy.spin_once(self.acao_node)
            self.acao_node.reset()

        rclpy.spin_once(self.acao_node)

        if self.comando_recebido:
            self.comando_recebido = False
            self.robot_state = 'pista_verde'

    def pista_verde(self):
        if self.acao_node.robot_state == 'done':
            rclpy.spin_once(self.acao_node)
            self.acao_node.reset()

        rclpy.spin_once(self.acao_node)

        if self.comando_recebido:
            self.comando_recebido = False
            self.robot_state = 'pista_azul'

    def pista_azul(self):
        # Na pista azul ele ignora novos comandos do Orquestrador até dar uma volta completa
        if self.acao_node.robot_state == 'done':
            rclpy.spin_once(self.acao_node)
            self.acao_node.reset()

        rclpy.spin_once(self.acao_node)

        # Se a ação completou a volta completa e retornou ao início
        if self.acao_node.robot_state == 'done':
            self.acao_node.control()
            self.robot_state = 'ciclo_completo'

    def ciclo_completo(self):
        self.twist.linear.x = 0.0
        self.twist.angular.z = 0.0
        # Envia READY novamente para recomeçar o ciclo eternamente
        self.enviar_status("READY")
        self.comando_recebido = False
        self.robot_state = 'aguardando_inicio'

    # --- REQUISITOS 5 E 6: FUNÇÃO CONTROL IDENTICA AO BASE_CONTROL ---
    def control(self):
        print(f'Estado Atual: {self.robot_state}')
        self.state_machine[self.robot_state]() 
        if self.robot_state not in self.estados_clientes:
            self.cmd_vel_pub.publish(self.twist)
 
def main(args=None):
    rclpy.init(args=args)
    ros_node = MudaPista()

    while rclpy.ok():
        rclpy.spin_once(ros_node)

    ros_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()