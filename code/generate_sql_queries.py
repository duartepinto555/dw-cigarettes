import os
import pandas as pd
from utils import log_wrapper, generate_sql


@log_wrapper
def main(db_name = 'dw_cigarettes'):
    try:
        df = pd.read_feather('datasets/cigarettes_treated.feather')
        dim_time = pd.read_feather('datasets/dim_time.feather')
    except Exception as e:
        df = pd.read_csv('../datasets/cigarettes_treated.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        dim_time = pd.read_feather('../datasets/dim_time.feather')
    df = df.sort_values(by=['Year', 'Month', 'Day'])

    queries_directory = f'{__file__.split("\\")[:-1]}\\..\\sql_queries'
    
    # Generate SQL to create Database if not exists
    with open(f'{queries_directory}\\00-create_dbase.sql', 'w') as sql_file:
        sql_file.write(f'CREATE DATABASE IF NOT EXISTS {db_name};')

    # -------------------------------------------------------------
    # STORES TABLE

    columns = ['Store_ID2', 'Outlet_Type', 'Retail_Subtype']
    df_t = df[columns]
    df_t = df_t.drop_duplicates().reset_index(drop=True)

    sql_queries = [
        f"CREATE TABLE IF NOT EXISTS {db_name}.DIM_STORE (Store_ID INT,Outlet_Type VARCHAR(50), Retail_Subtype VARCHAR(50), PRIMARY KEY(Store_ID));"
    ]

    for row in range(len(df_t)):
        ins = f'INSERT INTO {db_name}.DIM_STORE (Store_ID, Outlet_Type, Retail_Subtype) VALUES ({df_t["Store_ID2"][row]}, "{df_t["Outlet_Type"][row]}", "{df_t["Retail_Subtype"][row]}");'
        sql_queries.append(ins)

    with open(f'{queries_directory}\\01-dim_store.sql', 'w') as sql_file:

        for query in sql_queries:
            sql_file.write(query + '\n')

    # -------------------------------------------------------------
    # LOCATION TABLE
            
    columns = ['Suburb_ID', 'Suburb', 'Province_ID', 'Province', 'City_ID', 'City', 'Country_ID', 'Country']
    df_t = df[columns]
    df_t = df_t.drop_duplicates().reset_index(drop=True)

    sql_queries = [
        f"CREATE TABLE IF NOT EXISTS {db_name}.DIM_LOCATION (Suburb_ID INT, Suburb VARCHAR(50), Province_ID INT, Province VARCHAR(50), City_ID INT, City VARCHAR(50), Country_ID INT, Country VARCHAR(50), PRIMARY KEY(Suburb_ID));"
    ]

    for row in range(len(df_t)):
        ins = f'INSERT INTO {db_name}.DIM_LOCATION (Suburb_ID, Suburb, Province_ID, Province, City_ID, City, Country_ID, Country) VALUES ({df_t["Suburb_ID"][row]}, "{df_t["Suburb"][row]}", {df_t["Province_ID"][row]},"{df_t["Province"][row]}", {df_t["City_ID"][row]},"{df_t["City"][row]}", {df_t["Country_ID"][row]},"{df_t["Country"][row]}");'
        sql_queries.append(ins)

    with open(f'{queries_directory}\\02-dim_location.sql', 'w') as sql_file:

        for query in sql_queries:
            sql_file.write(query + '\n')

    # -------------------------------------------------------------
    # TIME TABLE

    columns = ['Day_ID', 'Day', 'weekday', 'Month_ID', 'Month', 'Month_Name', 'Year_ID', 'Year']
    df_t = dim_time[columns]
    df_t = df_t.drop_duplicates().reset_index(drop=True)

    sql_queries = [
        f"CREATE TABLE IF NOT EXISTS {db_name}.DIM_TIME (Day_ID INT, Day INT, Weekday INT, Month_ID INT, Month INT, Month_Name VARCHAR(20), Year_ID INT, Year INT, PRIMARY KEY(Day_ID));"
    ]

    for row in range(len(df_t)):
        ins = f'INSERT INTO {db_name}.DIM_TIME (Day_ID, Day, Weekday, Month_ID, Month, Month_Name, Year_ID, Year) VALUES ({int(df_t["Day_ID"][row])}, {int(df_t["Day"][row])}, {int(df_t["weekday"][row])}, {int(df_t["Month_ID"][row])}, {int(df_t["Month"][row])}, "{df_t["Month_Name"][row]}", {int(df_t["Year_ID"][row])}, {int(df_t["Year"][row])});'
        sql_queries.append(ins)

    with open(f'{queries_directory}\\03-dim_time.sql', 'w') as sql_file:

        for query in sql_queries:
            sql_file.write(query + '\n')

    # -------------------------------------------------------------
    # PRODUCT TABLE

    columns = ['Product_ID', 'Product', 'Sub_Brand_ID', 'Sub_Brand', 'Brand_ID', 'Brand']
    df_t = df[columns]
    df_t = df_t.drop_duplicates().reset_index(drop=True)

    sql_queries = [
        f"CREATE TABLE IF NOT EXISTS {db_name}.DIM_PRODUCT (Product_ID INT, Product VARCHAR(50), Sub_Brand_ID INT, Sub_Brand VARCHAR(100), Brand_ID INT, Brand VARCHAR(50), PRIMARY KEY(Product_ID));"
    ]

    for row in range(len(df_t)):
        ins = f'INSERT INTO {db_name}.DIM_PRODUCT (Product_ID, Product, Sub_Brand_ID, Sub_Brand, Brand_ID, Brand) VALUES ({df_t["Product_ID"][row]}, "{df_t["Product"][row]}", {df_t["Sub_Brand_ID"][row]},"{df_t["Sub_Brand"][row]}", {df_t["Brand_ID"][row]}, "{df_t["Brand"][row]}");'
        sql_queries.append(ins)

    with open(f'{queries_directory}\\04-dim_product.sql', 'w') as sql_file:

        for query in sql_queries:
            sql_file.write(query + '\n')

    # -------------------------------------------------------------
    # SALES TABLE

    columns = ['Store_ID2', 'Suburb_ID', 'Day_ID', 'Product_ID', 'Quantity', 'Dollar_Price']
    df_t = df[columns]
    df_t = df_t.drop_duplicates().reset_index(drop=True)

    sql_queries = [
        f"CREATE TABLE IF NOT EXISTS {db_name}.SALES (Store_ID INT, Suburb_ID INT, Day_ID INT, Product_ID INT, Quantity INT, Price DECIMAL(10, 4), FOREIGN KEY (Store_ID) REFERENCES DIM_STORE(Store_ID), FOREIGN KEY (Suburb_ID) REFERENCES DIM_LOCATION(Suburb_ID), FOREIGN KEY (Day_ID) REFERENCES DIM_TIME(Day_ID), FOREIGN KEY (Product_ID) REFERENCES DIM_PRODUCT(Product_ID));"
    ]

    for row in range(len(df_t)):
        ins = f'INSERT INTO {db_name}.SALES (Store_ID, Suburb_ID, Day_ID, Product_ID, Quantity, Price) VALUES ({df_t["Store_ID2"][row]}, {df_t["Suburb_ID"][row]},{df_t["Day_ID"][row]}, {df_t["Product_ID"][row]}, {df_t["Quantity"][row]}, {df_t["Dollar_Price"][row]});'
        sql_queries.append(ins)

    with open(f'{queries_directory}\\05-sales.sql', 'w') as sql_file:

        for query in sql_queries:
            sql_file.write(query + '\n')

    # -------------------------------------------------------------
    # Purchases Table
    purchases = pd.read_feather('../datasets/purchases.feather') if os.path.isdir('../datasets') else pd.read_feather('datasets/purchases.feather')
    purchases = purchases[['Day_ID', 'Store_ID2', 'Product_ID', 'Quantity']]
    purchases = purchases.rename(columns = {'Store_ID2': 'Store_ID'})
    generate_sql(purchases, f'{db_name}.purchases', f'{queries_directory}\\06-purchases.sql', insert_every_row=True)

    # -------------------------------------------------------------
    # Stocks Table
    stocks = pd.read_feather('../datasets/stocks.feather') if os.path.isdir('../datasets') else pd.read_feather('datasets/stocks.feather')
    generate_sql(stocks[['Store_ID2', 'Product_ID', 'Day_ID', 'stock_qty']], f'{db_name}.stocks', f'{queries_directory}\\07-stocks.sql', insert_every_row=True)

if __name__ == '__main__':
    main(db_name = 'dw_cigarettes')
