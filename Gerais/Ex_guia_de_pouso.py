"""
Contexto: Um drone de entregas precisa pousar em uma plataforma específica no meio de
várias outras. As plataformas são círculos de cores diferentes. O drone só pode pousar na
plataforma que estiver mais centralizada na imagem (mais próxima do centro da tela).

Você deve identificar todos os "alvos" (círculos) coloridos, calcular a distância de cada um até
o centro da imagem e indicar visualmente qual é o alvo ideal para o pouso.

método run(self, frame) deve:
- dentificar alvos de 3 cores (ex: Azul, Amarelo e Vermelho).
-Calcular o Centro (Centroide) de cada alvo.
- Calcular a Distância Euclidiana entre o centro do alvo e o centro da imagem ($width/2, height/2$).


O programa deve desenhar uma linha ligando o centro da imagem ao centro de cada alvo
A função main deve processar o vídeo da webcam e exibir no terminal qual cor é a "Vencedora" (a mais próxima do centro) em tempo real.

RUBRICA:
Segmenta as cores e encontra os contornos.
Calcula corretamente o centro de cada objeto (usando cv2.moments).
Desenha as linhas de guia e escreve a distância na tela (usando cv2.putText).
Implementa a lógica de decisão: o código identifica sozinho qual é a menor distância e destaca esse objeto
"""


import cv2
import numpy as np
import math

class LandingController:
    def __init__(self):
        # 1. Dicionário de cores (H, S, V)
        # Nota: O Vermelho às vezes precisa de dois ranges, aqui usamos o inicial
        self.colors = {
            'Vermelho': ([0, 100, 100], [10, 255, 255]),
            'Amarelo':  ([20, 100, 100], [35, 255, 255]),
            'Azul':     ([100, 100, 100], [130, 255, 255])
        }

    def run(self, frame):
        """Identifica alvos e decide qual está mais perto do centro."""
        
        # Pega o centro da imagem (X, Y)
        h_img, w_img = frame.shape[:2]
        centro_img = (w_img // 2, h_img // 2)
        
        # Desenha uma cruz no centro da tela para referência visual
        cv2.line(frame, (centro_img[0]-10, centro_img[1]), (centro_img[0]+10, centro_img[1]), (255,255,255), 2)
        cv2.line(frame, (centro_img[0], centro_img[1]-10), (centro_img[0], centro_img[1]+10), (255,255,255), 2)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        alvos_encontrados = [] # Lista para guardar as distâncias de cada cor

        for cor, (lower, upper) in self.colors.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
            
            contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contornos:
                if cv2.contourArea(cnt) > 1000: # Filtro de tamanho para o alvo
                    # 2. CALCULA O CENTRO DO ALVO (MOMENTS)
                    #PARTE QUE NAO TEM EM OUTROS CODIGOS 
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        
                        # 3. CALCULA A DISTÂNCIA ATÉ O CENTRO DA IMAGEM
                        dist = math.sqrt((cX - centro_img[0])**2 + (cY - centro_img[1])**2)
                        
                        # Guarda os dados para comparar depois
                        alvos_encontrados.append({
                            'cor': cor,
                            'distancia': dist,
                            'centro': (cX, cY),
                            'contorno': cnt
                        })
                        
                        # Desenha uma linha ligando o alvo ao centro
                        cv2.line(frame, (cX, cY), centro_img, (200, 200, 200), 1)

        # 4. LÓGICA DE DECISÃO: QUEM É O VENCEDOR?
        vencedor = None
        if len(alvos_encontrados) > 0:
            # Encontra o item da lista que tem a menor 'distancia'
            vencedor = min(alvos_encontrados, key=lambda x: x['distancia'])
            
            # Destaca o vencedor na tela
            cX, cY = vencedor['centro']
            cv2.putText(frame, "ALVO SEGURO", (cX-40, cY-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.drawContours(frame, [vencedor['contorno']], -1, (0, 255, 0), 3)

        return frame, vencedor

def main():
    cap = cv2.VideoCapture(0)
    controller = LandingController()

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Processa o frame
        resultado_frame, info_vencedor = controller.run(frame)

        # Imprime no terminal o vencedor do momento
        if info_vencedor:
            print(f"Pouso ideal: {info_vencedor['cor']} | Distância: {info_vencedor['distancia']:.1f}px")

        cv2.imshow("Guia de Pouso Drone", resultado_frame)
        
        if cv2.waitKey(1) == 27: # ESC para sair
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()