import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import zipfile
import shutil
import platform
from pathlib import Path
import sys

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DIRETORIO_TPS = os.path.join(BASE_DIR, "arquivos")
# CAMINHO_EXE = os.path.join(BASE_DIR, "ConvertRinex", "tps2rin.exe")
# DESTINO_ZIP = os.path.join(BASE_DIR, "resultados_rinex")
# RESULTADO_VOOS = os.path.join(BASE_DIR, "resultados_voos")
# ICONE_PATH = os.path.join(BASE_DIR, "img", "icon.png")

# Pasta Documentos do usuário (funciona em Windows e Linux)
DOCUMENTOS = str(Path.home() / "Documentos")

# Criar subpastas personalizadas
DIRETORIO_TPS = os.path.join(DOCUMENTOS, "cartografia_arquivos")
DESTINO_ZIP = os.path.join(DOCUMENTOS, "cartografia_resultados_rinex")
RESULTADO_VOOS = os.path.join(DOCUMENTOS, "cartografia_resultados_voos")

# Cria as pastas, se não existirem
for pasta in [DIRETORIO_TPS, DESTINO_ZIP, RESULTADO_VOOS]:
    try:
        os.makedirs(pasta, exist_ok=True)
    except Exception as e:
        print(f"❌ Erro ao criar pasta {pasta}: {e}")

# Caminhos que continuam relativos ao executável
# BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
# CAMINHO_EXE = os.path.join(BASE_DIR, "ConvertRinex", "tps2rin.exe")
# #ICONE_PATH = os.path.join(BASE_DIR, "img", "icon.png")
# if getattr(sys, 'frozen', False):
#     BASE_DIR = os.path.dirname(sys.executable)
#     RESOURCE_DIR = sys._MEIPASS  # Onde o PyInstaller extrai arquivos internos
# else:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     RESOURCE_DIR = os.path.join(BASE_DIR, "img")

# ICONE_PATH = os.path.join(RESOURCE_DIR, "icon.png")
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    ICONE_PATH = os.path.join(sys._MEIPASS, "img", "icon.png")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICONE_PATH = os.path.join(BASE_DIR, "img", "icon.png")

CAMINHO_EXE = os.path.join(BASE_DIR, "ConvertRinex", "tps2rin.exe")

def executar_conversao():
    if not os.path.isdir(DIRETORIO_TPS):
        messagebox.showerror("Erro", f"Diretório inválido:\n{DIRETORIO_TPS}")
        return
    if not os.path.isfile(CAMINHO_EXE):
        messagebox.showerror("Erro", f"Executável inválido:\n{CAMINHO_EXE}")
        return

    arquivos_tps = [f for f in os.listdir(DIRETORIO_TPS) if f.lower().endswith(".tps")]
    if not arquivos_tps:
        messagebox.showinfo("Aviso", "Nenhum arquivo .tps encontrado.")
        return

    log_path = os.path.join(DIRETORIO_TPS, "log_conversao.txt")
    with open(log_path, "w") as log_file:
        log_file.write(f"Conversão iniciada em: {DIRETORIO_TPS}\n")

        for arquivo in arquivos_tps:
            texto_saida.insert(tk.END, f"📄 Processando {arquivo}...\n")
            texto_saida.update()

            arquivos_antes = set(f for f in os.listdir(DIRETORIO_TPS) if f.endswith((".25o", ".25n", ".25g")))

            try:
                comando = []
                if platform.system() == "Linux":
                    comando = ["wine", CAMINHO_EXE, "-v", "2.11", arquivo]
                elif platform.system() == "Windows":
                    comando = [CAMINHO_EXE, "-v", "2.11", arquivo]
                else:
                    texto_saida.insert(tk.END, f"❌ Sistema não suportado: {platform.system()}\n")
                    return

                resultado = subprocess.run(
                    comando,
                    cwd=DIRETORIO_TPS,
                    capture_output=True,
                    text=True
                )
                log_file.write(f"\n===== Conversão de {arquivo} =====\n")
                log_file.write(resultado.stdout + resultado.stderr)

                if resultado.returncode == 0:
                    texto_saida.insert(tk.END, f"✅ Conversão de {arquivo} concluída.\n")
                    arquivos_depois = set(f for f in os.listdir(DIRETORIO_TPS) if f.endswith((".25o", ".25n", ".25g")))
                    novos_arquivos = list(arquivos_depois - arquivos_antes)

                    if novos_arquivos:
                        zip_name = os.path.splitext(arquivo)[0] + ".zip"
                        zip_path = os.path.join(DIRETORIO_TPS, zip_name)

                        with zipfile.ZipFile(zip_path, 'w') as zipf:
                            for arq in novos_arquivos:
                                full_path = os.path.join(DIRETORIO_TPS, arq)
                                zipf.write(full_path, arcname=arq)
                                os.remove(full_path)
                                texto_saida.insert(tk.END, f"🗑️ Removido: {arq}\n")

                        final_path = os.path.join(DESTINO_ZIP, zip_name)
                        os.replace(zip_path, final_path)
                        texto_saida.insert(tk.END, f"📦 ZIP movido para:\n→ {final_path}\n")
                    else:
                        texto_saida.insert(tk.END, f"⚠️ Nenhum arquivo .25o/.25n/.25g gerado.\n")
                else:
                    texto_saida.insert(tk.END, f"❌ Erro na conversão de {arquivo}. Veja o log.\n")
            except Exception as e:
                texto_saida.insert(tk.END, f"❌ Falha inesperada: {str(e)}\n")

            texto_saida.insert(tk.END, "-" * 50 + "\n")
            texto_saida.update()

        texto_saida.insert(tk.END, f"✅ Processamento finalizado. Log salvo em:\n{log_path}\n")
        texto_saida.yview_moveto(1)

# def extrair_arquivos_rgb():
#     pasta_origem = filedialog.askdirectory(title="Selecionar pasta com subpastas .jpg/.png")
#     if not pasta_origem:
#         return

#     texto_saida.insert(tk.END, f"🔍 Buscando arquivos RGB (.jpg/.png) em: {pasta_origem}\n")
#     total = 0

#     for root, _, files in os.walk(pasta_origem):
#         for file in files:
#             if file.lower().endswith((".jpg", ".jpeg", ".png")):
#                 origem = os.path.join(root, file)
#                 destino = os.path.join(RESULTADO_VOOS, file)
#                 try:
#                     shutil.copy2(origem, destino)
#                     texto_saida.insert(tk.END, f"📁 Copiado: {file}\n")
#                     total += 1
#                 except Exception as e:
#                     texto_saida.insert(tk.END, f"❌ Erro ao copiar {file}: {str(e)}\n")

#     if total == 0:
#         texto_saida.insert(tk.END, "⚠️ Nenhuma imagem RGB encontrada.\n")
#     else:
#         texto_saida.insert(tk.END, f"✅ {total} arquivos RGB copiados para: {RESULTADO_VOOS}\n")
#     texto_saida.yview_moveto(1)

def extrair_arquivos_tif():
    pasta_origem = filedialog.askdirectory(title="Selecionar pasta com subpastas .tif")
    if not pasta_origem:
        return

    texto_saida.insert(tk.END, f"🔍 Buscando arquivos .tif em: {pasta_origem}\n")
    total = 0

    for root, _, files in os.walk(pasta_origem):
        for file in files:
            if file.lower().endswith(".tif"):
                origem = os.path.join(root, file)
                destino = os.path.join(RESULTADO_VOOS, file)
                try:
                    shutil.copy2(origem, destino)
                    texto_saida.insert(tk.END, f"📁 Copiado: {file}\n")
                    total += 1
                except Exception as e:
                    texto_saida.insert(tk.END, f"❌ Erro ao copiar {file}: {str(e)}\n")

    if total == 0:
        texto_saida.insert(tk.END, "⚠️ Nenhum arquivo .tif encontrado.\n")
    else:
        texto_saida.insert(tk.END, f"✅ {total} arquivos .tif copiados para: {RESULTADO_VOOS}\n")
    texto_saida.yview_moveto(1)

janela = tk.Tk()
janela.title("Operadores - Back Office Cartography - Psyche Aerospace")
janela.geometry("740x520")
janela.configure(bg="#0A1F44")
janela.resizable(False, False)

frame_topo = tk.Frame(janela, bg="#0A1F44")
frame_topo.pack(pady=(10, 5), padx=10, fill='x')

frame_logo = tk.Frame(frame_topo, bg="#0A1F44")
frame_logo.pack(side=tk.RIGHT, padx=20)

try:
    imagem_original = Image.open(ICONE_PATH)
    imagem_redimensionada = imagem_original.resize((100, 100))
    imagem_logo = ImageTk.PhotoImage(imagem_redimensionada)
    label_logo = tk.Label(frame_logo, image=imagem_logo, bg="#0A1F44")
    label_logo.pack()
except Exception as e:
    print(f"Erro ao carregar o ícone: {e}")

frame_botoes = tk.Frame(frame_topo, bg="#0A1F44")
frame_botoes.pack(side=tk.LEFT, padx=20)

botao_converter = tk.Button(frame_botoes, text="Conversão RINEX", command=executar_conversao,
                            bg="#1E293B", fg="white", height=1, width=70, font=("Helvetica", 9, "bold"))
botao_converter.pack(pady=(5, 5), fill='x', expand=True)

botao_extrair = tk.Button(frame_botoes, text="Extrair Imagens Drone Multiespectral", command=extrair_arquivos_tif,
                          bg="#1E293B", fg="white", height=1, width=70, font=("Helvetica", 9, "bold"))
botao_extrair.pack(pady=(0, 5), fill='x', expand=True)

# botao_extrair_rgb = tk.Button(frame_botoes, text="Extrair Imagens Drone RGB", command=extrair_arquivos_rgb,
#                               bg="#1E293B", fg="white", height=1, width=70, font=("Helvetica", 9, "bold"))
# botao_extrair_rgb.pack(pady=(0, 5), fill='x', expand=True)

texto_saida = scrolledtext.ScrolledText(janela, wrap=tk.WORD, width=100, height=25)
texto_saida.pack(padx=10, pady=(0, 10), fill='both', expand=True)

janela.mainloop()
