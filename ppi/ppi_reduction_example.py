import os
import time

import random

import pickle
import pandas as pd
import networkx as nx
import numpy as np

def intersection(str1, str2):
    """
    Parse the pathway information read from dataframe, which is a string
    str1: string -- pathway1
    str2: string --- pathway2
    """
    if str1 == 'unknown' and str2 == 'unknown':
        return True
    elif str1 == 'unknown' or str2 == 'unknown':
        return False
    else:
        lst1 = str1.replace('[','').replace(']','').split(',')
        lst2 = str2.replace('[','').replace(']','').split(',')
        inter = list(set(lst1) & set(lst2))
        if len(inter)>0:
            return True
        else:
            return False

def get_neighbors(df, protein):
    """
    Find neighbors based from the edge list for a given node
    df: DataFrame -- master edge table
    protein: string -- protein name
    """
    nei_df1 = df[df['protein1'] == protein]
    neighbors1 = nei_df1['protein2'].tolist()
    nei_df2 = df[df['protein2'] == protein]
    neighbors2 = nei_df2['protein1'].tolist()
    neighbors = neighbors1 + neighbors2
    return neighbors

s = time.time()

"""
Set up the necessary paths
"""
root = './data/'
output_path = './reduced_output/'
"""
Load master_edge_table, affinity data, pathway data, disease scores, and kinase information
"""
master_edge_table = pd.read_csv(root + 'master_edge_table.csv')
ba = pd.read_csv(root + 'affinity.csv')
raw_pathways = pd.read_csv(root + 'pathway_info.csv')
z_scores = pd.read_csv(root + 'diseases_scores.csv')
with open(root + 'kinases.pkl','rb') as f:    
    kinases = pickle.load(f)
"""
create instance paths based on the combination of different cell line and drug name
"""
instance_id = '1321N1_lapatinib'
combination = instance_id.split('_')
cell_line = combination[0]
drug = combination[1]
ge_folder = './gene_expressions/'
ge = pd.read_csv(ge_folder + cell_line + '.csv')
"""
Generate instance node table (original_node_table)
"""
node_table = ge
affinity = ba.loc[ba['Drug_Name']==drug][['ENSEMBLID','Affinity', 'Class']]
affinity.rename(columns={'ENSEMBLID':'ensembl'}, inplace=True)
node_table_aff = node_table.merge(affinity, how='left') # combine affinity data into node_table
node_table_na = node_table_aff.fillna(0) # fill NaN affinities as 0
node_table_z = node_table_na.merge(z_scores) # combine disease scores into node_table
node_table_final = node_table_z.merge(raw_pathways) # combine pathway information into node_table
node_table_final['kinaseness'] = [1.0]*len(node_table_final) # combine kinase information into node_table
node_table_final.at[node_table_final['ensembl'].isin(kinases), 'kinaseness'] = 2.0
node_table_final.to_csv(root + instance_id + '.csv', index=False) # save instance
"""
Start the graph contraction
"""
new_edge_table = master_edge_table
# add gene expressions information to edge_table
ged = node_table_final[['ensembl', 'gene_exp']].to_dict('list')
ged1 = dict(zip(ged['ensembl'], ged['gene_exp']))
new_edge_table.at[:,'ge1'] = [ged1[x] for x in new_edge_table['protein1'].tolist()]
new_edge_table.at[:,'ge2'] = [ged1[x] for x in new_edge_table['protein2'].tolist()]
# add pathway information to edge_table
pathways = node_table_final[['ensembl', 'pathways']].to_dict('list')
pathways1 = dict(zip(pathways['ensembl'], pathways['pathways']))
new_edge_table.at[:,'inter'] = [intersection(pathways1[x],pathways1[y]) for x,y in zip(new_edge_table['protein1'].tolist(),new_edge_table['protein2'].tolist())]
# find edges that are NOT contractable (gene expression not the same | either node is a kinase | pathways not the same)
keepers = new_edge_table[(new_edge_table['protein1'].isin(kinases)) | 
                              (new_edge_table['protein2'].isin(kinases)) | 
                              (new_edge_table['ge1'] != new_edge_table['ge2'])|
                              (new_edge_table['inter'] == False)]

# Create a temp graph
tmp_G = nx.from_pandas_edgelist(new_edge_table, source='protein1', target='protein2',
                                edge_attr = new_edge_table.columns.tolist()[2])
# Remove the UNcontractable edges
keepers_tuple = [(x,y) for x,y in zip(keepers['protein1'].tolist(), keepers['protein2'].tolist())]
tmp_G.remove_edges_from(keepers_tuple)
# Find connected components that have more than one node
Gs = list(nx.connected_component_subgraphs(tmp_G))
connected_Gs = [x for x in Gs if len(x.nodes) > 1]
# Actual contraction part
new_node_table = node_table_final
d = {i:i for i in new_node_table['ensembl'].tolist()}
ids = 0
for G in connected_Gs:
    nodes = list(G.nodes)
    dest = random.choice(nodes)
    tmp_row = node_table_final[node_table_final['ensembl'] == dest]
    idx = tmp_row.index[0]
    node_attrs = node_table_final[node_table_final['ensembl'].isin(nodes)]
    medians = node_attrs.iloc[:,-5:-1].replace(0, np.nan).median() # can be max as well
#    maxs = node_attrs.iloc[:,-4:-1].replace(0, np.nan).max()
    tmp_row.at[idx, ['disgenet_score', 'diseases_score', 'malacards_score']] = medians.to_numpy()
    tmp_row.at[idx, 'ensembl'] = 'v{}'.format(ids)

    for item in nodes:
        d[item] = 'v{}'.format(ids)
    new_node_table.loc[new_node_table['ensembl'].isin(nodes),'kinaseness'] = 0.0
    new_node_table.loc[new_node_table['ensembl'].isin(nodes),'ensembl'] = 'v{}'.format(ids)
    new_edge_table.loc[new_edge_table['protein1'].isin(nodes),'protein1'] = 'v{}'.format(ids)
    new_edge_table.loc[new_edge_table['protein2'].isin(nodes),'protein2'] = 'v{}'.format(ids)
    new_edge_table = new_edge_table[new_edge_table['protein1'] != new_edge_table['protein2']]
    ids += 1
    
# Replace edge score with median of all contracted scores
new_node_table.drop_duplicates('ensembl', inplace=True)
dups = new_edge_table[new_edge_table.duplicated(['protein1', 'protein2'])]
c = dups[['protein1','protein2']].drop_duplicates()
w = [(x,y) for x, y in zip(c['protein1'].tolist(), c['protein2'].tolist())]
for t in w:
    tmp_rows = new_edge_table[(new_edge_table['protein1'] == t[0]) &
                              (new_edge_table['protein2'] == t[1])]
    med_score = tmp_rows['combined_score'].median()
    new_edge_table.loc[(new_edge_table['protein1'] == t[0]) & (new_edge_table['protein2'] == t[1]), 'combined_score'] = med_score
# Remove scenarios where A-B and B-A are the same
new_edge_table.drop_duplicates(['protein1', 'protein2'], inplace=True)
new_edge_table['check_string'] = new_edge_table.apply(lambda row: ''.join(sorted([str(row['protein1']), str(row['protein2'])])), axis=1)
new_edge_table.drop_duplicates('check_string', inplace=True)
new_edge_table.drop('check_string', inplace=True, axis=1)
# Replace NaN with 0 for disease scores
new_node_table.fillna({'disgenet_score':0, 'diseases_score':0, 'malacards_score':0}, inplace=True)
# Create new graph
GG = nx.from_pandas_edgelist(new_edge_table, source='protein1', target='protein2',
                            edge_attr = new_edge_table.columns.tolist()[2])
"""
Assign node attributes
"""
attr_d = node_table_final.to_dict(orient='index')
keys = list(attr_d.keys())
for k in keys:
   tmp_id = attr_d[k]['ensembl']
   attr_d[tmp_id] = attr_d.pop(k)
nx.set_node_attributes(GG, attr_d)
"""
Save stuff
"""
nx.write_gexf(GG, output_path + instance_id + '.gexf')
node_table_final.to_csv(output_path + instance_id + '/' + 'contracted_node_table_{}.csv'.format(instance_id), index=False)
new_edge_table.to_csv(output_path + instance_id + '/' + 'contracted_edge_table_{}.csv'.format(instance_id), index=False)
d1 = {'original':[], 'new':[]}
for k,v in d.items():
    d1['original'].append(k)
    d1['new'].append(v)
contraction_record = pd.DataFrame(d1)
contraction_record.to_csv(output_path + instance_id + '_record.csv', index=False)

print(time.time() - s)
