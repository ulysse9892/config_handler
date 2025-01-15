# Basic layout

At the top level you have a dictionary of global values to be used by all steps, and a serie of steps to be executed by the main script.

The dictionary of global values is always named "$global", the steps can be named whatever you please.

So a config file looks something like this:


```yaml
$global:
  ──────
step1:
  ──────
step2:
  ──────
```
# Basic keywords

The config files work based on keywords:

- "$global:" allows you to call variables stored in the dictionary of global values. For example if you stored var:"my name" in $global, "$global:var" will return "my name"
- "$env:" allows you to call environment variables. For example if you stored var:"my name" in your environment, "$env:var" will return "my name"
- "$import:" with this one you'll store whatever function or class you wrote after it. For example, "$import:pandas.read_parquet" will store the mentioned function
- "$path:" can call an existing path and combine it with another. For example, if you've already stored path_output:"C:\output", you can write "$path:path_output:table.parquet" to get the path "C:\output\table.parquet"
- "$config:" allows you to call other config files, it can be combined with "$path:". For example if you have config.yml in the folder whose path is stored at path_config, you can load it with "$config:$path:path_config:config.yml"
- "$method:" allows you to call methods from classes. For example if you have a dataframe stored as "df", "$method:df:to_parquet" will get the "to_parquet" method


# Advanced:

You can also store object that are the product of executing a function or initializing a class.

To that you need to use the keywords "obj_name", for the function or class and "init_args" for its arguments.

For example, let's say you want to store a parquet file located at "C:\output\table.parquet" as a pandas dataframe.

You will need to write:

```yaml
df:
  obj_name: "$import:pandas.read_parquet"
  init_args:
    path: "C:\output\table.parquet"
```
With this, the dataframe will be available under the name df

# Executing steps

1. Basics
    
    The steps are basically series of functions to execute.
    
    Those functions are put in a list under the keyword "methods" where they will be executed in order.
    The function is put under the keyword "name" and its arguments under "args"
    
    It is possible for the product of one function to be reused by the next. To that the keyword "result" must be used and called.
    For example if using result: "df", df will be available with "$result:df" (It will also be available for the "$method" keyword)
    
    ```yaml
    $global:
      data:
        A:
          - 1
          - 2
        B:
          - 1
          - 2
    
    step1:
      methods:
        - name: "$import:pandas.DataFrame"
          result: df
          args:
            data: "$global:data"
        - name: "$import:pandas.melt"
          result: df1
          args:
            frame: "$result:df"
            id_vars: ['A']
            value_vars: ['B']
        - name: "$method:df1:to_parquet"
          args:
            path: "C:\output\table.parquet"
    ```
    
    Here, step1 created a dataframe using stored data, melted it into another dataframe with the second function, and exported it as a parquet file with the third.

   
2. Methods from classes

    It is also possible to initialize a class from a method and have it execute methods. To do so the keyword "from" must be used for initializing, and "$method" to call the method you want to execute
    
    ```yaml
    step1:
      obj_name: "$import:pandas.read_parquet"
      from:
        name: "$method:from_dict"
        args:
          data:
            A:
              - 1
              - 2
            B:
              - 1
              - 2
      methods:
        - name: "$method:to_parquet"
          args:
            path: "C:\output\table.parquet"
    ```
    
    Here a dataframe was initialized using from_dict, and it was exported as a parquet file using the "to_parquet" method

3. Combining tools

    All those tools are made to be combined and used together. Functions can be executed at the same time as methods from classes taking global values as argument, flexibility is key.


