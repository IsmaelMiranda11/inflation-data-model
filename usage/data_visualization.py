import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from sqlalchemy import create_engine

from pathlib import Path
import os
os.chdir(Path(__file__).parent)

def get_data():
    engine = create_engine(
            'postgresql+psycopg2://'
            'postgres:postgres123'
            '@localhost:5432'
    )

    query = '''
        select
            cal.month_abbr || '/' || cal.year as month,
            i.ipca_accumulated_12_months_variation as value
        from
            inflation i
        join categories cat
                using (category_id)
        join cities cit
                using (city_id)
        join calendar cal on
            cal."date" = i.month_date
        where
            cat."level" = 0
            and cit.city_name = 'São Paulo'
            and i.ipca_accumulated_12_months_variation is not null
    '''

    with engine.connect() as conn: #type: ignore
        return pd.read_sql_query(query, con=conn.connection)

def plot_data(data: pd.DataFrame):
    sns.set_theme(style='darkgrid')

    plt.figure(figsize=(10, 3))

    sns.lineplot(x='month', y='value', data=data, color='gray')

    plt.title('IPCA Accumulated 12 Months Variation in São Paulo since 2020')
    plt.xlabel('Month')

    plt.ylabel('Inflation (%)')
    plt.yticks(fontsize=8)

    plt.xticks(rotation=90)
    plt.xticks(fontsize=8)

    # Only show january, june and december
    plt.xticks([i for i in range(0, len(data), 6)], 
               [data['month'][i] for i in range(0, len(data), 6)])

    # Show the last month
    plt.xticks([i for i in range(0, len(data), 6)] + [len(data) - 1], 
               [data['month'][i] for i in range(0, len(data), 6)] + 
               [data['month'][len(data) - 1]]
    )

    # Shade the area of the plot
    plt.fill_between(data['month'][0:13], data['value'][0:13], 
                     color='skyblue', alpha=0.4)
    plt.fill_between(data['month'][12:25], data['value'][12:25], 
                     color='lightgreen', alpha=0.4)
    plt.fill_between(data['month'][24:37], data['value'][24:37], 
                     color='lightcoral', alpha=0.4)
    plt.fill_between(data['month'][36:], data['value'][36:], 
                     color='lightgray', alpha=0.4)

    # Put a label in the middle of the shaded area
    plt.text('Jun/2021', 2, '2021', fontsize=10, ha='center') #type: ignore
    plt.text('Jun/2022', 2, '2022', fontsize=10, ha='center') #type: ignore
    plt.text('Jun/2023', 2, '2023', fontsize=10, ha='center') #type: ignore

    # Initiate the y axis in 0
    plt.ylim(0, 20)

    # Put values into lines to make it easier to read only for January, June and
    # December
    for i, txt in enumerate(data['value']):
        if i % 6 == 0:
            plt.annotate(f'{txt:.1f}%', (data['month'][i], txt), fontsize=10,
                         textcoords="offset points", xytext=(0,10), ha='center'
            )
            # Connect with line to label
            plt.plot([data['month'][i], data['month'][i]], [0, txt],
                     color='black', linestyle=':', linewidth=0.5)
        # Put a label in the last value
        if i == len(data) - 1:
            plt.annotate(f'{txt:.1f}%', (data['month'][i], txt), fontsize=10,
                         textcoords="offset points", xytext=(0,10), ha='center'
            )
            # Connect with line to label
            plt.plot([data['month'][i], data['month'][i]], [0, txt],
                     color='black', linestyle=':', linewidth=0.5)

    # export the plot as png
    plt.savefig('ipca_variation.png', dpi=800, bbox_inches='tight')

def main():
    data = get_data()
    plot_data(data)

if __name__ == '__main__':
    main()