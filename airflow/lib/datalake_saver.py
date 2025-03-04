from datetime import datetime 
import os
import json
import logging
from datetime import datetime
from typing import Any, Optional

def save_to_datalake(ti: Any, directory_path : str, today_date : datetime ,task_id: str, name: str, **kwargs) -> Optional[str]:
    """
    Save JSON data retrieved from XCom into a file in the datalake directory structure.

    The file is stored under the path:
        /mnt/data/raw/velib_api/{name}/{YYYYMMDD}/{YYYYMMDDHHMM}.json

    Parameters:
        ti (Any): The task instance used to pull XCom data.
        task_id (str): The ID of the task from which to retrieve the data.
        name (str): The directory name used in the path.
        **kwargs: Additional keyword arguments.

    Returns:
        Optional[str]: The full path to the saved file, or None if no data was found.
    """
    # Retrieve the JSON data from XCom
    data = ti.xcom_pull(task_ids=task_id)
    if data is None:
        logging.warning(f"No data found in XCom for task_id: {task_id}")
        return None

    now = datetime.now()
    granular_date_str = now.strftime("%Y%m%d%H%M")

    # Build the directory and file paths
    base_path = os.path.join(directory_path, name, today_date)
    filename = f"{granular_date_str}.json"
    full_path = os.path.join(base_path, filename)
    
    # Ensure the directory exists
    os.makedirs(base_path, exist_ok=True)
    
    # Write the data to a JSON file with indentation for readability
    try:
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Data saved successfully to {full_path}")
    except Exception as e:
        logging.error(f"Failed to write data to {full_path}: {e}")
        raise

    return full_path
