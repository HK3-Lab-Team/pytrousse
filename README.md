# pd_extras

This library is meant to be used to preprocess medical databases with many features/columns.

Library with useful wrapping for pandas DataFrame. It allows the user to have synthetic info about data, and to preprocess the DataFrame.


### Goal
The goals of this library are:
1. dealing with DataFrames with many features (e.g.: with values from many clinical exams) keeping track of 
the applied transformations
2. offering basic operations for data preprocessing like: encoding, bin splitting, correcting some typos, 
formatting features fixing wrong formats/types
3. providing basic informations about the database (columns count per type, trivial columns, ...)

Regarding 1), the idea is to have a base wrapper 'DataFrameWithInfo' for pandas.DataFrame that analyzes the dataset 
and gives synthetic infos about data (like type of columns, trivial columns, ...).
This class is used as input for many functions of the library and it tracks the operations performed on each feature.
