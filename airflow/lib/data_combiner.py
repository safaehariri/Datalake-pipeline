from pyspark.sql import SparkSession
from pyspark.sql.functions import array, col, lit
from datetime import datetime 
from pyspark.sql.window import Window
from lib.utils import get_latest_parquet_file
from pyspark.sql.functions import col, lit, max, rank


def combine_data(today_date, current_day_directory, station_df_path , **kwargs):
    """
    Combines daily usage data with station data to enrich the dataset with additional
    geolocation and timestamp information, then saves the result as a Parquet file.

    The function reads all Parquet files from the specified daily directory, joins them
    with the station details data, and adds two new fields:
    - 'location': an array combining longitude and latitude of the station.
    - 'timestamp': the exact time of data processing formatted as YYYY-MM-DDTHH:MM:SS.

    Parameters:
        today_date (str): The current date used to define output directory paths.
        current_day_directory (str): Path to the directory containing daily usage Parquet files.
        station_df_path (str): Path to the Parquet file containing station details.
        **kwargs: Keyword arguments that may include Airflow-specific functionality such
                  as task instance for XCom push.

    Returns:
        None. Outputs a Parquet file to a specified directory and pushes the
        output directory path to XCom.

    """

    timestamp_str = datetime.now().strftime("%Y%m%dT%H%M%S")
    output_directory = f"/mnt/data/usage/velib_analytics/{today_date}/{timestamp_str}.parquet"

    spark = SparkSession.builder.appName("VelibDataJoin").getOrCreate()
    
    latest_parquet_file = get_latest_parquet_file(current_day_directory)

    daily_df = spark.read.parquet(latest_parquet_file)
    
    stations_df = spark.read.parquet(station_df_path)
    
    final_df = daily_df.join(stations_df, "station_id", "inner")
    
    final_df = final_df.withColumn("location", array(col("longitude"), col("latitude")))
    
    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    final_df = final_df.withColumn("timestamp", lit(current_timestamp))
    
    window_spec = Window.partitionBy("station_id").orderBy(col("last_reported").desc())
    df_filtered = final_df.withColumn("rank", rank().over(window_spec)).filter(col("rank") == 1).drop("rank")


    df_filtered.coalesce(1).write.format("parquet").mode("overwrite").save(output_directory)
    kwargs['ti'].xcom_push(key='output_directory', value=output_directory)

    spark.stop()

