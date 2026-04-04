from pathlib import Path

from visualization import visualize_my_risk


def run_multivariate_visualization(show_plot=False):
    """Generate the multivariate fraud chart using project-relative paths."""
    # I rebuild the project paths here so this helper can be run directly from
    # the command line without depending on where I launched Python from.
    backend_dir = Path(__file__).resolve().parent
    project_root = backend_dir.parent.parent
    input_path = project_root / "data" / "raw" / "transactions" / "card_transdata.csv"
    output_path = backend_dir / "outputs" / "risk_visualization.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # I delegate the plotting work to the visualization helper because I want
    # this file to focus on path setup and orchestration only.
    visualize_my_risk(
        str(input_path),
        show_plot=show_plot,
        output_path=str(output_path),
    )
    return output_path


if __name__ == "__main__":
    chart_path = run_multivariate_visualization(show_plot=False)
    print(f"Saved chart to: {chart_path}")
