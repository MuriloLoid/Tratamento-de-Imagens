from PIL import Image
import os
import re

# --- CONFIGURAÇÕES DE PASTAS ---
input_folder = r"F:\Murilo\Downloads\Definitive_pdf\1º Passo\provas_cortadas" 
output_folder_concatenadas = r"F:\Murilo\Downloads\Definitive_pdf\2º Passo\concatenadas" 
output_folder_final = r"F:\Murilo\Downloads\Definitive_pdf\2º Passo\final"          
output_filename = "enem_completo_vertical.png"

# Páginas que NÃO devem ser divididas (as exceções que estão inteiras)
PAGINAS_INTEIRAS = [15, 28] 

# --- NOVO: PÁGINAS A SEREM IGNORADAS (LIXO) ---
PAGINAS_EXCLUIDAS = [1, 32] 
# ---------------------------------------------

Image.MAX_IMAGE_PIXELS = None

os.makedirs(output_folder_concatenadas, exist_ok=True)
os.makedirs(output_folder_final, exist_ok=True)

def get_page_number(filename):
    """Extrai o número da página para ordenação."""
    match = re.search(r'pagina_enem_(\d+)', filename)
    return int(match.group(1)) if match else 9999

# ----------------------------------------------------------------------
print("1. Concatenação de Questões (Direita ABAIXO da Esquerda)")
# ----------------------------------------------------------------------
paginas = {}
try:
    # 1.1. Agrupa os arquivos por número de página
    for filename in os.listdir(input_folder):
        match = re.search(r'pagina_enem_(\d+)', filename)
        if match:
            page_num = int(match.group(1))
            
            # --- FILTRO: IGNORA AS PÁGINAS EXCLUÍDAS ---
            if page_num in PAGINAS_EXCLUIDAS:
                print(f"Página {page_num}: IGNORADA (Excluída pelo usuário).")
                continue
            # ------------------------------------------
            
            if page_num not in paginas: 
                paginas[page_num] = {}
            
            if '_esquerda.png' in filename:
                paginas[page_num]['esquerda'] = filename
            elif '_direita.png' in filename:
                paginas[page_num]['direita'] = filename
            elif page_num in PAGINAS_INTEIRAS:
                paginas[page_num]['completa'] = filename

except FileNotFoundError:
    print(f"\nERRO: A pasta de entrada '{input_folder}' não foi encontrada.")
    exit()

# 1.2. Processa a concatenação vertical para cada página
imagens_concatenadas_ordenadas = []

for page_num in sorted(paginas.keys()):
    files = paginas[page_num]
    nome_saida = f"pagina_enem_{page_num}_reconstruida.png"
    caminho_saida = os.path.join(output_folder_concatenadas, nome_saida)
    
    if 'completa' in files:
        # Páginas que já estavam inteiras (exceções)
        img = Image.open(os.path.join(input_folder, files['completa']))
        img.save(caminho_saida)

    elif 'esquerda' in files and 'direita' in files:
        # Páginas que precisam de concatenação
        left_path = os.path.join(input_folder, files['esquerda'])
        right_path = os.path.join(input_folder, files['direita'])
        
        img_left = Image.open(left_path)
        img_right = Image.open(right_path)

        largura_total = max(img_left.width, img_right.width)
        altura_total = img_left.height + img_right.height

        nova_imagem = Image.new('RGB', (largura_total, altura_total), 'white')
        
        # 1. ESQUERDA no topo
        nova_imagem.paste(img_left, (0, 0))             
        
        # 2. DIREITA ABAIXO da esquerda
        nova_imagem.paste(img_right, (0, img_left.height)) 
        
        nova_imagem.save(caminho_saida)
    
    else:
        # Ignora páginas incompletas que não são exceções
        continue

    imagens_concatenadas_ordenadas.append((page_num, nome_saida))
    print(f"Página {page_num}: Reconstruída OK.")


# ----------------------------------------------------------------------
print("2. Concatenação Vertical (Criando Imagem Gigante)")
# ----------------------------------------------------------------------

if not imagens_concatenadas_ordenadas:
    print("ERRO: Nenhuma página para criar a imagem final. Processo parado.")
    exit()

# 2.1. Calcula as dimensões finais da imagem gigante
imagens_ordenadas_por_nome = [f[1] for f in imagens_concatenadas_ordenadas]

try:
    larguras = [Image.open(os.path.join(output_folder_concatenadas, f)).width for f in imagens_ordenadas_por_nome]
    alturas = [Image.open(os.path.join(output_folder_concatenadas, f)).height for f in imagens_ordenadas_por_nome]
except Exception as e:
    print(f"ERRO ao calcular dimensões: {e}")
    exit()

largura_total = max(larguras)
altura_total = sum(alturas)

# 2.2. Concatena verticalmente todas as páginas reconstruídas
imagem_final = Image.new('RGB', (largura_total, altura_total), 'white')

y_offset = 0
for nome_arquivo in imagens_ordenadas_por_nome:
    img = Image.open(os.path.join(output_folder_concatenadas, nome_arquivo))
    
    x_offset = (largura_total - img.width) // 2
    
    imagem_final.paste(img, (x_offset, y_offset))
    y_offset += img.height

output_path = os.path.join(output_folder_final, output_filename)
imagem_final.save(output_path)

print(f"\nIMAGEM GIGANTE CRIADA COM SUCESSO: {output_path}")
print("A próxima etapa é o recorte sequencial das questões (Etapa 3).")