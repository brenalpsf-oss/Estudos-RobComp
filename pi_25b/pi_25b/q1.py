import rclpy
import numpy as np
np.float = float
import math
from rclpy.node import Node
from robcomp_util.odom import Odom
from rclpy.qos import ReliabilityPolicy, QoSProfile
from geometry_msgs.msg import Twist, Point
from robcomp_interfaces.msg import OrquestratorMSG 


class ShowBot(Node, Odom):
    def __init__(self):
        Node.__init__(self, 'showbot_node') 
        Odom.__init__(self, self)


        self.nome_estudante = "Brena Lopes Ferro"
        self.formas_completas = 0

        #variáveis para guardar o que o orquestrador mandar 
        self.lado_L = 0.0
        self.angulo_tetha = 0.0

        #comunicação com o orquestrador
        #publicar e assinar o topico showbot
        self.showbot_pub = self.create_publisher(OrquestratorMSG, '/showbot', 10)
        self.showbot_sub = self.create_subscription(OrquestratorMSG, '/showbot', self.orquestrador_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10) #para o robo começar andar


        #maquina de estado
        self.robot_state = 'ready'
        self.state_machine = {
            'ready': self.ready, 
            'executar': self.executar, 
            'esperando_feedback': self.esperando_feedback,
            'done': self.done }
        
        
        self.sub_state = 'andar'
        self.contador_lados = 0
        self.twist = Twist()

        self.x0 = 0.0
        self.y0 = 0.0
        self.yaw0 = 0.0
        self.iniciou_segmento = True   #flag para saber quando salvar o ponto inicial

        self.timer = self.create_timer(0.1, self.control)
        self.estados_clientes = ['ready', 'done']


    def orquestrador_callback(self, msg):
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
    

    def control(self): # Controla a máquina de estados - eh chamado pelo timer
        if self.robot_state == 'ready':
            msg = OrquestratorMSG()
            msg.status = "READY"   #preenche o campo status com a palavra READY(palavra que o orq espera para saber que pode começar)
            msg.student_name = self.nome_estudante
            msg.horario = self.get_clock().now().nanoseconds/1e9 #colocar a hora na mensagem
            self.showbot_pub.publish(msg) #entrega o formulario

        #executa a maq de estados
        self.state_machine[self.robot_state]() # Chama o método do estado atual 

        if self.robot_state not in self.estados_clientes: # Se o estado atual não é um estado "cliente de ação"
            self.cmd_vel_pub.publish(self.twist) # Publica a velocidade

    def ready(self):
        self.twist = Twist()

    def executar(self):
        n_lados_total = abs(360//self.angulo_tetha)

        #se sub-estado for andar
        if self.sub_state == 'andar':
            #manda acao de andar L metros, se a acao de andar terminou, muda o sub_state para girar
            if self.iniciou_segmento:
                self.x0,self.y0 = self.x,self.y 
                self.iniciou_segmento = False
            
            dist_percorrida = math.sqrt((self.x-self.x0)**2 + (self.y - self.y0)**2)

            if dist_percorrida < self.lado_L:
                self.twist.linear.x = 0.2
                self.twist.angular.z = 0.0
            else:
                self.sub_state = 'girar'
                self.iniciou_segmento = True

        elif self.sub_state == 'girar':
            if self.iniciou_segmento:
                self.yaw0 = self.yaw
                self.iniciou_segmento = False
                self.target_rad = math.radians(self.angulo_theta)

            diff_yaw = self.yaw - self.yaw0
            diff_yaw = math.atan2(math.sin(diff_yaw), math.cos(diff_yaw))

            if abs(diff_yaw) < abs(self.target_rad):
                self.twist.linear.x = 0.0
                self.twist.angular.z = 0.4 if self.target_rad > 0 else -0.4
            else:
                self.contador_lados += 1
                self.iniciou_segmento = True
                
                if self.contador_lados >= n_lados_total:
                    self.robot_state = 'esperando_feedback'
                    self.contador_lados = 0
                    self.sub_state = 'andar'
                else:
                    self.sub_state = 'andar' 


    def esperando_feedback(self):
        self.twist = Twist()

    def done(self):
        self.twist = Twist()
        self.get_logger().info("fim da prova")
 
def main(args=None):
    rclpy.init(args=args) 
    ros_node = ShowBot() 

    while not ros_node.robot_state == 'done':
        rclpy.spin_once(ros_node) 

    ros_node.destroy_node() 
    rclpy.shutdown() 

if __name__ == '__main__':
    main()