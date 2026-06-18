import customtkinter
import config
from col_esq import criar_coluna_esquerda
from col_dir import criar_coluna_direita

# Configuração da Janela Principal
customtkinter.set_appearance_mode(config.APPERANCE_MODE)
customtkinter.set_default_color_theme(config.COLOR_THEME)

janela = customtkinter.CTk()
janela.geometry("950x650")
janela.title("Conversor de Moedas & Sugestão de Viagem")

# Inicializa as duas colunas
criar_coluna_esquerda(janela)
criar_coluna_direita(janela)

# Inicia o Loop da Aplicação
janela.mainloop()