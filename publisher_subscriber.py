import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
# IMPORTANTE: Na hora da prova, verifique o nome exato da mensagem do Orquestrador
# Geralmente é algo como:
# from robcomp_interfaces.msg import OrquestradorMSG 

class NoProva(Node):
    def __init__(self):
        super().__init__('no_da_brena') # Nome do nó

        # --- [1] VARIÁVEIS QUE VOCÊ VAI MUDAR NA PROVA ---
        self.TOPICO_JUIZ = '/showbot'      # Nome do tópico do Orquestrador
        self.TOPICO_VELOCIDADE = '/cmd_vel' 
        self.VEL_LIN = 0.2                 # Quanto ele anda pra frente
        self.VEL_ANG = 0.5                 # Quanto ele gira
        
        # --- [2] ESTADOS (O segredo da prova) ---
        # Defina aqui os nomes dos estados que a questão pedir
        self.ESTADO_PARADO = "PARADO"
        self.ESTADO_ANDANDO = "ANDANDO"
        self.ESTADO_FINALIZADO = "DONE"
        self.estado_atual = self.ESTADO_PARADO # Começa sempre parado!

        # --- [3] COMUNICAÇÃO (Pubs e Subs) ---
        self.pub_cmd_vel = self.create_publisher(Twist, self.TOPICO_VELOCIDADE, 10)
        
        # Assinante: Ele vai ouvir o Orquestrador
        # MUDE: 'OrquestradorMSG' para o tipo que estiver no handout da prova
        # self.sub_orquestrador = self.create_subscription(OrquestradorMSG, self.TOPICO_JUIZ, self.callback_juiz, 10)

        # --- [4] LOOP DE CONTROLE (O "Cérebro") ---
        self.timer = self.create_timer(0.1, self.control_loop)
        self.msg_cmd_vel = Twist()

        # DICA: Sempre printe algo ao iniciar para saber que o nó rodou
        self.get_logger().info("Nó da Brena iniciado e aguardando comandos...")

    def callback_juiz(self, msg):
        """
        Aqui é onde o robô ESCUTA. 
        Mude a lógica abaixo conforme as palavras que o Orquestrador enviar.
        """
        comando_recebido = msg.status # Pode ser msg.palavra, msg.status, etc.
        
        self.get_logger().info(f"Ouvi do juiz: {comando_recebido}")

        if comando_recebido == "IN_PROGRESS": # Exemplo da Batatinha Frita
            self.estado_atual = self.ESTADO_ANDANDO
        elif comando_recebido == "STOP" or comando_recebido == "LOST":
            self.estado_atual = self.ESTADO_PARADO
            self.get_logger().warn("Parei porque o juiz mandou!")

    def control_loop(self):
        """
        Aqui é onde o robô AGE baseado no estado.
        """
        # Limpa as velocidades para garantir que não vai andar sem querer
        self.msg_cmd_vel.linear.x = 0.0
        self.msg_cmd_vel.angular.z = 0.0

        if self.estado_atual == self.ESTADO_ANDANDO:
            self.msg_cmd_vel.linear.x = self.VEL_LIN
            self.msg_cmd_vel.angular.z = 0.0 # Se quiser que ele ande reto
            
        elif self.estado_atual == self.ESTADO_PARADO:
            self.msg_cmd_vel.linear.x = 0.0
            self.msg_cmd_vel.angular.z = 0.0

        # Publica a velocidade de fato
        self.pub_cmd_vel.publish(self.msg_cmd_vel)

def main(args=None):
    rclpy.init(args=args)
    no = NoProva()
    rclpy.spin(no)
    no.destroy_node()
    rclpy.init.shutdown()

if __name__ == '__main__':
    main()