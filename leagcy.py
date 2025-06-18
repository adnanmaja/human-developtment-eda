import csv
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

GRDPdir = "D:/Python/dsci2/GRDP Growth.csv"
INVESTMENTdir = "D:/Python/dsci2/Investasifix.csv"
IPMdir = "D:/Python/dsci2/IPM.csv"

with open(GRDPdir) as f1:
    grdp_test = csv.reader(f1)
    print([line for line in grdp_test])


# =============================================


grdp_data = pd.read_csv(GRDPdir)
invest_data = pd.read_csv(INVESTMENTdir)
ipm_data = pd.read_csv(IPMdir)

ipmfix = ['IPM 2019', 'IPM 2020', 'IPM 2021', 'IPM 2022', 'IPM 2023']
for col in ipmfix:
    ipm_data[col] = pd.to_numeric(ipm_data[col].astype(str).str.replace(',','.'))

grdp_clean = grdp_data.melt(id_vars='Provinsi', 
               value_vars= [col for col in grdp_data.columns if col.startswith('GRDP') and any(y in col for y in ['2019','2020','2021','2022','2023'])],
               var_name='GRDP_Tahun', value_name='GRDP')
grdp_clean['Tahun'] = grdp_clean['GRDP_Tahun'].str.extract(r'(\d{4})').astype(int)

ipm_clean = ipm_data.melt(id_vars='Provinsi', 
               value_vars= [col for col in ipm_data.columns if col.startswith('IPM')],
               var_name='IPM_Tahun', value_name='IPM')
ipm_clean['Tahun'] = ipm_clean['IPM_Tahun'].str.extract(r'(\d{4})').astype(int)
print(ipm_clean)


# =======================================================

# Merge to one df
df_merged = pd.merge(grdp_clean[['Provinsi', 'Tahun', 'GRDP']], 
                  ipm_clean[['Provinsi', 'Tahun', 'IPM']], 
                  on=['Provinsi', 'Tahun'])


df_merged = df_merged.sort_values(['Provinsi', 'Tahun'])
df_merged['GRDP'] = pd.to_numeric(df_merged['GRDP'])
df_merged['IPM'] = pd.to_numeric(df_merged['IPM'])
df_merged['GRDP_Growth'] = df_merged.groupby('Provinsi')['GRDP'].pct_change() * 100
df_merged['IPM_Growth'] = df_merged.groupby('Provinsi')['IPM'].pct_change() * 100

print(df_merged)
df_merged.to_csv('tessss.csv', index=False)
corrs = df_merged.groupby('Tahun')[['GRDP_Growth', 'IPM_Growth']].corr().iloc[0::2, 1]
print(corrs)


# ============================================================

for year in df_merged['Tahun'].unique():
    subset = df_merged[df_merged['Tahun'] == year]
    plt.figure(figsize=(12,10))
    sns.scatterplot(data=subset, x='GRDP_Growth', y='IPM_Growth', hue='Provinsi')
    plt.title(f"GRDP vs IPM Growth — {year}")
    plt.axhline(0, ls='--', color='grey')
    plt.axvline(0, ls='--', color='grey')
    plt.tight_layout()
    plt.show()


# ============================================================

avg_growth = df_merged.groupby('Tahun')[['GRDP_Growth', 'IPM_Growth']].mean().reset_index()

plt.plot(avg_growth['Tahun'], avg_growth['GRDP_Growth'], label='Avg GRDP Growth')
plt.plot(avg_growth['Tahun'], avg_growth['IPM_Growth'], label='Avg IPM Growth')
plt.title("National Average Growth: GRDP vs IPM")
plt.xlabel("Tahun")
plt.ylabel("Growth (%)")
plt.legend()
plt.grid(True)
plt.show()

# ================================================================


import plotly.express as px

fig = px.scatter(df_merged,
                 x='GRDP_Growth', y='IPM_Growth',
                 animation_frame='Tahun',
                 color='Provinsi',
                 size_max=60,
                 title="Yearly GRDP vs IPM Growth by Province")

fig.show()