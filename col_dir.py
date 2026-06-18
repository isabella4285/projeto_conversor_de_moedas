import customtkinter
from cotacao import pegar_cotacao_moeda
import config

def criar_coluna_direita(container):
    frame = customtkinter.CTkFrame(container, fg_color="#1a1a24", corner_radius=15)
    frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

    titulo_viagem = customtkinter.CTkLabel(frame, text="Sugestão de Viagem (Saindo de BRL)", font=("Verdana", 20, "bold"), text_color=config.COR_PRINCIPAL)
    titulo_viagem.pack(pady=20)

    texto_capital = customtkinter.CTkLabel(frame, text="Digite seu capital disponível (R$):", font=("Verdana", 14, "normal"))
    texto_capital.pack(pady=5)

    campo_capital = customtkinter.CTkEntry(frame, placeholder_text="Ex: 5000", width=250)
    campo_capital.pack(pady=5)

    lista_sugestoes = customtkinter.CTkScrollableFrame(frame, width=400, height=320, fg_color=config.COR_FUNDO_DROPDOWN)

    def calcular_sugestao_viagem():
        for widget in lista_sugestoes.winfo_children():
            widget.destroy()
            
        try:
            capital_brl = float(campo_capital.get())
        except ValueError:
            erro_label = customtkinter.CTkLabel(lista_sugestoes, text="Por favor, digite um valor numérico válido.", text_color="red")
            erro_label.pack(pady=10)
            return

        resultados = []

        for destino in config.DESTINOS:
            moeda_destino = destino["moeda"]
            try:
                cotacao = float(pegar_cotacao_moeda("BRL", moeda_destino))
                capital_convertido = capital_brl * cotacao
                dias_estimados = capital_convertido / destino["custo_diario_local"]
                
                resultados.append({
                    "pais": destino["pais"],
                    "dias": int(dias_estimados),
                    "valor_convertido": capital_convertido,
                    "moeda": moeda_destino
                })
            except Exception:
                continue

        resultados.sort(key=lambda x: x["dias"], reverse=True)

        if resultados:
            for res in resultados:
                texto_res = (f"📍 {res['pais']}\n"
                             f"⏱️ Rendimento estimado: {res['dias']} dias de viagem\n"
                             f"💵 Equivalente local: {res['valor_convertido']:.2f} {res['moeda']}\n"
                             f"----------------------------------------")
                label_resultado = customtkinter.CTkLabel(lista_sugestoes, text=texto_res, justify="left", font=("Verdana", 12, "normal"))
                label_resultado.pack(padx=15, pady=8, anchor="w")
        else:
            label_vazio = customtkinter.CTkLabel(lista_sugestoes, text="Não foi possível obter as cotações no momento.")
            label_vazio.pack(pady=10)

    botao_sugerir = customtkinter.CTkButton(
        frame, text="Buscar Destinos Vantajosos", command=calcular_sugestao_viagem, 
        fg_color=config.COR_PRINCIPAL, hover_color=config.COR_HOVER_DROPDOWN, width=200
    )
    botao_sugerir.pack(pady=15)
    lista_sugestoes.pack(padx=20, pady=10, fill="both", expand=True)

    return frame