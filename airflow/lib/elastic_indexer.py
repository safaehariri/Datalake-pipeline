from elasticsearch import Elasticsearch, helpers
from pyarrow import parquet as pq
import numpy as np
import pandas as pd

def index_parquet_to_elasticsearch(task_id ,es_url="http://elasticsearch:9200", index_name="velib_data_analytics" , **kwargs):
    """
    Indexes data from a Parquet file into an Elasticsearch index.

    Parameters:
        task_id (str): The Airflow task ID used to pull the output directory from XCom.
        es_url (str, optional): The URL of the Elasticsearch server. Defaults to "http://elasticsearch:9200".
        index_name (str, optional): The name of the Elasticsearch index where the data will be stored. 
                                    Defaults to "velib_data_analytics".
    Returns:
        None. This function performs operations that result in data being indexed in Elasticsearch.
    """
    ti = kwargs['ti']
    directory_path = ti.xcom_pull(task_ids= task_id, key='output_directory')
    
    # Charger le fichier Parquet en DataFrame Pandas
    table = pq.read_table(directory_path)
    df = table.to_pandas()
    df = df.replace({np.nan: None, pd.NA: None, 'None': None})
    # Connexion à Elasticsearch
    es = Elasticsearch(es_url)
    
    # Créer l'index avec mapping si celui-ci n'existe pas déjà
    if not es.indices.exists(index=index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "location": {"type": "geo_point"},
                    "station_id": {"type": "keyword"},
                    "num_bikes_available": {"type": "integer"},
                    "num_docks_available": {"type": "integer"},
                    "is_installed": {"type": "integer"},
                    "is_returning": {"type": "integer"},
                    "is_renting": {"type": "integer"},
                    "last_reported": {"type": "date"},
                    "mechanical_bikes_available": {"type": "integer"},
                    "ebikes_available": {"type": "integer"},
                    "name": {"type": "keyword"},
                    "latitude": {"type": "float"},
                    "longitude": {"type": "float"},
                    "capacity": {"type": "integer"},
                    "timestamp": {"type": "date"}
                }
            }
        }
        es.indices.create(index=index_name, body=mapping)
        print(f"Index '{index_name}' créé avec mapping.")
    
    # Préparer les documents pour l'indexation
    records = df.to_dict(orient="records")
    actions = [{"_index": index_name, "_source": record} for record in records]
    
    # Indexation en bulk (les nouveaux documents sont ajoutés, l'historique est conservé)
    helpers.bulk(es, actions)
