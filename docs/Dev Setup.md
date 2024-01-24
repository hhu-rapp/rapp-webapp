# Development Setup

The `dev_setup.py` script is designed to facilitate the setup of a development database, providing the necessary data for development purposes.

## Functional Queries

Functional queries are defined by `.sql` files located in the 'uploads' folder.

## Targets

Targets are folders within the 'uploads' directory that must meet a specific criteria:

- Each target folder must contain a `.sql` file with the query.
- Additionally, each target folder must contain a `.joblib` file with the corresponding model.
- Configuration details for each target are stored in a `config.ini` file within the folder.

### Configuration File (config.ini)

The `config.ini` file within each target folder should have the following structure:

```ini
[DEFAULT]
label = Name of the target feature (case-sensitive if the feature should be dropped)
description = Description of the target (optional)
model = Name of the model (optional)
```

### Usage
To execute the script, run it as the main module using the following command:

```bash
python dev_setup.py [optional_database_name.db]
```

- The database must be located in the 'uploads' directory.
- If no database name is provided, the script defaults to 'rapp_dummy.db' within the 'uploads' directory.
