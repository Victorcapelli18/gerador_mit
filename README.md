# MIT JSON Generator

A modern application for generating MIT JSON files from Excel data.

## Features

- Load company data from Excel files
- Process and transform data according to MIT specifications
- Validate JSON against a schema
- Generate valid MIT JSON files
- Modern and user-friendly interface

## Architecture

This application follows Clean Architecture and SOLID principles:

- **Domain Layer**: Contains business entities, repository interfaces, and use cases
- **Infrastructure Layer**: Contains implementations of repositories
- **Presentation Layer**: Contains controllers and UI components

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application using one of the following methods:

### Method 1: Using the run.py script (Recommended)

```bash
python run.py
```

### Method 2: Using Python module mode

```bash
python -m src.main
```

### Method 3: Directly (requires PYTHONPATH to be set)

```bash
# Set PYTHONPATH first
set PYTHONPATH=%PYTHONPATH%;.  # Windows
export PYTHONPATH=$PYTHONPATH:.  # Linux/Mac

# Then run
python src/main.py
```

## Application Usage

1. Select an Excel file with company data
2. Select an output directory
3. Click "Generate JSON" to generate the files

## Excel File Format

The Excel file should contain the following sheets:

- **PeriodoApuracao**: Period information
- **DadosIniciais**: Initial company data
- **Debitos**: Debit information
- **ListaSuspensoes**: Suspension information

## License

MIT 