from datetime import datetime, timedelta
import pandas as pd
from functools import partial

from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.models.baseoperator import chain

from lib.datalake_saver import save_to_datalake
from lib.data_formatting import format_velib_data, format_station_details_data
from lib.data_combiner import combine_data
from lib.elastic_indexer import index_parquet_to_elasticsearch
from lib.utils import get_latest_parquet_file,process_files_in_directory

# Constants
TODAY_DATE = datetime.today().strftime("%Y%m%d")
RAW_DATA_DIR = "/mnt/data/raw/velib_api"
CURRENT_DAY_DIRECTORY = f"/mnt/data/formatted/velib_api/velib_stations/{TODAY_DATE}"
API_CONNECTION_ID = 'velib_api_connection'
CONTENT_TYPE_JSON = {"Content-Type": "application/json"}
STATION_DF_PATH = f"/mnt/data/formatted/velib_api/station_information/{TODAY_DATE}"

JSON_RESPONSE_FILTER = lambda response: response.json()

default_args = {
    'start_date': datetime(2025, 2, 25),
    'execution_timeout': timedelta(minutes=60), 
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG('api_to_db_dag',
         default_args=default_args,
         schedule_interval='0/15 * * * *',
         #schedule_interval='0 * * * *',
         catchup=False) as dag:

    get_api_station_data = SimpleHttpOperator(
        task_id='get_velib_data',
        http_conn_id=API_CONNECTION_ID,
        endpoint='station_status.json',
        method='GET',
        headers=CONTENT_TYPE_JSON,
        response_filter=lambda response: response.json(),
        do_xcom_push=True
    )

    get_api_station_details_data = SimpleHttpOperator(
        task_id='get_station_information',
        http_conn_id=API_CONNECTION_ID,
        endpoint='station_information.json',
        method='GET',
        headers=CONTENT_TYPE_JSON,
        response_filter=lambda response: response.json(),
        do_xcom_push=True
    )

    save_stations_data_task = PythonOperator(
        task_id='save_raw_station_information',
        python_callable=save_to_datalake,
        op_kwargs={'directory_path': RAW_DATA_DIR, 'today_date':TODAY_DATE ,'task_id': 'get_velib_data', 'name': 'velib_stations'},
    )

    save_stations_details_data_task = PythonOperator(
        task_id='save_raw_station_details_information',
        python_callable=save_to_datalake,
        op_kwargs={'directory_path': RAW_DATA_DIR, 'today_date':TODAY_DATE ,'task_id': 'get_station_information', 'name': 'station_information'},
    )
    
    process_files_station_information = PythonOperator(
        task_id='process_raw_station_information',
        python_callable=process_files_in_directory,
        op_kwargs={'function': format_station_details_data, 'raw_data_directory' : RAW_DATA_DIR, 'directory': 'station_information'},
        provide_context=True
    )

    process_files_velib_station = PythonOperator(
        task_id='process_raw_velib_station',
        python_callable=process_files_in_directory,
        op_kwargs={'function': format_velib_data, 'raw_data_directory' : RAW_DATA_DIR, 'directory': 'velib_stations'},
        provide_context=True
    )


    process_combined_data_task = PythonOperator(
        task_id='combine_analyse_data',
        python_callable=combine_data,
        op_kwargs={'today_date': TODAY_DATE, 'current_day_directory': CURRENT_DAY_DIRECTORY, 'station_df_path': get_latest_parquet_file(STATION_DF_PATH)},
        dag=dag,
    )

    index_task = PythonOperator(
        task_id='index_data_to_elasticsearch',
        python_callable=index_parquet_to_elasticsearch,
        op_kwargs={'task_id' : 'combine_analyse_data' , 'es_url': "http://elasticsearch:9200", 'index_name': "velib_analytics"},
        dag=dag,
    )

    chain(
        [get_api_station_data, get_api_station_details_data],
        [save_stations_data_task, save_stations_details_data_task],
        [process_files_velib_station, process_files_station_information],
        process_combined_data_task
    )

    process_combined_data_task >> index_task
