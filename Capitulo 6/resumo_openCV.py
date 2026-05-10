import cv2
import numpy as np

"""
RESUMO DE OPERAÇÕES BÁSICAS - OPENCV
Foco: Manipulação de Máscaras e Imagens 
"""

# --- 1. REDIMENSIONAR (Resize) ---
# O QUE FAZ: Muda o tamanho da imagem.
# Shape é (H, W), mas Resize pede (W, H). 
# Se inverter, a imagem estica ou dá erro de memória.
def exemplo_resize(img):
    h, w = img.shape[:2]
    # Redimensiona usando a largura primeiro, depois a altura
    img_resized = cv2.resize(img, (w, h)) 
    return img_resized


# --- 2. MÁSCARA BINÁRIA (inRange) ---
# O QUE FAZ: Cria uma imagem P&B onde o que você quer é BRANCO (255) e o resto é PRETO (0).
# LOGICA: Pixel dentro do intervalo -> 255. Fora -> 0.
def exemplo_mask(img):
    limite_inferior = np.array([250, 250, 250]) # Branco "sujo"
    limite_superior = np.array([255, 255, 255]) # Branco puro
    mask = cv2.inRange(img, limite_inferior, limite_superior)
    return mask


# --- 3. INVERSÃO LÓGICA (bitwise_not) ---
# O QUE FAZ: Inverte as cores da máscara (Negativo).
# UTILIDADE: Essencial para selecionar o fundo quando você só tem a máscara do objeto.
def exemplo_inverter(mask):
    mask_inv = cv2.bitwise_not(mask)
    return mask_inv


# --- 4. EFEITO CORTADOR DE BISCOITO (bitwise_and) ---
# O QUE FAZ: Só deixa passar a cor da imagem onde a máscara for BRANCA.
# PASSO A PASSO: 
#   - Use a mask original para recortar algo novo (fundo colorido).
#   - Use a mask_inv para "furar" a imagem original (tirar o que era branco).
def exemplo_recortar(imagem, mascara):
    # Aplica a máscara sobre a imagem
    resultado = cv2.bitwise_and(imagem, imagem, mask=mascara)
    return resultado


# --- 5. SOMA DE PIXELS / COLAGEM (add) ---
# O QUE FAZ: Soma os valores dos pixels.
# LOGICA: Pixel Colorido + Preto (0) = Pixel Colorido.
# É a "cola" final que junta as partes recortadas.
def exemplo_colagem(parte1, parte2):
    final = cv2.add(parte1, parte2)
    return final


"""
POST-IT DE CONSULTA RÁPIDA:
----------------------------------------------------------------------
| FUNÇÃO      | LEMBRETE DE PROVA                                    |
|-------------|------------------------------------------------------|
| shape       | Retorna (Altura, Largura). Cuidado na inversão!      |
| inRange     | Cria a máscara binária (Preto e Branco).             |
| bitwise_not | Inverte a máscara (Cria o negativo).                 |
| bitwise_and | Filtra a imagem usando a máscara (Recorta).          |
| add         | Faz a colagem final (Soma os recortes).              |
----------------------------------------------------------------------
"""

if __name__ == "__main__":
    print("Cheat Sheet carregado! Use as funções acima como referência no seu q2.py")