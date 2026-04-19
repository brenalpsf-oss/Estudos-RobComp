import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rclpy.qos import ReliabilityPolicy, QoSProfile

class SecondNode(Node):
    def __init__(self):
        super().__init__('second_node')
        self.x = 0.0
        self.y = 0.0

        #assina o topico /odom recebendo mensagens Odometry
        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            #executa a cada mensagem recebida
            #odom_calback atualiza x e y com a posicao do robo
            self.odom_callback,
            #qualidade de codigo(opcional)
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.timer = self.create_timer(0.25, self.control)

    def odom_callback(self, msg: Odometry):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def control(self):
        print(f'Posição x: {self.x:.3f}')
        print(f'Posição y: {self.y:.3f}\n')


def main(args=None):
    rclpy.init(args=args)
    node = SecondNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()