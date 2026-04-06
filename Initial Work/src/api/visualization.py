import pandas as pd
import matplotlib.pyplot as plt


def visualize_my_risk(path, show_plot=False, output_path="risk_visualization.png"):
    # I switch to a non-interactive backend when I only want to save the chart,
    # because API environments usually do not have a screen to display plots.
    if not show_plot:
        plt.switch_backend("Agg")

    # I read only part of the dataset so the visualization stays quick enough
    # for exploration and API use during this early project stage.
    dataframe = pd.read_csv(path, nrows=1000)

    # I use mean plus three standard deviations as a simple beginner-friendly
    # rule for spotting unusually large values.
    price_mean = dataframe["ratio_to_median_purchase_price"].mean()
    price_std = dataframe["ratio_to_median_purchase_price"].std()
    limit_price = price_mean + (3 * price_std)

    distance_mean = dataframe["distance_from_home"].mean()
    distance_std = dataframe["distance_from_home"].std()
    limit_dist = distance_mean + (3 * distance_std)

    # I start everyone at zero risk points and then add points when a row
    # crosses one of the rough outlier thresholds.
    dataframe["risk_score"] = 0

    high_price_mask = dataframe["ratio_to_median_purchase_price"] > limit_price
    far_from_home_mask = dataframe["distance_from_home"] > limit_dist

    dataframe.loc[high_price_mask, "risk_score"] += 1
    dataframe.loc[far_from_home_mask, "risk_score"] += 1

    # I create the figure explicitly so I can control the chart size instead
    # of relying on plotting defaults that may differ across environments.
    plt.figure(figsize=(10, 6))

    colors = {0: "lightgray", 1: "orange", 2: "red"}

    for score in [0, 1, 2]:
        mask = dataframe["risk_score"] == score

        # I use a mask so I can plot each risk group with its own color and
        # label, which makes the chart easier for me to explain later.
        x_values = dataframe.loc[mask, "distance_from_home"]
        y_values = dataframe.loc[mask, "ratio_to_median_purchase_price"]

        plt.scatter(
            x_values,
            y_values,
            c=colors[score],
            label=f"Risk Score {score}",
            alpha=0.7,
        )

    plt.title("Multi-Variable Fraud Discovery Chart")
    plt.xlabel("Distance from Home")
    plt.ylabel("Price Ratio to Median")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)

    # I save the figure because this visualization is meant to become a project
    # output that other routes or reports can reuse.
    plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show_plot:
        plt.show()

    plt.close()
