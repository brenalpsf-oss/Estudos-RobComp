import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry # Mensagem que traz a posição (x, y) do robô
import math 

# IMPORTANTE: Se a prova pedir um orquestrador, importe a mensagem dele aqui:
# from robcomp_interfaces.msg import OrquestradorMSG 

class NoLogicaMovimento(Node):
    def __init__(self):
        # 1. Nome do nó que aparece no terminal (ros2 node list)
        super().__init__('no_da_brena')

        # --- 2. VARIÁVEIS DE CONFIGURAÇÃO (MUDE OS VALORES NA PROVA) ---
        self.VEL_LINEAR_BASE = 0.2    # Velocidade para frente
        self.VEL_ANGULAR_BASE = 0.5   # Velocidade de giro (positivo = esquerda)
        self.DISTANCIA_ALVO = 1.0     # Quanto o robô deve andar (em metros)
        
        # --- 3. MÁQUINA DE ESTADOS (ETIQUETAS DE COMPORTAMENTO) ---
        self.ESTADO_PARADO = "PARADO"
        self.ESTADO_ANDANDO = "ANDANDO"
        self.ESTADO_GIRANDO = "GIRANDO"
        self.estado_atual = self.ESTADO_PARADO # Começa sempre parado por segurança

        # --- 4. VARIÁVEIS DE CÁLCULO DE DISTÂNCIA (ODOMETRIA) ---
        self.x_inicial = None # Guardará o X de onde o robô saiu
        self.y_inicial = None # Guardará o Y de onde o robô saiu
        self.distancia_percorrida = 0.0 # Soma o quanto ele já andou

        # --- 5. COMUNICAÇÃO (QUEM FALA E QUEM ESCUTA) ---
        # Publicador: O robô "fala" a velocidade para os motores
        self.pub_cmd_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Assinante 1: O robô "escuta" a própria posição (Odometria)
        self.sub_odom = self.create_subscription(Odometry, '/odom', self.callback_odom, 10)
        
        # Assinante 2: O robô "escuta" o Juiz/Orquestrador (Mude o tipo e tópico se necessário)
        # self.sub_juiz = self.create_subscription(OrquestradorMSG, '/showbot', self.callback_juiz, 10)

        # --- 6. TIMER E COMANDO ---
        # Timer: Roda a função 'control_loop' a cada 0.1 segundos (10 vezes por segundo)
        self.timer = self.create_timer(0.1, self.control_loop)
        self.msg_cmd_vel = Twist() # Variável que guarda a velocidade antes de publicar

        self.get_logger().info("Nó da Brena Iniciado! Aguardando comandos...")

    def callback_odom(self, msg):
        """Função que atualiza a distância percorrida baseada nos sensores do robô."""
        x_atual = msg.pose.pose.position.x
        y_atual = msg.pose.pose.position.y

        # Na primeira vez que rodar, fixa o ponto de partida
        if self.x_inicial is None:
            self.x_inicial = x_atual
            self.y_inicial = y_atual
            self.get_logger().info(f"Saída fixada em X:{x_atual:.2f} Y:{y_atual:.2f}")

        # Cálculo da distância entre o ponto inicial e o atual (Pitágoras)
        # d = raiz_quadrada( (x2-x1)^2 + (y2-y1)^2 )
        self.distancia_percorrida = math.sqrt(
            (x_atual - self.x_inicial)**2 + (y_atual - self.y_inicial)**2
        )

    def callback_juiz(self, msg):
        """Aqui você decide o que fazer quando o juiz mandar uma mensagem."""
        # comando = msg.status # Exemplo: "IN_PROGRESS", "STOP", "LOST"
        # if comando == "IN_PROGRESS":
        #    self.estado_atual = self.ESTADO_ANDANDO
        pass

    def stop_robot(self):
        """Zera todas as velocidades para o robô não bater em nada."""
        self.msg_cmd_vel.linear.x = 0.0
        self.msg_cmd_vel.angular.z = 0.0
        self.pub_cmd_vel.publish(self.msg_cmd_vel)

    def control_loop(self):
        """O cérebro do robô: decide o movimento baseado no ESTADO e na DISTÂNCIA."""
        
        # Por padrão, vamos garantir que o robô esteja parado antes de decidir
        self.msg_cmd_vel.linear.x = 0.0
        self.msg_cmd_vel.angular.z = 0.0

        if self.estado_atual == self.ESTADO_PARADO:
            self.stop_robot()
            
        elif self.estado_atual == self.ESTADO_ANDANDO:
            # VERIFICAÇÃO: Se já andou o que devia, para. Se não, continua andando.
            if self.distancia_percorrida >= self.DISTANCIA_ALVO:
                self.get_logger().warn(f"Cheguei! Andei {self.distancia_percorrida:.2f} metros.")
                self.estado_atual = self.ESTADO_PARADO # Muda para parado
            else:
                self.msg_cmd_vel.linear.x = self.VEL_LINEAR_BASE
                self.msg_cmd_vel.angular.z = 0.0 # Anda reto
            
        elif self.estado_atual == self.ESTADO_GIRANDO:
            self.msg_cmd_vel.linear.x = 0.0
            self.msg_cmd_vel.angular.z = self.VEL_ANGULAR_BASE

        # Envia a velocidade decidida para o simulador
        self.pub_cmd_vel.publish(self.msg_cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    no = NoLogicaMovimento()
    rclpy.spin(no)
    no.destroy_node()
    rclpy.init.shutdown()

if __name__ == '__main__':
    main()