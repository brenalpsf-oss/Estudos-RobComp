import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class FirstNode(Node):
    def __init__(self):
        #cria um nó chamado first_node
        super().__init__('first_node')

        #Twist: tipo de mensagem que será publicada
        #'/cmd_vel' -> nome do tópico que será publicado
        #10 -> tamanho da fila de mensagens(o valor padrão é 10)
        self.vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        #0.25 -> tempo entre execuções da função self.control
        #self.control -> função que será executada a cada 0.25 segundos
        self.timer = self.create_timer(0.25, self.control)


        """
        A função self.control será chamada a cada 0.25 segundos, e em cada chamada,
        ela cria uma mensagem do tipo Twist, altera o valor da velocidade linear para 0.2 e
        publica a mensagem no tópico cmd_vel.
        """

    def control(self):
        msg = Twist()
        msg.linear.x = 0.2  # m/s
        self.vel_pub.publish(msg)


def main(args=None):
    #inicializa o modulo rclpy(modulo da ROS)
    rclpy.init(args=args)
    #cria uma instancia da classe FirstNOde
    node = FirstNode()
    #mantem o nó em execucao ate que ele seja finalizado
    rclpy.spin(node)
    #finaliza o no 
    node.destroy_node()
    #finaliza o modulo rclpy
    rclpy.shutdown()

if __name__ == '__main__':
    main()