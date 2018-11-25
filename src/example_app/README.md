# Example SageMaker App

This is an example application that demonstrates how to use the Amazon SageMaker 
Runtime and a deployed model endpoint.

It is a simple command line executable, but the concepts here could easily be
transferred to a simple web application or serverless invocation using AWS
Lambda.

## Files

### configuration

* `config.ini`: the primary configuration file for the application
* `cluster_map_*.json`: mappings of cluster ids to super populations

### data

* `cluster_labels_*.csv`: cross-tabulation of clusters to labeled super-populations 
    from model training, where `*` is the number of clusters defined in the model.
* `test_data.csv`: the last 5 rows of aggregated, processed genotypes.  The
    index column and column headers have been removed because the inferrence
    endpoint expects only the numeric values in csv format.
* `random.csv`: randomly generated series of possible genotype values.

## Usage

```bash
./invoke.py -h

./invoke.py test_data.csv
./invoke.py random.csv
```
