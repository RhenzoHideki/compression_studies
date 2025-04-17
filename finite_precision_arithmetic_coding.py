import numpy as np

class ArithmeticCoding:
    def __init__(self, precision=32):
        """
        Inicializa o codificador aritmético com precisão finita.
        
        Args:
            precision: Número de bits para representar um número (32bits, 64bits, etc.)
        """
        self.precision = precision
        self.whole = 2 ** precision
        self.half = self.whole // 2
        self.quarter = self.whole // 4
        self.three_quarters = 3 * self.quarter
        
    def encode(self, data, c_values, d_values, R=1):
        """
        Codificador aritmético com precisão finita.
        
        Args:
            data: Lista de símbolos a serem codificados
            c_values: Lista de valores c para cada símbolo
            d_values: Lista de valores d para cada símbolo
            R: Fator de escala para os valores c e d
            
        Returns:
            Lista de bits codificados
        """
        a = 0
        b = self.whole
        s = 0
        output = []
        
        for symbol in data:
            # Verificar se o símbolo está nos limites válidos
            if symbol >= len(c_values) or symbol < 0:
                raise ValueError(f"Símbolo {symbol} fora dos limites válidos")
                
            w = b - a
            b = a + round(w * d_values[symbol] / R)
            a = a + round(w * c_values[symbol] / R)
            
            # Loop de escalonamento e emissão de bits
            while b < self.half or a > self.half:
                if b < self.half:
                    # Emitir 0 e s uns
                    output.append(0)
                    output.extend([1] * s)
                    s = 0
                    a = 2 * a
                    b = 2 * b
                elif a > self.half:
                    # Emitir 1 e s zeros
                    output.append(1)
                    output.extend([0] * s)
                    s = 0
                    a = 2 * (a - self.half)
                    b = 2 * (b - self.half)
            
            # Loop de escalonamento e2
            while a > self.quarter and b < self.three_quarters:
                s += 1
                a = 2 * (a - self.quarter)
                b = 2 * (b - self.quarter)
        
        # Emissão final de bits
        s += 1
        if a <= self.quarter:
            output.append(0)
            output.extend([1] * s)
        else:
            output.append(1)
            output.extend([0] * s)
        
        return output
        
    def decode(self, encoded_bits, c_values, d_values, n, R=1):
        """
        Decodificador aritmético com precisão finita.
        
        Args:
            encoded_bits: Lista de bits codificados
            c_values: Lista de valores c para cada símbolo
            d_values: Lista de valores d para cada símbolo
            n: Número de símbolos possíveis (0 a n)
            R: Fator de escala para os valores c e d
            
        Returns:
            Lista de símbolos decodificados
        """
        if not encoded_bits:
            return []
            
        a = 0
        b = self.whole
        z = 0
        i = 1
        M = len(encoded_bits)
        output = []
        
        # Inicialização de z com os primeiros bits
        while i <= self.precision and i <= M:
            if i <= M and encoded_bits[i-1] == 1:
                z = z + 2**(self.precision - i)
            i += 1
        
        # Decodificação
        max_iterations = 1000  # Limite de segurança para evitar loops infinitos
        iteration_count = 0
        
        while iteration_count < max_iterations:
            iteration_count += 1
            found_match = False
            
            for j in range(n+1):  # Símbolos de 0 a n
                w = b - a
                b0 = a + round(w * d_values[j] / R)
                a0 = a + round(w * c_values[j] / R)
                
                if a0 <= z < b0:
                    output.append(j)
                    a, b = a0, b0
                    found_match = True
                    
                    if j == 0:  # Símbolo de término
                        return output
                    break
            
            if not found_match:
                print("Erro: Não foi possível decodificar os bits fornecidos.")
                break
            
            # Loop de escalonamento e1
            scaling_count = 0
            scaling_limit = 100  # Limite para evitar loops infinitos no escalonamento
            
            while (b < self.half or a > self.half) and scaling_count < scaling_limit:
                scaling_count += 1
                if b < self.half:
                    a = 2 * a
                    b = 2 * b
                    z = 2 * z
                elif a > self.half:
                    a = 2 * (a - self.half)
                    b = 2 * (b - self.half)
                    z = 2 * (z - self.half)
                
                if i <= M and encoded_bits[i-1] == 1:
                    z = z + 1
                i += 1
            
            # Loop de escalonamento e2
            scaling_count = 0
            
            while a > self.quarter and b < self.three_quarters and scaling_count < scaling_limit:
                scaling_count += 1
                a = 2 * (a - self.quarter)
                b = 2 * (b - self.quarter)
                z = 2 * (z - self.quarter)
                
                if i <= M and encoded_bits[i-1] == 1:
                    z = z + 1
                i += 1
        
        print(f"Aviso: Número máximo de iterações atingido ({max_iterations}). Decodificação pode estar incompleta.")
        return output
    
    @staticmethod
    def calculate_pmf(data):
        """
        Calcula a PMF (Função de Massa de Probabilidade) dos dados.
        
        Args:
            data: Lista de símbolos
            
        Returns:
            Dicionário com a PMF para cada símbolo
        """
        total = len(data)
        pmf = {}
        
        for symbol in data:
            if symbol in pmf:
                pmf[symbol] += 1
            else:
                pmf[symbol] = 1
        
        for symbol in pmf:
            pmf[symbol] /= total
            
        return pmf
    
    @staticmethod
    def create_c_d_values(pmf, max_symbol):
        """
        Cria os valores c e d a partir da PMF.
        
        Args:
            pmf: Dicionário com a PMF para cada símbolo
            max_symbol: O maior símbolo possível
            
        Returns:
            Tupla com listas de c_values e d_values
        """
        c_values = [0] * (max_symbol + 1)
        d_values = [0] * (max_symbol + 1)
        
        # Garantir que todos os símbolos estejam no pmf
        full_pmf = {i: pmf.get(i, 0) for i in range(max_symbol + 1)}
        
        cumulative = 0
        for symbol in range(max_symbol + 1):
            c_values[symbol] = cumulative
            cumulative += full_pmf.get(symbol, 0)
            d_values[symbol] = cumulative
        
        return c_values, d_values
        
    @staticmethod
    def bits_to_binary_string(bits):
        """Converte uma lista de bits em uma string binária."""
        return ''.join(map(str, bits))
    
    @staticmethod
    def binary_string_to_bits(binary_string):
        """Converte uma string binária em uma lista de bits."""
        return [int(bit) for bit in binary_string]

# Exemplo de uso
def example_usage():
    # Supondo que temos um alfabeto de 3 símbolos (1, 2, 3) mais o símbolo de término (0)
    precision = 32  # 32 bits de precisão
    
    # Dados a serem codificados (terminando com o símbolo 0)
    data = [1, 2, 1, 0]
    
    # Criar o codificador/decodificador
    codec = ArithmeticCoding(precision=precision)
    
    # Calcular a PMF
    pmf = codec.calculate_pmf(data)
    print(f"PMF: {pmf}")
    
    # Criar valores c e d a partir da PMF
    max_symbol = max(data)
    c_values, d_values = codec.create_c_d_values(pmf, max_symbol)
    print(f"c_values: {c_values}")
    print(f"d_values: {d_values}")
    
    # Verificar se os valores c e d são válidos
    if d_values[-1] != 1.0:
        # Normalizar se necessário
        scale = 1.0 / d_values[-1]
        d_values = [d * scale for d in d_values]
        c_values = [c * scale for c in c_values]
        print(f"Valores normalizados:")
        print(f"c_values: {c_values}")
        print(f"d_values: {d_values}")
    
    # Codificar
    encoded = codec.encode(data, c_values, d_values, R=1)
    print(f"Dados originais: {data}")
    print(f"Dados codificados: {encoded}")
    print(f"String binária: {codec.bits_to_binary_string(encoded)}")
    
    # Decodificar
    decoded = codec.decode(encoded, c_values, d_values, max_symbol, R=1)
    print(f"Dados decodificados: {decoded}")

if __name__ == "__main__":
    example_usage()