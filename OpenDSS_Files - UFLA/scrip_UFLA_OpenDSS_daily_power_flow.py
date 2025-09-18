
# -*- coding: utf-8 -*-
import opendssdirect as dss
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- Caminhos dos arquivos ---
master_ts = r"C:\Users\User\Desktop\ModelingUFLA\Master_daily.dss"

# Cenário A
loadshape_a = r"C:\Users\User\Desktop\ModelingUFLA\LoadShape_A.txt"
loads_a = r"C:\Users\User\Desktop\ModelingUFLA\Loads_A_daily.txt"
pv1_a = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem1_daily.txt"
pv2_a = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem2_daily.txt"

# Cenário B
loadshape_b = r"C:\Users\User\Desktop\ModelingUFLA\LoadShape_B.txt"
loads_b = r"C:\Users\User\Desktop\ModelingUFLA\Loads_B_daily.txt"
pv1_b = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem1_daily.txt"
pv2_b = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem2_daily.txt"

saida_excel = r"C:\Users\User\Desktop\ModelingUFLA\Resultados\resultados_cenarios_daily.xlsx"

# Barra de entrada / alimentador
alimentador = "P1"

# --- Função para rodar um cenário de time series ---
def rodar_cenario_ts(descricao, loadshape_file, arquivo_cargas, usar_DG=False, pv1=None, pv2=None,
                     capacitor_bus=None, capacitor_kvar=None, capacitor_kv=13.8, capacitor_phases=3):
    dss.Text.Command("Clear")
    dss.Text.Command(f"Redirect {master_ts}")
    dss.Text.Command(f"Redirect {loadshape_file}")
    dss.Text.Command(f"Redirect {arquivo_cargas}")

    if usar_DG:
        if pv1 is not None:
            dss.Text.Command(f"Redirect {pv1}")
        if pv2 is not None:
            dss.Text.Command(f"Redirect {pv2}")

    if capacitor_bus is not None and capacitor_kvar is not None:
        dss.Text.Command(f"New Capacitor.CB_{descricao} Bus1={capacitor_bus} "
                         f"kV={capacitor_kv} kVar={capacitor_kvar} Phases={capacitor_phases}")

    resultados = []
    for passo in range(1, 25):
        dss.Solution.DblHour(passo - 1)
        dss.Solution.Solve()

        if not dss.Solution.Converged():
            print(f"Passo {passo} não convergiu para {descricao}")
            continue

        p_total, q_total = dss.Circuit.TotalPower()
        p_total = -p_total
        q_total = -q_total

        barras = dss.Circuit.AllBusNames()
        tensoes_pu = []

        for barra in barras:
            dss.Circuit.SetActiveBus(barra)
            v = dss.Bus.Voltages()
            base_kv = dss.Bus.kVBase()
            for i in range(0, len(v), 2):
                v_fase = (v[i]**2 + v[i+1]**2)**0.5
                tensoes_pu.append(v_fase / (base_kv*1000))

        v_max = max(tensoes_pu)
        v_min = min(tensoes_pu)
        fp = abs(p_total) / ((p_total**2 + q_total**2)**0.5) if p_total != 0 else 0
        perdas = dss.Circuit.Losses()
        perdas_kw = perdas[0] / 1000
        perdas_kvar = perdas[1] / 1000

        dss.Circuit.SetActiveBus(alimentador)
        v_alim = dss.Bus.Voltages()
        base_kv_alim = dss.Bus.kVBase()
        tensoes_alim = []
        for i in range(0, len(v_alim), 2):
            v_fase = (v_alim[i]**2 + v_alim[i+1]**2)**0.5
            tensoes_alim.append(v_fase / (base_kv_alim*1000))
        v_alim_pu = sum(tensoes_alim) / len(tensoes_alim)

        resultados.append({
            "Cenario": descricao,
            "Hora": passo,
            "P_total_kW": p_total,
            "Q_total_kVar": q_total,
            "V_max_pu": v_max,
            "V_min_pu": v_min,
            "V_alim": v_alim_pu,
            "FP": fp,
            "Perdas_P_kW": perdas_kw,
            "Perdas_Q_kVar": perdas_kvar
        })

    return resultados

# --- Função para otimizar banco de capacitores ---
def otimizar_banco_capacitor(descricao_base, loadshape_file, arquivo_cargas, usar_DG=False, pv1=None, pv2=None,
                             capacitor_unit=100, v_min_lim=0.95, v_max_lim=1.05, max_iterations=20):
    resultados_iter = []
    capacitor_kvar_atual = 0
    pf_medio_anterior = 0
    capacitor_otimo = 0
    iteracao = 0
    continua = True
    
    while continua and iteracao < max_iterations:
        iteracao += 1
        capacitor_kvar_atual += capacitor_unit
        descricao_cenario = f"{descricao_base}_{capacitor_kvar_atual}kVar"

        resultados = rodar_cenario_ts(descricao_cenario, loadshape_file, arquivo_cargas,
                                      usar_DG=usar_DG, pv1=pv1, pv2=pv2,
                                      capacitor_bus=alimentador,
                                      capacitor_kvar=capacitor_kvar_atual,
                                      capacitor_kv=13.8, capacitor_phases=3)
        
        tensoes = [r["V_max_pu"] for r in resultados] + [r["V_min_pu"] for r in resultados]
        pf_medio = sum(r["FP"] for r in resultados)/len(resultados)
        p_total = [r["P_total_kW"] for r in resultados]
        q_total = [r["Q_total_kVar"] for r in resultados]
        
        # Verificar se há algum valor negativo e armazenar esses valores
        q_negativos = [q for q in q_total if q < 0]

        # Criar q_ref: None se não houver negativo, ou lista dos valores negativos
        q_ref = q_negativos if q_negativos else None

        # Critérios de parada
        if max(tensoes) > v_max_lim or min(tensoes) < v_min_lim:
            print(f"Iteração {iteracao}: tensão fora do limite. Parando.")
            break
        if q_ref is not None:
            print(f"Iteração {iteracao}: sobrecompensação. Parando.")
            break
        if pf_medio <= pf_medio_anterior:
            print(f"Iteração {iteracao}: fator de potência não melhorou. Parando.")
            break

        resultados_iter.append({
            "Iteracao": iteracao,
            "Capacitor_kVAr": capacitor_kvar_atual,
            "PF_medio": pf_medio,
            "P_total_kW": p_total,
            "Q_total_kVar": q_total,
            "V_max_pu": max(r["V_max_pu"] for r in resultados),
            "V_min_pu": min(r["V_min_pu"] for r in resultados)
        })

        pf_medio_anterior = pf_medio
        capacitor_otimo = capacitor_kvar_atual

    # Salvar capacitor ótimo
    print(f"Capacitor ótimo encontrado: {capacitor_otimo} kVAr")

    df_iter = pd.DataFrame(resultados_iter)
    arquivo_saida = f"C:\Users\User\Desktop\ModelingUFLA\Resultados\resultados_otimizacao_{descricao_base}.xlsx"
    df_iter.to_excel(arquivo_saida, index=False)
    print(f"Resultados de otimização salvos em: {arquivo_saida}")
    
    return resultados_iter

# --- Executar cenários normais ---
todos_resultados = []
todos_resultados += rodar_cenario_ts("A - Sem DG", loadshape_a, loads_a, False)
todos_resultados += rodar_cenario_ts("A - Com DG", loadshape_a, loads_a, True, pv1_a, pv2_a)
todos_resultados += rodar_cenario_ts("BC_A", loadshape_a, loads_a, True, pv1_a, pv2_a, capacitor_bus=alimentador, capacitor_kvar=300)
todos_resultados += rodar_cenario_ts("B - Sem DG", loadshape_b, loads_b, False)
todos_resultados += rodar_cenario_ts("B - Com DG", loadshape_b, loads_b, True, pv1_b, pv2_b)
todos_resultados += rodar_cenario_ts("BC_B", loadshape_b, loads_b, True, pv1_b, pv2_b, capacitor_bus=alimentador, capacitor_kvar=400)

# Salvar resultados dos cenários normais
df = pd.DataFrame(todos_resultados)
df.to_excel(saida_excel, index=False)
print(f"Resultados salvos em: {saida_excel}")

# --- Executar otimização de banco de capacitores ---
resultados_BC_A = otimizar_banco_capacitor("BC_A", loadshape_a, loads_a, usar_DG=True, pv1=pv1_a, pv2=pv2_a)
resultados_BC_B = otimizar_banco_capacitor("BC_B", loadshape_b, loads_b, usar_DG=True, pv1=pv1_b, pv2=pv2_b)







# ------------------------ EXIBIÇÃO DE RESULTADOS -----------------------------




# --- Filtrar DataFrames por cenário ---
df_a_sem = df[df["Cenario"] == "A - Sem DG"]
df_a_com = df[df["Cenario"] == "A - Com DG"]
df_b_sem = df[df["Cenario"] == "B - Sem DG"]
df_b_com = df[df["Cenario"] == "B - Com DG"]
df_c_1 = df[df["Cenario"] == "BC_A"]
df_c_2 = df[df["Cenario"] == "BC_B"]



# --- Função para configurar os gráficos -------------------------------------
def configurar_plot(xlabel, ylabel=None, ylim=None, yticks=None, xticks=None, nome_arquivo=None):
    fig, ax = plt.subplots(figsize=(3.5, 3.5)) 
    fig.subplots_adjust(left=0.13, bottom=0.15, right=0.97, top=0.9)  
    ax.grid(True)
    ax.set_xlabel(xlabel, fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    if ylim:
        ax.set_ylim(ylim)
    if yticks is not None:
        ax.set_yticks(yticks)
    if xticks is not None:
        ax.set_xticks(xticks)
    ax.tick_params(axis="both", labelsize=9)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    if nome_arquivo:
        plt.savefig(nome_arquivo, dpi=300, bbox_inches="tight")
    return fig, ax





# ------------------------ Potência Ativa ----------------------------------

# --- Cenário C - Potência Ativa ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[-1000, 1000],
    yticks=range(-1000, 1001, 500),
    xticks=range(0, 25, 4),
    nome_arquivo="result_P_scenarioC.png"
)

ax.plot(df_a_sem["Hora"], df_a_sem["P_total_kW"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_a_com["Hora"], df_a_com["P_total_kW"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_1["Hora"], df_c_1["P_total_kW"], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_P_cenarioC2.png", dpi=300, bbox_inches="tight")
plt.show()



# --- Cenário D - Potência Ativa ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[0, 2000],
    yticks=range(0, 2001, 500),
    xticks=range(0, 25, 4),
    nome_arquivo="result_P_scenarioC.png"
)

ax.plot(df_b_sem["Hora"], df_b_sem["P_total_kW"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_b_com["Hora"], df_b_com["P_total_kW"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_2["Hora"], df_c_2["P_total_kW"], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_P_cenarioD2.png", dpi=300, bbox_inches="tight")
plt.show()







# ------------------------ Potência Reativa ----------------------------------
# --- Cenário C - Potência Reativa ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[-200, 800],
    yticks=range(-200, 801, 200),
    xticks=range(0, 25, 4),
    nome_arquivo="result_Q_scenarioC.png"
)

ax.plot(df_a_sem["Hora"], df_a_sem["Q_total_kVar"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_a_com["Hora"], df_a_com["Q_total_kVar"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_1["Hora"], df_c_1["Q_total_kVar"], color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_Q_cenarioC2.png", dpi=300, bbox_inches="tight")
plt.show()



# --- Cenário D - Potência Reativa ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[-200, 800],
    yticks=range(-200, 801, 200),
    xticks=range(0, 25, 4),
    nome_arquivo="result_Q_scenarioD.png"
)

ax.plot(df_b_sem["Hora"], df_b_sem["Q_total_kVar"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_b_com["Hora"], df_b_com["Q_total_kVar"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_2["Hora"], df_c_2["Q_total_kVar"], color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_Q_cenarioD2.png", dpi=300, bbox_inches="tight")
plt.show()









# ------------------------Fator de Potência ----------------------------------

# --- Cenário C - Fator de Potência ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[0, 1.2],
    yticks=[i/5 for i in range(0, 7)],  # 0, 0.2, 0.4, ..., 1.2
    xticks=range(0, 25, 4),
    nome_arquivo="result_FP_cenarioC.png"
)

#ax.plot(time, FP_ref, '.-k', linewidth=0.5)
ax.plot(df_a_sem["Hora"], df_a_sem["FP"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_a_com["Hora"], df_a_com["FP"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_1["Hora"], df_c_1["FP"], color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], color=[0.2081, 0.1663, 0.5292], linewidth=1.5)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_FP_cenarioC.png", dpi=300, bbox_inches="tight")
plt.show()


# --- Cenário D - Fator de Potência ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[0, 1.2],
    yticks=[i/5 for i in range(0, 7)],
    xticks=range(0, 25, 4),
    nome_arquivo="result_FP_cenarioD.png"
)

#ax.plot(time, FP_ref, '.-k', linewidth=0.5)
ax.plot(df_b_sem["Hora"], df_b_sem["FP"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_b_com["Hora"], df_b_com["FP"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_2["Hora"], df_c_2["FP"], color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], color=[0.2081, 0.1663, 0.5292], linewidth=1.5)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_FP_cenarioD.png", dpi=300, bbox_inches="tight")
plt.show()



# ------------------------ Perfil de Tensão ----------------------------------

# --- Cenário C - Perfil de TEnsão ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[0.98, 1.01],
    yticks=np.arange(0.98, 1.0101, 0.005), 
    xticks=range(0, 25, 4),
    nome_arquivo="result_tensoes_cenarioC.png"
)

ax.plot(df_a_sem["Hora"], df_a_sem["V_alim"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_a_com["Hora"], df_a_com["V_alim"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_1["Hora"], df_c_1["V_alim"], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_tensoes_cenarioC.png", dpi=300, bbox_inches="tight")
plt.show()



# --- Cenário D - Perfil de Tensão ---
fig, ax = configurar_plot(
    xlabel="Time [h]",
    ylim=[0.98, 1.01],
    yticks=np.arange(0.98, 1.0101, 0.005),
    xticks=range(0, 25, 4),
    nome_arquivo="result_tensoes_cenarioD.png"
)

ax.plot(df_b_sem["Hora"], df_b_sem["V_alim"], color=[0.388, 0.588, 0.709], linewidth=1.5)
ax.plot(df_b_com["Hora"], df_b_com["V_alim"], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
ax.plot(df_c_2["Hora"], df_c_2["V_alim"], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

# Linhas fictícias para legenda
h1, = ax.plot([], [], color=[0.388, 0.588, 0.709], linewidth=1.5)
h2, = ax.plot([], [], color=[0.6082, 0.8610, 0.2038], linewidth=1.5)
h3, = ax.plot([], [], "--", color=[0.2081, 0.1663, 0.5292], linewidth=1.0)

ax.legend([h1, h2, h3], ["Model", "DG", "DG and BC"], loc="upper center", ncol=3, fontsize=9, frameon=True)

plt.savefig(r"C:\Users\User\Desktop\ModelingUFLA\Resultados\result_tensoes_cenarioD.png", dpi=300, bbox_inches="tight")
plt.show()




