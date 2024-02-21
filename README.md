# BPlusTree and Jaccard Index Application

## Introduction

This Python application combines the functionality of a B+ tree implementation (`BPlusTree`) and a Jaccard Index calculator (`jaccard_index`). The B+ tree is used to efficiently store and retrieve (document, term) pairs, and the Jaccard Index is calculated to measure the similarity between categories and stems associated with these documents.

## Logging

The application includes a comprehensive logging mechanism to capture relevant information during runtime. Logging configuration can be found in `myeditorlog.conf`. The logging phase helps in debugging, understanding the flow of the application, and identifying potential issues.

## Profiling

Barbara Riga has contributed to the profiling section of the application. Profiling involves measuring the performance characteristics of the code, identifying bottlenecks, and optimizing critical sections. Check the profiling phase to ensure optimal execution and resource utilization.

## Refactoring

Thanos Panou has conducted the refactoring phase, improving the code's structure, readability, and maintainability. The refactoring efforts aim to enhance the overall quality of the application and simplify future development.

## Unit Testing

The application is accompanied by a suite of unit tests to validate the correctness of individual components. Thanos Panou has contributed to the creation of these tests, ensuring the reliability and stability of the application.

## BPlusTree

The `BPlusTree` class provides a B+ tree implementation with support for insertion, retrieval, and deletion of key-value pairs. The tree is designed to efficiently 
handle large datasets by organizing the data into a hierarchical structure. The branching factor, or order, of the tree is configurable, allowing you to adapt it to your specific needs.
For further details, you may see the document [BplusTreeReport.pdf](https://github.com/CodeMaestro1/NewsAnalyzer/blob/main/BplusTreeReport_Final.pdf).


## Jaccard Index

The `jaccard_index` class calculates the Jaccard Index, a measure of similarity between two sets, for stems and categories associated with documents. The Jaccard Index is used to identify the most relevant stems for a given category and vice versa.

### Usage

To use the Jaccard Index calculator, instantiate the `jaccard_index` class with three dictionaries representing categories, terms, and stems:

```python
jaccard_instance = jaccard_index(categories_dict, terms_dict, stems_dict)
jaccard_index_values = jaccard_instance.calculate_jaccard_index()
```

#### Get Most Relevant Stems for a Category

```python
category = "category1"
k = 5
top_k_stems = jaccard_instance.get_most_relevant_stems_for_category(category, k)
print(f"The top {k} stems for category {category} are: {top_k_stems}")
```

#### Get Most Relevant Categories for a Stem

```python
stem = "stem1"
k = 5
top_k_categories = jaccard_instance.get_most_relevant_categories_for_stem(stem, k)
print(f"The top {k} categories for stem {stem} are: {top_k_categories}")
```

### Example

```python
# Create a Jaccard Index calculator
jaccard_instance = jaccard_index(categories_dict, terms_dict, stems_dict)

# Calculate Jaccard Index
jaccard_index_values = jaccard_instance.calculate_jaccard_index()

# Get the top 5 stems for category "category1"
top_stems = jaccard_instance.get_most_relevant_stems_for_category("category1", 5)
print(f"The top 5 stems for category1 are: {top_stems}")

# Get the top 5 categories for stem "stem1"
top_categories = jaccard_instance.get_most_relevant_categories_for_stem("stem1", 5)
print(f"The top 5 categories for stem1 are: {top_categories}")
```

## MainConsole

The `MainConsole` class provides a command-line interface for interacting with the B+ tree and Jaccard Index functionality. It allows users to perform various operations such as retrieving relevant stems and categories, calculating Jaccard Index, saving data to files, and more.

### Usage

1. Run the application by executing the script.
2. Follow the on-screen instructions to choose an operation and provide any required parameters.

### Example

```python
# Run the application
MainConsole.main()
```

## Files I/O

The application supports reading pairs from files and writing results to files. The `read_files` class reads pairs from a file and stores them in the B+ tree, while the `write_files` class writes Jaccard Index results to a specified file in either JSON or XLSX format.

### Example

```python
# Read pairs from a file and store them in B+ tree
bpt_categories = BPlusTree(order=10)
returned_data = read_files.read_pairs_from_file("category_docId.txt", bpt_categories)

# Write Jaccard Index results to a file in JSON format
jaccard_instance = jaccard_index(categories_dict, terms_dict, stems_dict)
jaccard_index_values = jaccard_instance.calculate_jaccard_index()
writer = write_files("output", jaccard_index_values, "json")
writer.write_to_file()
```

## Conclusion

This application combines the efficiency of a B+ tree for managing large datasets with the utility of the Jaccard Index for measuring similarity between sets. The command-line interface provides a user-friendly way to interact with the functionality and perform various operations on the stored data.

**Contributions:**
- **Profiling:** [Barbara Riga](https://github.com/BarbaraRiga) - Barbara has conducted the profiling section, focusing on measuring the performance characteristics of the code.
- **Refactoring:** [Thano Panou](https://github.com/Thanospa2002) - Thanos has contributed to the refactoring phase, enhancing the code's structure and maintainability.

**License:**
GNU General Public License v3.0
