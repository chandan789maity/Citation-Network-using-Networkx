import pandas as pd
import networkx as nx
import zipfile
from rarfile import RarFile

#1:Function to read data from a rar file(convert the rar file data ->text file)
def read_rar_data(rar_file, filename):
    with RarFile(rar_file, 'r') as rar_ref:
        with rar_ref.open(filename) as file:
            content = file.read().decode('utf-8')
            return pd.DataFrame([x.split(' ---- ') for x in content.split('\n')], columns=['index', 'info'])

# 2:Function to read data from a zip file(zipFile->Text file)
def read_zip_data(zip_file, filename, header=None, names=None):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        with zip_ref.open(filename) as file:
            return pd.read_csv(file, header=header, names=names)
#Relationship for the given require relation.
def find_papers_by_author(author_id):
    papers = author_paper_data[author_paper_data['AuthorID'] == author_id]
    return papers[['PaperID', 'AuthorPosition']]

# Example usage: Find papers by a specific author (replace 'desired_author_id' with an actual author ID)
desired_author_id = 'example_author_id'
papers_by_author = find_papers_by_author(desired_author_id)
print(f"Papers by author {desired_author_id}:\n{papers_by_author}")

# 3:Read AMiner-Paper.rar file
paper_data = read_rar_data('AMiner-Paper.rar', 'AMiner-Paper.txt')
papers = {}
current_paper = None

for index, row in paper_data.iterrows():
    if row['index'].startswith('#index'):
        current_paper = int(row['index'].split(' ')[-1])
        papers[current_paper] = {}
    elif row['index'].startswith('#*'):
        papers[current_paper]['title'] = row['info'][2:]
    elif row['index'].startswith('#@'):
        papers[current_paper]['authors'] = row['info'][2:].split(';')
    elif row['index'].startswith('#o'):
        papers[current_paper]['affiliations'] = row['info'][2:].split(';')
    elif row['index'].startswith('#t'):
        papers[current_paper]['year'] = int(row['info'][2:])
    elif row['index'].startswith('#c'):
        papers[current_paper]['publication_venue'] = row['info'][2:]
    elif row['index'].startswith('#%'):
        papers[current_paper].setdefault('references', []).append(int(row['info'].split(' ')[-1]))
    elif row['index'].startswith('#!'):
        papers[current_paper]['abstract'] = row['info'][2:]

# 4:Read AMiner-Author.zip file
author_data = read_zip_data('AMiner-Author.zip', 'AMiner-Author.txt', header=None, names=['index', 'info'])
authors = {}
current_author = None

for index, row in author_data.iterrows():
    if row['index'].startswith('#index'):
        current_author = int(row['index'].split(' ')[-1])
        authors[current_author] = {}
    elif row['index'].startswith('#n'):
        authors[current_author]['name'] = row['info'][2:]
    elif row['index'].startswith('#a'):
        authors[current_author]['affiliations'] = row['info'][2:].split(';')
    elif row['index'].startswith('#pc'):
        authors[current_author]['published_papers'] = int(row['info'].split(' ')[-1])
    elif row['index'].startswith('#cn'):
        authors[current_author]['total_citations'] = int(row['info'].split(' ')[-1])
    elif row['index'].startswith('#hi'):
        authors[current_author]['h_index'] = int(row['info'].split(' ')[-1])
    elif row['index'].startswith('#pi'):
        authors[current_author]['p_index_equal'] = int(row['info'].split(' ')[-1])
    elif row['index'].startswith('#upi'):
        authors[current_author]['p_index_unequal'] = int(row['info'].split(' ')[-1])
    elif row['index'].startswith('#t'):
        authors[current_author]['research_interests'] = row['info'][2:].split(';')

# 5:Read AMiner-Coauthor.zip file
collab_data = read_zip_data('AMiner-Coauthor.zip', 'AMiner-Coauthor.txt', header=None, names=['author1', 'author2', 'collaborations'])
collaborations = [(int(row['author1']), int(row['author2']), {'collaborations': row['collaborations']}) for _, row in collab_data.iterrows()]
#Now sir i am creating the graph relation of the required data frame
# Create a graph using NetworkX
G = nx.Graph()

# Add authors as nodes
G.add_nodes_from(authors.keys(), bipartite=0)

# Add papers as nodes
G.add_nodes_from(papers.keys(), bipartite=1)

# Add collaboration edges
G.add_edges_from(collaborations)

# Visualize the graph or perform network analysis
# For example:
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())
print("Degree centrality:", nx.degree_centrality(G))

# nx.draw(G, with_labels=True)  
# Drawing the graph might not be suitable for large graphs
