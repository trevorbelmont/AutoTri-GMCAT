import re

def format_by_pattern(valor: str, mascara: str, placeholder: str = '#') -> str:
    """
    Aplica uma máscara de formatação a uma string bruta.
    
    A função primeiro remove todos os caracteres não-alfanuméricos do valor de entrada,
    e então preenche os slots definidos pelo 'placeholder' na máscara com esses caracteres.
    Caractéres na máscara que não são o placeholder são mantidos como literais (separadores). 
    Trunca caracteres à mais que so da Máscara.

    :param valor: A string de entrada (bruta, pode conter sujeira).
    :param mascara: O padrão visual (ex: "###-####").
    :param placeholder: O caractere que representa os slots de dados (default: '#').
    :return: A string formatada.
    """
    if not valor:
        return ""

    val_limpo = re.sub(r"[^a-zA-Z0-9]", "", str(valor))
    
    resultado = []
    idx_val = 0
    
    for char_mask in mascara:
        if idx_val >= len(val_limpo):
            break
            
        if char_mask == placeholder:
            resultado.append(val_limpo[idx_val])
            idx_val += 1
        else:
            resultado.append(char_mask)
            
    return "".join(resultado)





def format_by_pattern2(valor: str, mascara: str, placeholder: str = '#') -> str:
    """
    Aplica uma máscara de formatação a uma string bruta.
    
    A função sanitiza a entrada (mantendo apenas alfanuméricos) e preenche os slots 
    definidos pelo 'placeholder'. Caracteres literais da máscara são preservados.

    --- Comportamento em caso de Mismatch (Diferença de Tamanho) ---
    
    1. Entrada MENOR que o padrão (Lack): 
       Retorna a formatação parcial até onde os dados da entrada permitirem.
       Ex: format_by_pattern("123", "#####") -> "123"
       
    2. Entrada MAIOR que o padrão (Excess):
       Aplica a máscara até o fim do padrão e concatena (anexa) todos os 
       caracteres excedentes da entrada ao final da string retornada (sem formatação).
       Ex: format_by_pattern("123456", "##-##") -> "12-3456"

    :param valor: A string de entrada (bruta, pode conter sujeira).
    :param mascara: O padrão visual (ex: "###-####").
    :param placeholder: O caractere que representa os slots de dados (default: '#').
    :return: A string formatada.
    """
    if not valor:
        return ""

    val_limpo = re.sub(r"[^a-zA-Z0-9]", "", str(valor))
    
    resultado = []
    idx_val = 0
    
    for char_mask in mascara:
        if idx_val >= len(val_limpo):
            break
            
        if char_mask == placeholder:
            resultado.append(val_limpo[idx_val])
            idx_val += 1
        else:
            resultado.append(char_mask)
            
    if idx_val < len(val_limpo):
        resultado.append(val_limpo[idx_val:])
            
    return "".join(resultado)