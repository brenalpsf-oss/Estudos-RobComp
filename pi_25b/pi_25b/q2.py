import cv2
import numpy as np
import math

class LogoManipulator:
    def run(self, logo, background):
        # 1. redimensionar o fundo para ter o mesmo tamanho do logo (codigo dado no enunciado)
        h, w = logo.shape[:2] # altura e largura da imagem de referência
        background = cv2.resize(background, (w, h))# redimensiona o background para ter o mesmo tamanho

        # 2. Criar a máscara para as partes brancas
        # No BGR, o branco puro é (255, 255, 255)
        lower_white = np.array([250, 250, 250])
        upper_white = np.array([255, 255, 255])
        mask = cv2.inRange(logo, lower_white, upper_white)

        # 3. Criar a máscara invertida (o que NÃO é branco)
        mask_inv = cv2.bitwise_not(mask)

        # 4. Recortar o fundo onde a logo deve aparecer
        # Usamos o 'bitwise_and' com a máscara para extrair apenas os pixels coloridos
        logo_fill = cv2.bitwise_and(background, background, mask=mask)

        # 5. Recortar a parte colorida do logo original (o que sobrou)
        logo_original_part = cv2.bitwise_and(logo, logo, mask=mask_inv)

        # 6. Juntar as duas partes
        final_image = cv2.add(logo_fill, logo_original_part)

        return final_image


def main():
    # Carregar as imagens 
    img_logo = cv2.imread('logo1.png')
    img_bg = cv2.imread('background.png')

    if img_logo is None or img_bg is None:
        print("Erro: Não foi possível carregar as imagens. Verifique os nomes dos arquivos.")
        return

    # Instanciar a classe e rodar o método
    manipulator = LogoManipulator()
    result = manipulator.run(img_logo, img_bg)

    # Exibir e salvar o resultado
    cv2.imshow("Logo Manipulada", result)
    cv2.imwrite("resultado_final.png", result)
    
    print("Sucesso! Imagem salva como 'resultado_final.png'.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()