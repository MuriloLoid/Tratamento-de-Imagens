from pdf2image import convert_from_path
from PIL import Image
import os
import re

# --- CONFIGURAÇÕES CRÍTICAS ---
pdf_path = r"F:\Murilo\Downloads\Definitive_pdf\1º Passo\enem2024.pdf"

# **ATUALIZE ESTE CAMINHO** com o local exato do 'bin' do Poppler no seu PC!
# Exemplo (baseado no histórico):
POPPLER_PATH = r"F:\Murilo\Downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin" 

resolucao_dpi = 300

# Margens a remover (baseado nas suas dimensões típicas)
CROP_LEFT = 276
CROP_TOP = 390
CROP_RIGHT = 276
CROP_BOTTOM = 280

# Páginas que NÃO devem ser divididas em metades (as exceções)
PAGINAS_INTEIRAS = [15, 28] 

# --- PASTAS DE TRABALHO ---
# Pasta de saída das imagens convertidas, recortadas e divididas (metades)
output_folder_temp = "provas_cortadas" 

# Aumenta o limite de segurança do Pillow para abrir imagens grandes
Image.MAX_IMAGE_PIXELS = None

# Cria a pasta necessária
os.makedirs(output_folder_temp, exist_ok=True)

print("--- 1. CONVERSÃO, RECORTE DE MARGENS E DIVISÃO (METADES) ---")
# ----------------------------------------------------------------------
try:
    images = convert_from_path(
        pdf_path,
        dpi=resolucao_dpi,
        fmt="png",
        poppler_path=POPPLER_PATH,
        paths_only=False,
    )

    for i, imagem in enumerate(images):
        numero_imagem = i + 1
        largura, altura = imagem.size
        
        # 1. RECORTAR MARGENS (Header, Footer, Laterais)
        caixa_corte_margem = (
            CROP_LEFT,
            CROP_TOP,
            largura - CROP_RIGHT,
            altura - CROP_BOTTOM
        )
        
        imagem_cortada = imagem.crop(caixa_corte_margem)
        largura_cortada, altura_cortada = imagem_cortada.size
        nome_base_arquivo = f"pagina_enem_{numero_imagem}"

        # 2. DIVISÃO EM METADES (Ou salvamento completo para exceções)
        
        if numero_imagem in PAGINAS_INTEIRAS:
            # PÁGINAS EXCEÇÃO (15, 28): Salva a página completa na pasta de metades
            nome_saida = f"{nome_base_arquivo}.png"
            caminho_saida = os.path.join(output_folder_temp, nome_saida)
            imagem_cortada.save(caminho_saida)
            print(f"Página {numero_imagem}: Salva completa (Exceção).")
            
        else:
            # PÁGINAS NORMAIS: Divide em Esquerda e Direita
            meio = largura_cortada // 2

            # Metade ESQUERDA
            esquerda = imagem_cortada.crop((0, 0, meio, altura_cortada))
            nome_esquerda = f"{nome_base_arquivo}_esquerda.png"
            esquerda.save(os.path.join(output_folder_temp, nome_esquerda))

            # Metade DIREITA
            direita = imagem_cortada.crop((meio, 0, largura_cortada, altura_cortada))
            nome_direita = f"{nome_base_arquivo}_direita.png"
            direita.save(os.path.join(output_folder_temp, nome_direita))
            
            print(f"Página {numero_imagem}: Dividida em Esquerda e Direita.")

except FileNotFoundError as e:
    print(f"\nERRO: O arquivo '{pdf_path}' ou o Poppler não foram encontrados.")
    print(f"Detalhes: {e}")
    print("Verifique se o PDF está no diretório correto e se o POPPLER_PATH está EXATO.")
except Exception as e:
    print (f"\nERRO FATAL NA CONVERSÃO: {e}")
    exit()
    
print("\nProcessamento da Etapa 1 concluído!")
print(f"As metades estão prontas na pasta '{output_folder_temp}'.")