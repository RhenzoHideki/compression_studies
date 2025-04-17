import numpy as np
from fractions import Fraction

class CompressionAlgorithm:
    def __init__(self, precision="infinite"):
        self.precision = precision
        # Se quisermos trabalhar com precisão "infinita", usamos a classe Fraction
        # Se não, podemos usar float com alta precisão

    def encode(self, data, c_values, d_values):
        """
        Encoder para o algoritmo de compressão
        
        Args:
            data: Lista de símbolos a serem codificados (valores de 0 a n-1)
            c_values: Lista de valores c para cada símbolo
            d_values: Lista de valores d para cada símbolo
            
        Returns:
            Lista de bits codificados
        """
        # Inicialização
        a = Fraction(0, 1)
        b = Fraction(1, 1)
        output = []
        
        # Para cada símbolo na entrada
        for symbol in data:
            # Cálculo do intervalo
            w = b - a
            b = a + w * d_values[symbol]
            a = a + w * c_values[symbol]
            
            # Emissão de bits
            s = 0
            while True:
                if b <= Fraction(1, 2):
                    # Emitir 0
                    output.append(0)
                    a = 2 * a
                    b = 2 * b
                    s += 1
                elif a >= Fraction(1, 2):
                    # Emitir 1
                    output.append(1)
                    a = 2 * (a - Fraction(1, 2))
                    b = 2 * (b - Fraction(1, 2))
                    s += 1
                else:
                    break
        
        # Emissão final de bits
        if a <= Fraction(1, 4):
            output.append(0)
            # Emitir s uns
            output.extend([1] * s)
        else:
            output.append(1)
            # Emitir s zeros
            output.extend([0] * s)
            
        return output
    
    def decode(self, encoded_bits, c_values, d_values, n):
        """
        Decoder para o algoritmo de compressão
        
        Args:
            encoded_bits: Lista de bits codificados
            c_values: Lista de valores c para cada símbolo
            d_values: Lista de valores d para cada símbolo
            n: Número de símbolos possíveis
            
        Returns:
            Lista de símbolos decodificados
        """
        # Inicialização
        a = Fraction(0, 1)
        b = Fraction(1, 1)
        output = []
        
        # Converter os bits codificados em um número z entre 0 e 1
        z = Fraction(0, 1)
        for i, bit in enumerate(encoded_bits):
            z += Fraction(bit, 2**(i+1))
        
        # Decodificação
        while True:
            found_match = False
            for j in range(n+1):  # Assumindo símbolos de 0 a n
                w = b - a
                b0 = a + w * d_values[j]
                a0 = a + w * c_values[j]
                
                if a0 <= z < b0:
                    output.append(j)
                    a, b = a0, b0
                    found_match = True
                    
                    if j == 0:  # Símbolo de término
                        return output  # Retornar todos os símbolos, incluindo o 0 final
                    break
            
            if not found_match:
                # Se não encontrou nenhum intervalo que contenha z, algo está errado
                print("Erro: Não foi possível decodificar os bits fornecidos.")
                break
    
    @staticmethod
    def bits_to_binary_string(bits):
        """Converte uma lista de bits em uma string binária."""
        return ''.join(map(str, bits))
    
    @staticmethod
    def binary_string_to_bits(binary_string):
        """Converte uma string binária em uma lista de bits."""
        return [int(bit) for bit in binary_string]

# Exemplo de uso:
def example_usage():
    # Supondo que temos um alfabeto de 3 símbolos (0, 1, 2) mais o símbolo de término (3)
    # Os valores c e d definem os intervalos para cada símbolo
    c_values = [0, 0.25, 0.5, 0.75]  # Para símbolos 0, 1, 2, 3
    d_values = [0.25, 0.5, 0.75, 1.0]
    
    # Fractions para precisão "infinita"
    c_values_frac = [Fraction(0, 1), Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)]
    d_values_frac = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1)]
    
    # Dados a serem codificados (terminando com o símbolo 0)
    #data = [1, 2, 1, 0]
    data = [1, 3, 2, 1, 3, 2, 1, 1, 3, 2, 0]
    # Criar o codificador/decodificador
    codec = CompressionAlgorithm(precision="infinite")
    
    # Codificar
    encoded = codec.encode(data, c_values_frac, d_values_frac)
    print(f"Dados originais: {data}")
    print(f"Dados codificados: {encoded}")
    print(f"String binária: {codec.bits_to_binary_string(encoded)}")
    
    # Decodificar
    decoded = codec.decode(encoded, c_values_frac, d_values_frac, 3)
    print(f"Dados decodificados: {decoded}")

if __name__ == "__main__":
    example_usage()