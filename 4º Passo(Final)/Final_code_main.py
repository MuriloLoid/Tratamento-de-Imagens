from PIL import Image
import os
import re

# --- CONFIGURAÇÕES DE PASTAS ---
target_folder = r"F:\Murilo\Downloads\Definitive_pdf\3º Passo\questoes_finais_prontas" 

# --- CONFIGURAÇÕES DE DETECÇÃO DE FAIXA ---
FAIXA_COR_AZUL = (64, 193, 243) 
FAIXA_COR_BRANCA = (255, 255, 255) 
TOLERANCIA = 30 
PERCENTUAL_AZUL = 0.85 

# Padronize para a maior altura para garantir que a imagem não termine antes do teste
ALTURA_PADRAO_MAX = 13 

Image.MAX_IMAGE_PIXELS = None

# ----------------- FUNÇÕES DE IDENTIFICAÇÃO DE FAIXA (SUPORTE DUPLO) -----------------

def eh_cor_proxima(pixel, cor_alvo, tolerancia):
    """Verifica se a cor de um pixel está dentro da tolerância da cor alvo."""
    r, g, b = pixel
    r_alvo, g_alvo, b_alvo = cor_alvo
    return (abs(r - r_alvo) <= tolerancia and
            abs(g - g_alvo) <= tolerancia and
            abs(b - b_alvo) <= tolerancia)

def linha_contem_cor(imagem, y, cor_alvo, tolerancia, percentual_minimo):
    """Amostra uma linha para verificar se atinge o percentual mínimo da cor alvo."""
    largura = imagem.width
    pixels_cor = 0
    for x in range(0, largura, 50): 
        if eh_cor_proxima(imagem.getpixel((x, y)), cor_alvo, tolerancia):
            pixels_cor += 1
    return (pixels_cor / (largura / 50)) >= percentual_minimo

def testar_padrao(imagem, y, branco_altura):
    """Função auxiliar para testar um padrão de (4 Azul + X Branco + 4 Azul)"""
    
    # 1. Padrão 4x Azul (Primeira Faixa)
    is_azul1 = all(linha_contem_cor(imagem, y + i, FAIXA_COR_AZUL, TOLERANCIA, PERCENTUAL_AZUL) 
                   for i in range(4))
    
    # 2. Padrão Xx Branco (Faixa Central)
    y_branco = y + 4
    is_branco = all(linha_contem_cor(imagem, y_branco + i, FAIXA_COR_BRANCA, TOLERANCIA, 0.95) 
                    for i in range(branco_altura)) 
    
    # 3. Padrão 4x Azul (Segunda Faixa)
    y_azul2 = y + 4 + branco_altura
    is_azul2 = all(linha_contem_cor(imagem, y_azul2 + i, FAIXA_COR_AZUL, TOLERANCIA, PERCENTUAL_AZUL) 
                    for i in range(4))
    
    return is_azul1 and is_branco and is_azul2

def encontrar_primeira_faixa_dupla(imagem):
    """
    Encontra o Y inicial da PRIMEIRA ocorrência do padrão,
    testando primeiro 4-5-4 e depois 4-4-4.
    """
    largura, altura = imagem.size
    y = 0

    while y < altura - ALTURA_PADRAO_MAX:
        # TESTE 1: PADRÃO 4-5-4 (Altura 13)
        if y < altura - 13:
            if testar_padrao(imagem, y, 5):
                return y # Padrão 4-5-4 encontrado!

        # TESTE 2: PADRÃO 4-4-4 (Altura 12)
        if y < altura - 12:
            if testar_padrao(imagem, y, 4):
                return y # Padrão 4-4-4 encontrado!
        
        y += 1
            
    return -1

# ----------------- LÓGICA PRINCIPAL DE REVISÃO E CORREÇÃO -----------------

def revisar_e_recortar_por_faixa(pasta):
    
    arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    print(f"Iniciando revisão em {len(arquivos)} arquivos na pasta '{pasta}'...")

    for nome_arquivo in arquivos:
        caminho_arquivo = os.path.join(pasta, nome_arquivo)
        
        try:
            imagem = Image.open(caminho_arquivo).convert('RGB')
        except Exception as e:
            print(f"ERRO: Não foi possível abrir {nome_arquivo}. {e}")
            continue

        largura, altura = imagem.size
        
        # 1. RECORTAR ALTURA (LIMPEZA POR FAIXA)
        
        y_corte = encontrar_primeira_faixa_dupla(imagem)
        
        if y_corte != -1:
            # Encontrou a faixa, corta 10px antes dela.
            y_final_recorte = y_corte - 10
            
            if y_final_recorte > 0 and y_final_recorte < altura:
                caixa_corte_y = (0, 0, largura, y_final_recorte)
                img_final = imagem.crop(caixa_corte_y)
                
                # Sobrescreve o arquivo original
                img_final.save(caminho_arquivo)
                print(f"-> {nome_arquivo}: Recortado. Conteúdo abaixo da faixa removido (Padrão: {'4-5-4' if '4-5-4' in str(y_corte) else '4-4-4'}).")
            else:
                print(f"-> {nome_arquivo}: Faixa encontrada, mas corte em Y inválido. Arquivo intocado.")
        else:
            print(f"-> {nome_arquivo}: Nenhum padrão de faixa encontrado. Arquivo intocado.")


# Inicia o processamento na pasta de questões prontas
revisar_e_recortar_por_faixa(target_folder)