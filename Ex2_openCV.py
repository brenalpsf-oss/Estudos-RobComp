import cv2
import numpy as np
import os # Para lidar com nomes de arquivos

class BalloonCounter:
    def __init__(self):
        # Intervalos HSV para Amarelo, Laranja e Roxo
        self.ranges = {
            'amarelo': ([20, 100, 100], [35, 255, 255]),
            'laranja': ([5, 100, 100], [18, 255, 255]),
            'roxo': ([130, 50, 50], [170, 255, 255])
        }

    def run(self, image):
        """Processa uma única imagem e retorna a contagem de balões."""
        contagem = {'amarelo': 0, 'laranja': 0, 'roxo': 0}
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        for cor, (lower, upper) in self.ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            # Limpeza de ruído
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5), np.uint8))
            
            # Identificação de contornos
            contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contornos:
                if cv2.contourArea(cnt) > 500: # Filtro de tamanho
                    contagem[cor] += 1
        return contagem

def main():
    # 1. Inicializa a classe e o dicionário mestre de resultados
    counter = BalloonCounter()
    resultados = {}
    
    # 2. Lista com os nomes das 5 imagens (ajuste se os nomes forem diferentes)
    lista_imagens = ["img1.png", "img2.png", "img3.png", "img4.png", "img5.png"]
    pasta = "imgs/" # Certifique-se que as imagens estão nesta pasta

    for nome_arquivo in lista_imagens:
        caminho = os.path.join(pasta, nome_arquivo)
        img = cv2.imread(caminho)

        if img is not None:
            # 3. Chama o método run para obter a contagem daquela imagem
            contagem_atual = counter.run(img)
            
            # 4. Armazena no dicionário mestre
            resultados[nome_arquivo] = contagem_atual
            
            # 5. Visualização (Exigência da Rubrica 2)
            print(f"Processando {nome_arquivo}...")
            cv2.imshow(f"Original - {nome_arquivo}", img)
            cv2.waitKey(500) # Mostra por meio segundo e pula para a próxima
        else:
            print(f"Erro: Não foi possível carregar {nome_arquivo}")

    # 6. Fecha janelas e imprime o resultado final (Exigência da Rubrica 5)
    cv2.destroyAllWindows()
    
    print("\n--- RESULTADO FINAL ---")
    import json # Usamos json apenas para o print ficar bonito/identado
    print(json.dumps(resultados, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()