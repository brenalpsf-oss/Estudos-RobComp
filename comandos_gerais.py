# LÊ O ARQUIVO DE IMAGEM
cv2.imread("img/img9x9_aumentada.png")

# VISUALIZANDO A IMAGEM
cv2.imshow("Imagem BGR", grid) # Visualizando a imagem
cv2.waitKey() # Segura a imagem na tela
cv2.destroyAllWindows() # Fecha as janelas antes de sair da célula de código

# CONVERTE DE BGR PARA RGB
cv2.cvtColor(grid, cv2.COLOR_BGR2RGB)

# CONVERTE DE BGR PARA TONS DE CINZA
cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# PARA VER AS DIMENSÕES DA MATRIZ
mini_grid = cv2.imread("img/img9x9.png")
print(mini_grid.shape)  # Usamos o .shape

# PARA SEPARAR OS CANAIS DE COR
cv2.split()

# PARA JUNTAR OS CANAIS DE COR
cv2.merge()

# ABRE A CAMERA DE ÍNDICE ZERO DO COMPUTADOR
cv2.VideoCapture(0)

# IMPORTA TEMPO E ABRE UM TIMER PARA ESPERAR A WEBCAM ABRIR CORRETAMENTE
import time as t
t.sleep(5) # Espera a webcam ficar pronta

# RETORNA UM PAR DE VALORES: 1o - SE A LEITURA DEU CERTO, 2o - A IMAGEM LIDA (como se fosse uma foto)
val, image = webcam.read() # Função .read()

# FECHA A WEBCAM
webcam.release()

# MOSTRA A IMAGEM DA WEBCAM (a foto tirada)
cv2.imshow("webcam", image)
cv2.waitKey()
cv2.destroyAllWindows()

# LOOP PARA VER O VÍDEO DA WEBCAM EM TEMPO REAL
webcam = cv2.VideoCapture(0)
cv2.namedWindow("cam")
while(True):
    val, image = webcam.read()
    if val:
        cv2.imshow("cam", image)
    if cv2.waitKey(1) == 27: # Aguarda 1 ms pela tecla 'ESC'
        break
            
cv2.destroyAllWindows()
webcam.release()

# PINTANDO TODOS OS PIXELS DE UMA IMAGEM
saida[:] = 255

# CRIA UMA IMAGEM COM O MESMO TAMANHO DA IMAGEM DE ENTRADA (mas com os pixels igual a 0)
saida = np.zeros_like(entrada, dtype=np.uint8)

# RETORNA OS VALORES UNICOS DE UMA MATRIZ
np.unique(saida)

# CORTANDO UMA IMAGEM
horizontal = entrada.copy()
vertical = entrada.copy()

height, width = entrada.shape

# Corte Horizontal
horizontal[:int(height/2), :] = 255

# Corte Vertical
vertical[:, int(width/2):] = 0

cv2.imshow("Entrada", entrada)
cv2.imshow("Horizontal", horizontal)
cv2.imshow("Vertical", vertical)
cv2.waitKey()
cv2.destroyAllWindows()

# ROI - Region Of Interesting - É A DERTERMINAÇÃO DE UM RETÂNGULO DE INTERESSE EM UMA IMAGEM
minx, miny = 50, 50 # Definindo os valores mínimos em x do retângulo
maxx, maxy = 250, 250 # Definindo os valores máximos em y do retângulo
yellow_bgr = (0,255,255) # Definindo a cor do retângulo
arara_corte = cv2.rectangle(arara, (minx, miny), (maxx, maxy), yellow_bgr, 2) # Desenhando o retângulo na imagem 
recorte = arara_corte[miny: maxy,minx: maxx] # Recortando o retângulo

# OBTENDO ESTATÍSTICAS DA IMAGEM
minimo = np.min(rintin_gray) # Indica o pixel mais escuro da imagem
maximo = np.max(rintin_gray) # Indica o pixel mais claro da imagem
media = np.mean(rintin_gray) # INdica o brilho médio da imagem

# OPERAÇÕES CONDICIONAIS NO NUMPY
codicionado[codicionado < media] = 0  # Transforma todos os pixels menores que o brilho médio na cor preta
codicionado[codicionado >= media] = 255  # Transforma todos os pixels maiores ou iguais ao brilho médio na cor branca

# CALCULANDO A ÁREA DA IMAGEM P&B
area = np.sum(codicionado)/255 

# SEGMENTAÇÃO DE IMAGENS

''' Mascaramento: é uma forma de segmentação onde uma imagem binária é criada a partir da imagem original,
colorida ou em tons de cinza, para indicar os pixels de interesse e separá-los dos pixels de fundo.

Chamamos a imagem binária criada de máscara ou mask. O valor preto 0 indica o pixel de fundo e o valor branco 255
indica os pixels de interesse.

Fazemos o histograma da imagem para ver a distribuição de pixels dentros dos possíveis valores de intensidade.
Assim separamos os três canais (vermelho, azul e verde) e plotamos o histrograma de cada canal, que possibilita 
visualizar a distribuição das intensidades de cada pixel, por canal. '''

# **Canal Vermelho**
plt.subplot(1,3,2)
plt.title("Canal Vermelho")
cores_r = cores_rgb[:,:,0]
plt.imshow(cores_r, cmap='gray')

''' O código acima plota a imagem original em cinza, nos permitindo visualizar a intensidade de vermelho em cada cor
da imagem original. Podemos fazer o mesmo para os canais azul e verde.'''

plt.subplot(1,3,3)
plt.title("Histograma do Canal Vermelho")
plt.hist(cores_r.flatten(), bins=256)
plt.xlim([-1,256]) # para melhor visualização do histograma
plt.show()

''' O código acima plota o histograma da intensidade de vermelho usada nos pixels. Podemos fazer o mesmo para os
canais azul e verde.'''

''' Vamos filtrar a cor verde na imagem. Para criar a máscara, usamos a função: '''

cv2.inRange()

''' Para usá-la, precisamos definir a imagem de entrada, um limite inferior (tuple) e um limite superior (tuple). A função
retorna uma imagem binária, onde os pixels que estão no intervalo são brancos e os pixels que estão fora são pretos. 

Para definir os limites inferior e superior, analisamos os histogramas da imagem de cada canal.
Vamos definir os limites do azul como 0 e 20; os limites do verde como 80 e 255 e os limites do vermelho como 0 e 50.
A escolha dos valores é arbitraria, deve-se analisar o histograma para definir a melhor faixa de valores. '''

inferior = (0,80,0) 
superior = (50,255,20)
mask = cv2.inRange(cores_rgb, inferior, superior)

cv2.imshow("Imagem BGR", cores)
cv2.imshow("Mask", mask)
cv2.waitKey()
cv2.destroyAllWindows()

''' O código acima cria a máscara e, em seguida, ilustra ela na tela. Na imagem, é possível enxergar que os pixels em branco
estão na região que antes era ocupada pela faixa verde na imagem colorida. Assim, o filtro da cor verde foi aplicado. '''


# DETECÇÃO DE CORES COM HSV

''' O espaço de cores HSV - Hue, Saturation, Value - é o mais adequado para detecção de cores em imagens, pois separa a
informação de cor (H) da infromação de luminosidade (V) e de saturação(S). Isso permite que a detecção de cores seja mais
robusta a variações de iluminação.

O canal Hue varia de 0 a 180 graus. Os canais Saturation e Value variam de 0 a 100%, é necessários converte-los de 0 a 255 
para usá-los no filtro na OpenCV.'''


# --- SNAPSHOT DE SEGMENTAÇÃO ---
hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
lower = np.array([H_min, S_min, V_min])
upper = np.array([H_max, S_max, V_max])
mask = cv2.inRange(hsv, lower, upper)

# Para aplicar a máscara e ver a imagem colorida só com a cor filtrada:
res = cv2.bitwise_and(imagem, imagem, mask=mask)