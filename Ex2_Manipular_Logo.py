import cv2
import numpy as np

class LogoManipulator:
    def __init__(self):
        # Não precisamos de variáveis iniciais para esta lógica
        pass

    def run(self, logo, fundo):
        """Recebe a imagem da logo e do fundo, retornando a logo preenchida."""
        
        # 1. Redimensionar o fundo para ter o mesmo tamanho da logo (Exigência 4 e Dica)
        h, w = logo.shape[:2]
        fundo_resized = cv2.resize(fundo, (w, h))

        # 2. Criar máscara para identificar onde a logo é BRANCA (255, 255, 255)
        # Usamos um range alto para pegar o branco puro do símbolo/texto
        mask = cv2.inRange(logo, np.array([250, 250, 250]), np.array([255, 255, 255]))

        # 3. Criar a máscara inversa (onde NÃO é branco, ou seja, o fundo da logo original)
        mask_inv = cv2.bitwise_not(mask)

        # 4. Isolar apenas a parte colorida da imagem da logo original (o que não é branco)
        logo_fundo_original = cv2.bitwise_and(logo, logo, mask=mask_inv)

        # 5. Isolar apenas a parte do NOVO fundo que ficará dentro do símbolo branco
        novo_preenchimento = cv2.bitwise_and(fundo_resized, fundo_resized, mask=mask)

        # 6. Somar as duas partes para obter o resultado final (Exigência 4 e Dica)
        resultado = cv2.add(logo_fundo_original, novo_preenchimento)

        return resultado

def main():
    # Inicializa a classe
    manipulador = LogoManipulator()

    # Carrega a imagem de fundo (background.png)
    background = cv2.imread("imgs/background.png")
    
    # Lista das logos fornecidas para o loop (Exigência 6 e Vídeo)
    logos_nomes = ["logo1.png", "logo2.png", "logo3.png"]

    if background is None:
        print("Erro: Imagem de fundo não encontrada.")
        return

    for nome in logos_nomes:
        logo_img = cv2.imread(f"imgs/{nome}")

        if logo_img is not None:
            # Aplica o método de manipulação
            resultado_final = manipulador.run(logo_img, background)

            # Exibe os resultados (Rubrica 2)
            cv2.imshow(f"Original - {nome}", logo_img)
            cv2.imshow(f"Resultado - {nome}", resultado_final)
            
            # Salva o resultado no disco (Exigência 6)
            cv2.imwrite(f"resultado_{nome}", resultado_final)
            
            print(f"Processado: {nome} -> salvo como resultado_{nome}")
            cv2.waitKey(0) # Espera uma tecla para passar para a próxima logo
        else:
            print(f"Erro ao carregar: {nome}")

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()