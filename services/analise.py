import pandas as pd
from datetime import datetime

def processar_dados(df):
    # Filtra apenas linhas que são serviços de "banho"
    # O SimplesVet usa "Produto/serviço" como nome da coluna
    banhos = df[df['Produto/serviço'].str.contains('banho', case=False, na=False)].copy()
    
    # Converte data brasileira (15/04/2026)
    banhos['Data'] = pd.to_datetime(banhos['Data'], dayfirst=True, errors='coerce')
    banhos = banhos.sort_values(by=['Cliente', 'Pet', 'Data'])

    resultados = []
    hoje = datetime.now()

    for (cliente, pet), grupo in banhos.groupby(['Cliente', 'Pet']):
        datas = grupo['Data'].dropna().unique()
        if len(datas) == 0: continue
        
        ultima_visita = datas.max()
        dias_ausente = (hoje - ultima_visita).days
        
        # Cálculo da média individual (Aprendizado)
        if len(datas) > 1:
            intervalos = pd.Series(datas).sort_values().diff().dt.days.dropna()
            freq_media = round(intervalos.mean(), 1)
        else:
            freq_media = 14.0 # Default para novo cliente

        # Lógica de Status Baseada em Evidência Individual
        if dias_ausente > (freq_media + 3):
            status = "CRÍTICO (Sumido)"
        elif dias_ausente >= freq_media:
            status = "PROSPECÇÃO (No prazo)"
        else:
            status = "OK"

        resultados.append({
            "Cliente": cliente,
            "Pet": pet,
            "Última Visita": ultima_visita.strftime('%d/%m/%Y'),
            "Média Habitual": f"{freq_media} dias",
            "Dias de Ausência": dias_ausente,
            "Status": status
        })

    return pd.DataFrame(resultados).sort_values(by="Dias de Ausência", ascending=False)
