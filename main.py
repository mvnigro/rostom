import pandas as pd
import numpy as np
import pdfkit

df = pd.read_excel('relatorio.xlsx')

data = df['Data']
hora = df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M')
procedimento = df['Procedimento']
executante = df['Executante']
df['Data'] = df['Data'].dt.date

resultados = []
for i in range(len(data)):
        if hora[i].hour < 12:
            período = 'Manhã'
        elif hora[i].hour < 18:
            período = 'Tarde'
        else:
            período = 'Outro'

        if data[i].weekday() == 5:
            dia = 'Sábado'
        else:
            dia = 'Semana'

        if 'doppler' in procedimento[i].lower() or 'arterial' in procedimento[i].lower() or 'venoso' in procedimento[i].lower():
            valor = 40.00
            tipo = 'Doppler Vascular'
        elif 'doppler' not in procedimento[i].lower():
            valor = 25.00
            tipo = 'Modo B'
        else:
            valor = 30.00
            tipo = 'Não Vascular'

        resultados.append([data[i], hora[i], procedimento[i], executante[i], período, dia, tipo, valor])

df_resultados = pd.DataFrame(resultados, columns=['Data', 'Hora', 'Procedimento', 'Executante', 'Período', 'Dia', 'Tipo', 'Valor'])


# Adiciona as colunas "Total por período"
df_grouped = df_resultados.groupby(['Data', 'Período'])['Valor'].sum().reset_index()
df_grouped = df_grouped.rename(columns={'Valor': 'Valor_Total_Período'})
df_resultados = df_resultados.merge(df_grouped, on=['Data', 'Período'])

df_grouped = df_resultados[df_resultados['Dia'] == 'Sábado'].groupby(['Data'])['Valor'].sum().reset_index()
df_grouped = df_grouped.rename(columns={'Valor': 'Valor_Total_Sábado'})
df_resultados = df_resultados.merge(df_grouped, on=['Data'], how='left')

df_resultados.to_excel('relatorio_filtrado.xlsx', index=False)

df_grouped = df_resultados.groupby(['Executante', 'Data', 'Período', 'Dia'])['Valor'].sum().reset_index()
df_grouped['Valor_a_Pagar'] = np.where((df_grouped['Período'].isin(['Manhã', 'Tarde'])) & (df_grouped['Valor'] < 600), 600,
np.where((df_grouped['Dia'] == 'Sábado') & (df_grouped['Valor'] < 650), 650, df_grouped['Valor']))


df_grouped.to_excel('relatorio_filtradoporexecutante.xlsx', index=False)

df_grouped = df_grouped.groupby(['Executante'])['Valor_a_Pagar'].sum().reset_index()
df_grouped.to_excel('totalporexecutante.xlsx', index=False)




executants = df_grouped['Executante'].unique()
for executant in executants:
    executant_df = df_grouped[df_grouped['Executante'] == executant]
    executant_file_name = f"{executant}.pdf"
    html = executant_df.to_html()
    pdfkit.from_string(html, executant_file_name, options={'page-size': 'Letter', 'encoding': "UTF-8"})

    