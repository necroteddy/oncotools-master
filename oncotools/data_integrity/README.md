# Data integrity

Python framework for data integrity validation with Oncospace database

See full documentation `Documentation` folder. Integrated with Oncospace documentation.

## User guide

User needs to write two modules, a data query object and a integrity check object.

### Query Module
The purpose of these modules is to get the specific data type for the integrity modules.
For example, `/data/data_doses.py` reads dosegrid data for specific patient representation IDs.

Super class example for data query modules is `data/Query_Module.py`
General query module structure:

```python
class query_module_name(Query_Module):
    def __init__(self):
        self.name = "query_module_name"
        self.function = "description of data collected"
        self.description = {self.name: self.function}

    def get_data(dbase, ID):
        data = []
        ## TODO: data acquisition methods
        return data
```

### Integrity Module
The purpose of these modules is to run the data validation algorithm on the data selected.
For example, `/Modules/check_dose_grid.py` takes in a dose grid and checks if the dose grid is valid.

Super class example for integrity check modules is `Modules/Integrity_Module.py`
General query module structure:

```python
def check_integrity(self, data):
    def __init__(self):
        self.name = "query_module_name"
        self.function = "description of data collected"
        self.description = {self.name: self.function}

    def check_integrity(self, data):
        ## TODO: integrity validation method
        return (valid, message, errortype)
```

## TODO

- Implement other data integrity modules
- Implement other data reading modules
