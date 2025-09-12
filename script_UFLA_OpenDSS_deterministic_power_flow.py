# -*- coding: utf-8 -*-
import opendssdirect as dss
import pandas as pd

# Caminhos dos arquivos
circuito = r"C:\Users\User\Desktop\ModelingUFLA\Master_A.dss"
arquivo_cargas_min = r"C:\Users\User\Desktop\ModelingUFLA\Loads_A.txt"
arquivo_cargas_max = r"C:\Users\User\Desktop\ModelingUFLA\Loads_B.txt"
pv1 = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem1.txt"
pv2 = r"C:\Users\User\Desktop\ModelingUFLA\PVSystem2.txt"

# Função para rodar um cenário
def rodar_cenario(descricao, arquivo_cargas, usar_DG=False):
    # Limpar circuito e carregar Master
    dss.Text.Command("Clear")
    dss.Text.Command(f"Redirect {circuito}")
    
    # Carregar o arquivo de cargas específico
    dss.Text.Command(f"Redirect {arquivo_cargas}")
    
    # Habilitar DG se solicitado
    if usar_DG:
        dss.Text.Command(f"Redirect {pv1}")
        dss.Text.Command(f"Redirect {pv2}")
    
    # Resolver fluxo de carga
    dss.Solution.Solve()
    
    # Potência total do circuito
    p_total, q_total = dss.Circuit.TotalPower()  # kW e kVar
    
    # Perdas do circuito
    perdas = dss.Circuit.Losses()  # W e var
    perdas_kw = perdas[0] / 1000
    perdas_kvar = perdas[1] / 1000
    
    # Potência total das cargas (para cálculo de % de perdas)
    carga_kw = sum(dss.Loads.kW() for load in dss.Loads.AllNames())
    
    # Tensões máxima e mínima em p.u.
    barras = dss.Circuit.AllBusNames()
    tensoes_pu = []

    for barra in barras:
        dss.Circuit.SetActiveBus(barra)
        v = dss.Bus.Voltages()         # lista [Re, Im, Re, Im, ...]
        base_kv = dss.Bus.kVBase()     # tensão base do barramento
        
        # Calcular magnitude de cada fase e converter para p.u.
        for i in range(0, len(v), 2):
            v_fase = (v[i]**2 + v[i+1]**2)**0.5
            tensoes_pu.append(v_fase / (base_kv*1000))
    
    v_max = max(tensoes_pu)
    v_min = min(tensoes_pu)
    
    # Fator de potência
    if p_total != 0:
        fp = p_total / ((p_total**2 + q_total**2)**0.5)
    else:
        fp = 0
    
    return {
        "Descrição": descricao,
        "P_total_kW": p_total,
        "Q_total_kVar": q_total,
        "V_max_pu": v_max,
        "V_min_pu": v_min,
        "FP": fp,
        "Perdas_P_kW": perdas_kw,
        "Perdas_Q_kVar": perdas_kvar,
        "Perdas_P_kW_%": (perdas_kw / p_total * 100) if carga_kw > 0 else 0,
        "Perdas_Q_kVar_%": (perdas_kvar / q_total * 100) if carga_kw > 0 else 0

    }

# --- Executar os 4 cenários ---
resultados = []

# Cenário A - mínima demanda
resultados.append(rodar_cenario("A - Sem DG", arquivo_cargas=arquivo_cargas_min, usar_DG=False))
resultados.append(rodar_cenario("A - Com DG", arquivo_cargas=arquivo_cargas_min, usar_DG=True))

# Cenário B - máxima demanda
resultados.append(rodar_cenario("B - Sem DG", arquivo_cargas=arquivo_cargas_max, usar_DG=False))
resultados.append(rodar_cenario("B - Com DG", arquivo_cargas=arquivo_cargas_max, usar_DG=True))

# Transformar em DataFrame
df = pd.DataFrame(resultados)
print(df)

# Salvar em Excel
df.to_excel(r"C:\Users\User\Desktop\resultados_cenarios.xlsx", index=False)

