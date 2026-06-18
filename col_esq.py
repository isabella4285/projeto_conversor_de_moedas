import customtkinter
import json
import os
from moedas import nomes_moedas, conversoes_disponiveis
from cotacao import pegar_cotacao_moeda
import config

ARQUIVO_CACHE = "cotacoes_offline.json"


def carregar_cache():
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, "r") as f:
            return json.load(f)
    return {}


def salvar_no_cache(origem, destino, valor):
    cache = carregar_cache()
    chave = f"{origem}-{destino}"
    cache[chave] = valor
    with open(ARQUIVO_CACHE, "w") as f:
        json.dump(cache, f)


def criar_coluna_esquerda(container):
    dic_conversoes_disponiveis = conversoes_disponiveis()

    frame = customtkinter.CTkFrame(container, fg_color="transparent")
    frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

    titulo = customtkinter.CTkLabel(frame, text="Conversor de Moedas", font=("Verdana", 22, "bold"))
    titulo.pack(padx=10, pady=10)

    texto_moeda_origem = customtkinter.CTkLabel(frame, text="Selecione a moeda de origem",
                                                font=("Verdana", 14, "normal"))
    texto_moeda_origem.pack(padx=10, pady=5)

    def carregar_moedas_destino(moeda_selecionada):
        lista_moedas_destino = dic_conversoes_disponiveis[moeda_selecionada]
        campo_moeda_destino.configure(values=lista_moedas_destino)
        campo_moeda_destino.set(lista_moedas_destino[0])

    campo_moeda_origem = customtkinter.CTkOptionMenu(
        frame, values=list(dic_conversoes_disponiveis.keys()), command=carregar_moedas_destino,
        fg_color=config.COR_PRINCIPAL, button_color=config.COR_BOTAO_DROPDOWN,
        button_hover_color=config.COR_HOVER_DROPDOWN, text_color="white",
        dropdown_fg_color=config.COR_FUNDO_DROPDOWN, dropdown_hover_color=config.COR_PRINCIPAL,
        dropdown_text_color="white"
    )
    campo_moeda_origem.pack(padx=10, pady=5)

    texto_moeda_destino = customtkinter.CTkLabel(frame, text="Selecione a moeda de destino",
                                                 font=("Verdana", 14, "normal"))
    texto_moeda_destino.pack(padx=10, pady=5)

    campo_moeda_destino = customtkinter.CTkOptionMenu(
        frame, values=["Selecione uma moeda de origem"],
        fg_color=config.COR_PRINCIPAL, button_color=config.COR_BOTAO_DROPDOWN,
        button_hover_color=config.COR_HOVER_DROPDOWN, text_color="white",
        dropdown_fg_color=config.COR_FUNDO_DROPDOWN, dropdown_hover_color=config.COR_PRINCIPAL,
        dropdown_text_color="white"
    )
    campo_moeda_destino.pack(padx=10, pady=5)

    # --- FUNÇÃO DE CONVERSÃO PURA ---
    def converter_moeda():
        moeda_origem = campo_moeda_origem.get()
        moeda_destino = campo_moeda_destino.get()

        if moeda_origem and moeda_destino:
            avisar_modo_offline = False

            try:
                cotacao = pegar_cotacao_moeda(moeda_origem, moeda_destino)
                salvar_no_cache(moeda_origem, moeda_destino, cotacao)
            except Exception:
                cache = carregar_cache()
                chave = f"{moeda_origem}-{moeda_destino}"
                if chave in cache:
                    cotacao = cache[chave]
                    avisar_modo_offline = True
                else:
                    texto_cotacao_moeda.configure(text="Sem conexão e sem dados locais.",
                                                  font=("Verdana", 14, "normal"))
                    return

            if avisar_modo_offline:
                texto_cotacao_moeda.configure(text=f"1 {moeda_origem} = {cotacao} {moeda_destino} (Offline)",
                                              font=("Verdana", 14, "normal"))
            else:
                texto_cotacao_moeda.configure(text=f"1 {moeda_origem} = {cotacao} {moeda_destino}",
                                              font=("Verdana", 16, "normal"))

    botao_converter = customtkinter.CTkButton(
        frame, text="Converter", command=converter_moeda,
        fg_color=config.COR_BOTAO_CONVERTER, hover_color=config.COR_FUNDO_DROPDOWN
    )
    botao_converter.pack(padx=10, pady=10)

    texto_cotacao_moeda = customtkinter.CTkLabel(frame, text="")
    texto_cotacao_moeda.pack(padx=10, pady=5)

    # --- SEÇÃO SEPARADA PARA O ALERTA DE PREÇO ---
    frame_alerta = customtkinter.CTkFrame(frame, fg_color="gray15", corner_radius=8)
    frame_alerta.pack(padx=10, pady=15, fill="x")

    texto_titulo_alerta = customtkinter.CTkLabel(frame_alerta, text="Configurar Alerta de Preço",
                                                 font=("Verdana", 12, "bold"))
    texto_titulo_alerta.pack(padx=10, pady=(5, 2))

    campo_alerta = customtkinter.CTkEntry(frame_alerta, placeholder_text="Preço alvo (Ex: 5.00)", width=180)
    campo_alerta.pack(padx=10, pady=5)

    texto_status_alerta = customtkinter.CTkLabel(frame_alerta, text="", font=("Verdana", 12, "bold"))

    def checar_alerta():
        moeda_origem = campo_moeda_origem.get()
        moeda_destino = campo_moeda_destino.get()
        valor_alerta = campo_alerta.get()

        if not valor_alerta:
            texto_status_alerta.configure(text="Erro: Digite um valor primeiro.", text_color="#f1c40f")
            texto_status_alerta.pack(padx=10, pady=5)
            return

        try:
            limite = float(valor_alerta.replace(",", "."))
            # Puxa o valor do cache ou online para validar o alerta
            try:
                cotacao = pegar_cotacao_moeda(moeda_origem, moeda_destino)
            except Exception:
                cache = carregar_cache()
                cotacao = cache.get(f"{moeda_origem}-{moeda_destino}")
                if not cotacao:
                    texto_status_alerta.configure(text="Sem conexão para validar o alerta.", text_color="#f1c40f")
                    texto_status_alerta.pack(padx=10, pady=5)
                    return

            valor_atual = float(cotacao)
            if valor_atual <= limite:
                texto_status_alerta.configure(text=f"🚨 ALERTA: O {moeda_origem} atingiu o preço alvo!",
                                              text_color="#e74c3c")
            else:
                texto_status_alerta.configure(text=f"Monitorando: Preço atual ({valor_atual}) acima do limite.",
                                              text_color="#2ecc71")
        except ValueError:
            texto_status_alerta.configure(text="Erro: Digite apenas números.", text_color="#f1c40f")

        texto_status_alerta.pack(padx=10, pady=5)

    botao_alerta = customtkinter.CTkButton(
        frame_alerta, text="Ativar Alerta", command=checar_alerta,
        fg_color="#2980b9", hover_color="#3498db"
    )
    botao_alerta.pack(padx=10, pady=5)

    # --- TABELA DE MOEDAS NO FINAL ---
    titulo_lista = customtkinter.CTkLabel(frame, text="Códigos de Moedas Disponíveis", font=("Verdana", 14, "bold"))
    titulo_lista.pack(pady=(15, 5))

    lista_moedas = customtkinter.CTkScrollableFrame(frame, width=350, height=150)
    lista_moedas.pack(padx=10, pady=5, fill="both", expand=True)

    moedas_disponiveis = nomes_moedas()
    for codigo_moeda in moedas_disponiveis:
        nome_moeda = moedas_disponiveis[codigo_moeda]
        texto_moeda = customtkinter.CTkLabel(lista_moedas, text=f"{codigo_moeda}: {nome_moeda}")
        texto_moeda.pack(anchor="w", padx=10)

    return frame