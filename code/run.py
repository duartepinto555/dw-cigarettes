import data_treatment
import generate_currency
import generate_purchases_and_stocks
import generate_sql_queries
import utils

# Setting the random seed to a fixed value so we can reproduce the same results
generate_purchases_and_stocks.np.random.seed(0)


# Execute all scripts
@utils.log_wrapper
def main():
    data_treatment.main()
    generate_currency.main()
    generate_purchases_and_stocks.main()
    generate_sql_queries.main() 


if __name__ == '__main__':
    # purchases = utils.pd.read_feather('datasets/purchases.feather')
    # utils.generate_sql(purchases, 'purchases', f'sql_queries\\purchases.sql', )
    main()