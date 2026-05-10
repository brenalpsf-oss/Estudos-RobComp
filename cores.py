import cv2
import numpy as np

class ProcessadorVisao:
    def __init__(self):
        # --- 1. CONFIGURAÇÃO DE CORES (H, S, V) ---
        # Dica: Na prova, use o seletor de cores ou os valores do handout
        # Lembrar: H vai de 0 a 180 no OpenCV
        self.COR_MIN = np.array([0, 100, 100]) # Ex: Vermelho mínimo
        self.COR_MAX = np.array([10, 255, 255]) # Ex: Vermelho máximo
        
        # Variáveis para guardar resultados
        self.centro_x = 0
        self.area_objeto = 0

    def processar(self, frame):
        """Recebe uma imagem BGR e faz a mágica acontecer."""
        # 1. Converte para HSV (Melhor para cores)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 2. Cria a máscara (Tudo que é da cor vira BRANCO, o resto PRETO)
        mask = cv2.inRange(hsv, self.COR_MIN, self.COR_MAX)
        
        # 3. Limpeza de ruído (Opcional, mas ajuda)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
        
        # 4. Encontrar contornos (Para saber onde o objeto está e o tamanho dele)
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contornos) > 0:
            # Pega o maior contorno encontrado (o objeto principal)
            maior_contorno = max(contornos, key=cv2.contourArea)
            self.area_objeto = cv2.contourArea(maior_contorno)
            
            # Calcula o CENTRO do objeto (Moments)
            M = cv2.moments(maior_contorno)
            if M["m00"] != 0:
                self.centro_x = int(M["m10"] / M["m00"])
                centro_y = int(M["m01"] / M["m00"])
                
                # Desenha um círculo no centro para a gente ver no vídeo
                cv2.circle(frame, (self.centro_x, centro_y), 5, (0, 255, 0), -1)
        else:
            self.area_objeto = 0

        return mask, frame

# --- FUNÇÃO MAIN PARA TESTAR NO VSCODE ---
def main():
    # Se for vídeo de arquivo: cv2.VideoCapture("video.mp4")
    # Se for webcam: cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0) 
    visao = ProcessadorVisao()

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        mask, resultado = visao.processar(frame)
        
        cv2.imshow("Mascara", mask)
        cv2.imshow("Resultado", resultado)
        
        if cv2.waitKey(1) == 27: break # ESC para sair

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()