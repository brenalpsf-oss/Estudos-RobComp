class Carro:
    def __init__(self, cor, marca, modelo, ano): #construtor(é chamado novamente sempre que criamos um novo objeto)
        #tributos
        self.cor = cor   
        self.marca = marca
        self.modelo = modelo
        self.ano = ano

    def acelerar(self):
        print("O carro está acelerando.")

    def frear(self):
        print("O carro está freando.")


Meu_carro = Carro("Vermelho", "Ferrari", "458 Italia", 2020)
Meu_carro.acelerar()
Meu_carro.frear()

###############################

class Carro:
    def __init__(self, cor: str, marca: str, modelo: str, ano: int):
        self.cor = cor
        self.marca = marca
        self.modelo = modelo
        self.ano = ano

    def acelerar(self):
        print(f'O {self.modelo} está acelerando.')

    def frear(self):
        print(f'O {self.modelo} está freando.')

    @staticmethod  #usado para indicar que um método é um método estático 
    def numero_de_rodas():
        print("O carro possui 4 rodas.")

Carro.numero_de_rodas()


#################################

# Classe filha Caminhao que herda de Carro
class Caminhao(Carro):
    def __init__(self, cor: str, marca: str, modelo: str, ano: int, capacidade_carga: int):
        super().__init__(cor, marca, modelo, ano)  # Chama o construtor da classe pai
        self.capacidade_carga = capacidade_carga  # Atributo adicional

    def carregar(self, carga: int):
        if carga &lt;= self.capacidade_carga:
            print(f"Carregando {carga} toneladas no caminhão.")
        else:
            print("Carga excede a capacidade máxima do caminhão!")

    # Sobrescrevendo o numero de rodas
    @staticmethod
    def numero_de_rodas():
        print("O caminhão possui 6 rodas.")

    # Sobrescrevendo o método frear

# Exemplo de uso
carro = Carro("Vermelho", "Toyota", "Corolla", 2020)
caminhao = Caminhao("Azul", "Volvo", "FH16", 2021, 20)

carro.acelerar()
carro.numero_de_rodas()
caminhao.carregar(15)
caminhao.numero_de_rodas()


