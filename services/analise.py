import pandas as pd
from datetime import datetime

def processar_dados(df):
    # Padronização de nomes de colunas para evitar erros de digitação/espaços
    df.columns = [c.strip() for c in df.columns]
    
    # Filtro robusto: ignora Case (banho, BANHO, Banho)
    banhos = df[df['Produto/serviço'].str.contains('banho', case=False, na=False)].copy()
    
    if banhos.empty:
        return pd.DataFrame({"Aviso": ["Nenhum serviço contendo 'banho' foi encontrado no arquivo enviado."]})

    banhos['Data'] = pd.to_datetime(banhos['Data'], dayfirst=True, errors='coerce')
    banhos = banhos.dropna(subset=['Data']).sort_values(by=['Cliente', 'Pet', 'Data'])

    resultados = []
    hoje = datetime.now()

    for (cliente, pet), grupo in banhos.groupby(['Cliente', 'Pet']):
        datas = grupo['Data'].unique()
        ultima_visita = datas.max()
        dias_ausente = (hoje - ultima_visita).days
        
        if len(datas) > 1:
            intervalos = pd.Series(datas).sort_values().diff().dt.days.dropna()
            freq_media = round(intervalos.mean(), 1)
        else:
            freq_media = 14.0

        if dias_ausente > (freq_media + 3):
            status = "🔴 CRÍTICO"
        elif dias_ausente >= freq_media:
            status = "🟡 PROSPECÇÃO"
        else:
            status = "🟢 OK"

        resultados.append({
            "Cliente": cliente,
            "Pet": pet,
            "Última Visita": ultima_visita.strftime('%d/%m/%Y'),
            "Média (Dias)": freq_media,
            "Ausência (Dias)": dias_ausente,
            "Status": status
        })

    return pd.DataFrame(resultados).sort_values(by="Ausência (Dias)", ascending=False)
