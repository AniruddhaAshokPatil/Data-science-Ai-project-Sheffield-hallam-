import pandas as pd
import matplotlib.pyplot as plt

def visualize_my_risk(path, show_plot=False, output_path="risk_visualization.png"):
    if not show_plot:
        plt.switch_backend("Agg")

    df = pd.read_csv(path, nrows=1000)

    limit_price = df['ratio_to_median_purchase_price'].mean() + \
                  (3 * df['ratio_to_median_purchase_price'].std())

    limit_dist = df['distance_from_home'].mean() + \
                 (3 * df['distance_from_home'].std())

    df['risk_score'] = 0

    df.loc[df['ratio_to_median_purchase_price'] > limit_price, 'risk_score'] += 1
    df.loc[df['distance_from_home'] > limit_dist, 'risk_score'] += 1

    plt.figure(figsize=(10,6))

    colors = {0:'lightgray',1:'orange',2:'red'}

    for score in [0,1,2]:
        mask = df['risk_score'] == score
        plt.scatter(df.loc[mask,'distance_from_home'],
                    df.loc[mask,'ratio_to_median_purchase_price'],
                    c=colors[score],
                    label=f'Risk Score {score}',
                    alpha=0.7)

    plt.title('Multi-Variable Fraud Discovery Chart')
    plt.xlabel('Distance from Home')
    plt.ylabel('Price Ratio to Median')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)

    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plot:
        plt.show()

    plt.close()
