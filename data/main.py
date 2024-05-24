import pandas as pd
import matplotlib.pyplot as plt


import geopandas
from geodatasets import get_path

#Load data and initial cleaning 
df = pd.read_excel("Unemployment.xlsx", header=None) 
df.columns = df.iloc[4]
df.drop([0, 1, 2, 3, 4], inplace=True)

#print(df.loc[df['FIPS_Code']=="00000"])
df.drop(df[df['FIPS_Code'].astype(int) % 1000 == 0].index, inplace=True)
df.drop(df[df['State'] == "PR"].index, inplace=True)

df['Area_Name'] = df['Area_Name'].str.replace(r' County.+', '', regex=True)

#print(df)
print(len(df.index))

# Reshape for Employed and Unemployed over all years 
Employed_columns = df.filter(regex='^Employed_').columns
df_long_stub1 = pd.melt(df, id_vars=['FIPS_Code'], value_vars=Employed_columns, var_name='year', value_name='Employed')
df_long_stub1['year'] = df_long_stub1['year'].str.extract('(\d+)$')

Unemployed_columns = df.filter(regex='^Unemployed_').columns
df_long_stub2 = pd.melt(df, id_vars=['FIPS_Code'], value_vars=Unemployed_columns, var_name='year', value_name='Unemployed')
df_long_stub2['year'] = df_long_stub1['year'].str.extract('(\d+)$')

#Keep the variables asked and duplicate them so that we can merge with Employed/Unemployed
col_list = ['FIPS_Code', 'State', 'Area_Name', 'Rural_Urban_Continuum_Code_2013', 'Urban_Influence_Code_2013',	'Metro_2013',	'Median_Household_Income_2021']
df = df[col_list]

#Now duplicate
df['year'] = '2000'

df_copy = df.copy()
df_copy['year'] = '2001'
df_combined = pd.concat([df, df_copy], ignore_index=True)

for i in range(2002,2023):
    df_copy = df.copy()
    df_copy['year'] = str(i)
    df_combined = pd.concat([df_combined, df_copy], ignore_index=True)


#Now merge the asked variables with Employed/Unemployed
df_long = pd.merge(df_long_stub1, df_long_stub2, on=['FIPS_Code', 'year'])
df_long2 = pd.merge(df_combined, df_long, on=['FIPS_Code', 'year'])

df_long2.dropna(how='any', inplace=True)
df_long2.to_csv("county_unemployment_clean.csv")

print(len(df_long.index))
print(len(df_combined.index))
print(len(df_long2.index))

###############
# Now draw some graphs using the data

#Load shapefile
path_to_data = "US_state_shapefile/cb_2018_us_county_500k.shp"
gdf = geopandas.read_file(path_to_data)

print(gdf)
gdf['FIPS_Code'] = gdf['STATEFP'] + gdf['COUNTYFP']
gdf = gdf.set_index("FIPS_Code")

#Prepare df to merge with gdf
col_list = ['FIPS_Code', 'State', 'Area_Name', 'Employed', 'Unemployed', 'year']
df_long2 = df_long2[col_list]
df_long2['Unemp_rate'] = 100 * df_long2['Unemployed']/(df_long2['Employed'] + df_long2['Unemployed'])

for i in range(2001,2023):
    df_long2.drop(df_long2[df_long2['year'] == str(i)].index, inplace=True)
print(df_long2)
df_long2.drop(df_long2[df_long2['State'] == 'AK'].index, inplace=True)
df_long2.drop(df_long2[df_long2['State'] == 'HI'].index, inplace=True)

#Merge gdf and df
gdf_merged = pd.merge(gdf, df_long2, on=['FIPS_Code'])
print(gdf_merged)

#Plot unemployment in 2000
gdf_merged.plot("Unemp_rate")
plt.show()


print("This is test")