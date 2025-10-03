from PIL import Image
import os
import re
import shutil

# --- CONFIGURAÇÕES DE PASTAS ---
input_folder = r"F:\Murilo\Downloads\Definitive_pdf\2º Passo\final"
input_filename = "enem_completo_vertical.png"
output_folder_temp = r"F:\Murilo\Downloads\Definitive_pdf\3º Passo\questoes_temporarias"     
output_folder_final = r"F:\Murilo\Downloads\Definitive_pdf\3º Passo\questoes_finais_prontas" 

# --- CONFIGURAÇÕES DE RECORTE SEQUENCIAL (FAIXA AZUL) ---
FAIXA_COR = (64, 193, 243) # Cor #40c1f3
TOLERANCIA = 30
ALTURA_FAIXA_MIN = 8 
PERCENTUAL_AZUL = 0.85

# --- CONFIGURAÇÕES DE RECORTE FINO LATERAL (DIMENSÕES REVISADAS) ---
# NOVO: Início do conteúdo principal (para remover a margem da esquerda)
CROP_INICIO_CONTEUDO_X = 528 
# NOVO: Fim do conteúdo principal (para remover margem e coluna de referência da direita)
# Se a largura total é 2100, 2100 - 529 = 1571. 
# Usaremos 1571 como o ponto final do nosso recorte de largura.
CROP_FIM_CONTEUDO_X = 1571 

EXCECOES_LATERAL = [35, 36, 77, 78, 79] # Questões que não cortam lateralmente

Image.MAX_IMAGE_PIXELS = None
os.makedirs(output_folder_temp, exist_ok=True)
os.makedirs(output_folder_final, exist_ok=True)

# ----------------- FUNÇÕES DE IDENTIFICAÇÃO DE FAIXA AZUL (COMPLETAS) -----------------

def eh_cor_proxima(pixel, cor_alvo, tolerancia):
    r, g, b = pixel
    r_alvo, g_alvo, b_alvo = cor_alvo
    return (abs(r - r_alvo) <= tolerancia and
            abs(g - g_alvo) <= tolerancia and
            abs(b - b_alvo) <= tolerancia)

def encontrar_todas_as_faixas(imagem, altura_minima, cor_alvo, tolerancia, percentual_azul):
    largura, altura = imagem.size
    faixas_encontradas = []
    x_centro = largura // 2
    y = 0
    while y < altura:
        pixels_azuis = 0
        for x in range(x_centro - 50, x_centro + 50, 10):
            if eh_cor_proxima(imagem.getpixel((x, y)), cor_alvo, tolerancia):
                pixels_azuis += 1
        
        if (pixels_azuis / 10) >= percentual_azul:
            y_inicio_faixa = y
            faixa_altura_atual = 0
            y_temp = y
            
            while y_temp < altura:
                pixels_azuis_temp = 0
                for x in range(x_centro - 50, x_centro + 50, 10):
                    if eh_cor_proxima(imagem.getpixel((x, y_temp)), cor_alvo, tolerancia):
                        pixels_azuis_temp += 1
                
                if (pixels_azuis_temp / 10) >= percentual_azul:
                    faixa_altura_atual += 1
                    y_temp += 1
                else:
                    break
            
            if faixa_altura_atual >= altura_minima:
                faixas_encontradas.append(y_inicio_faixa)
                y = y_temp + 10 
            else:
                y += 1
        else:
            y += 1
    return faixas_encontradas

# ----------------- LÓGICA PRINCIPAL: DUAS ETAPAS INTEGRADAS -----------------

def processar_recortes_completos(caminho_imagem):
    try:
        imagem = Image.open(caminho_imagem).convert('RGB')
    except Exception as e:
        print(f"Erro ao abrir a imagem: {e}")
        return

    largura, altura = imagem.size
    
    # =========================================================================
    # ETAPA 1: RECORTE SEQUENCIAL (DIVISÃO POR FAIXA AZUL)
    # =========================================================================
    
    print("--- ETAPA 1: Recorte Sequencial (Divisão por Faixa Azul) ---")
    faixas = encontrar_todas_as_faixas(imagem, ALTURA_FAIXA_MIN, FAIXA_COR, TOLERANCIA, PERCENTUAL_AZUL)
    
    if not faixas:
        print("Nenhuma faixa azul foi encontrada. Não é possível dividir as questões.")
        return
    
    print(f"Total de {len(faixas)} faixas encontradas.")
    
    num_questao_sequencial = 1
    idioma_atual = ""
    questoes_salvas_temp = []
    
    # 1. Trata o primeiro bloco (Introdução/Questão 1)
    caixa_corte_primeira = (0, 0, largura, faixas[0] - 10)
    if caixa_corte_primeira[3] > caixa_corte_primeira[1]:
        primeira_questao = imagem.crop(caixa_corte_primeira)
        nome_temp = "questao_introducao.png"
        primeira_questao.save(os.path.join(output_folder_temp, nome_temp))
        print(f"Bloco inicial salvo temporariamente: {nome_temp}")

    # 2. Corta as questões entre as faixas
    for i in range(len(faixas)):
        y_faixa_atual = faixas[i]
        y_faixa_proxima = faixas[i+1] if i + 1 < len(faixas) else altura

        caixa_corte = (0, y_faixa_atual - 10, largura, y_faixa_proxima - 10)
        
        if i == 0 and y_faixa_proxima != altura:
             caixa_corte = (0, faixas[0] - 10, largura, faixas[1] - 10)

        if caixa_corte[3] > caixa_corte[1] and num_questao_sequencial < 91:
            questao_img = imagem.crop(caixa_corte)

            # --- Lógica de NOMEAÇÃO (1 a 5, 1 a 5, 6+) ---
            # (Mantida a lógica de numeração para a Etapa 2)
            if num_questao_sequencial == 1:
                if not idioma_atual:
                    idioma_atual = input(f"A questão sequencial {num_questao_sequencial} é a número 1. Qual o idioma (ex: ingles)? ").strip().lower()
                nome_saida = f"questao_{num_questao_sequencial}_{idioma_atual}.png"
                num_questao_sequencial += 1
            elif num_questao_sequencial <= 5:
                nome_saida = f"questao_{num_questao_sequencial}_{idioma_atual}.png"
                num_questao_sequencial += 1
            elif num_questao_sequencial == 6:
                novo_idioma = input(f"A questão sequencial {num_questao_sequencial} é a número 6. Mudar idioma? (ex: espanhol) ou 'n': ").strip().lower()
                if novo_idioma != 'n' and novo_idioma != '':
                    idioma_atual = novo_idioma
                    num_questao_sequencial = 1 
                    nome_saida = f"questao_{num_questao_sequencial}_{idioma_atual}.png"
                    num_questao_sequencial += 1
                else:
                    nome_saida = f"questao_{num_questao_sequencial}.png"
                    num_questao_sequencial += 1
            else:
                nome_saida = f"questao_{num_questao_sequencial}.png"
                num_questao_sequencial += 1

            caminho_saida = os.path.join(output_folder_temp, nome_saida)
            questao_img.save(caminho_saida)
            questoes_salvas_temp.append((num_questao_sequencial - 1, nome_saida))
            print(f"Questão {num_questao_sequencial - 1} salva temporariamente: {nome_saida}")
            
    print("-" * 40)
    print("ETAPA 1 concluída.")

    # =========================================================================
    # ETAPA 2: RECORTE FINO LATERAL (CORTE DE LARGURA ÚNICA)
    # =========================================================================

    print("\n--- ETAPA 2: Recorte Fino Lateral (Conteúdo Único) ---")

    for num_questao, nome_arquivo in questoes_salvas_temp:
        caminho_entrada = os.path.join(output_folder_temp, nome_arquivo)
        caminho_saida = os.path.join(output_folder_final, nome_arquivo)
        
        try:
            questao_img = Image.open(caminho_entrada).convert('RGB')
        except Exception as e:
            print(f"ERRO: Não foi possível abrir {nome_arquivo} para corte fino. {e}")
            continue

        largura, altura = questao_img.size
        
        # 1. VERIFICA AS EXCEÇÕES (Mantém a largura total)
        if num_questao in EXCECOES_LATERAL:
            questao_img.save(caminho_saida)
            print(f"-> {nome_arquivo} (EXCEÇÃO): Copiada sem alteração de largura.")
            continue
            
        # 2. APLICA O RECORTE DE LARGURA ÚNICA (528 até 1571)
        
        # Garante que as dimensões do corte estão dentro dos limites da imagem real
        inicio_x = min(CROP_INICIO_CONTEUDO_X, largura)
        fim_x = min(CROP_FIM_CONTEUDO_X, largura)
        
        # A caixa de corte pega apenas o conteúdo principal
        caixa_corte_final = (inicio_x, 0, fim_x, altura)

        if fim_x > inicio_x:
            img_final = questao_img.crop(caixa_corte_final)
            img_final.save(caminho_saida)
            print(f"-> {nome_arquivo}: Recorte lateral ({inicio_x} a {fim_x}) aplicado e salva na pasta final.")
        else:
             print(f"-> {nome_arquivo}: AVISO! Dimensões de corte inválidas. Arquivo copiado sem alteração.")
             questao_img.save(caminho_saida)
    
    # 3. Copia o bloco de introdução
    caminho_intro_temp = os.path.join(output_folder_temp, "questao_introducao.png")
    caminho_intro_final = os.path.join(output_folder_final, "questao_introducao.png")
    if os.path.exists(caminho_intro_temp):
        shutil.copy(caminho_intro_temp, caminho_intro_final)
        print("-> Bloco de introdução copiado para a pasta final.")

    print("\nProcesso de Recorte Completo concluído!")
    print(f"As questões finais (sem coluna lateral) estão na pasta '{output_folder_final}'.")


# Inicia o processamento
caminho_completo_imagem = os.path.join(input_folder, input_filename)

if not os.path.exists(caminho_completo_imagem):
    print(f"Erro: Arquivo '{input_filename}' não encontrado na pasta '{input_folder}'.")
else:
    processar_recortes_completos(caminho_completo_imagem)