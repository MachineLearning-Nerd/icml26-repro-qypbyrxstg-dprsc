import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    return mo, np, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Differential privacy for range subgraphs

    **Central reproduced result:** across the full released-data accuracy
    protocol, the proposed method has lower mean relative error in
    **144/144 privacy-matched comparisons**. The chart immediately below
    embeds the epsilon-2 evidence, so opening this notebook does not rerun
    the expensive experiments.
    """)
    return


@app.cell
def _():
    embedded_accuracy = {
        "CA": {
            "edge": [11.4722339781, 1.4719344553],
            "2-star": [11.6307333505, 1.4933287351],
            "triangle": [11.6454906360, 1.6315108134],
        },
        "Wiki": {
            "edge": [231.1142145740, 4.9072790729],
            "2-star": [231.4450484430, 4.9170645255],
            "triangle": [231.3952863810, 5.0256497760],
        },
        "Worm": {
            "edge": [883.6862617730, 9.4800718620],
            "2-star": [884.0103117877, 9.4948936612],
            "triangle": [884.0018058610, 9.2097907690],
        },
    }
    return (embedded_accuracy,)


@app.cell
def _(embedded_accuracy, np, plt):
    accuracy_labels = [
        f"{dataset}\n{pattern}"
        for dataset, patterns in embedded_accuracy.items()
        for pattern in patterns
    ]
    accuracy_pure = [
        values[0]
        for patterns in embedded_accuracy.values()
        for values in patterns.values()
    ]
    accuracy_approx = [
        values[1]
        for patterns in embedded_accuracy.values()
        for values in patterns.values()
    ]
    accuracy_x = np.arange(len(accuracy_labels))
    accuracy_fig, accuracy_ax = plt.subplots(figsize=(10, 5))
    accuracy_ax.bar(
        accuracy_x - 0.19,
        accuracy_pure,
        0.38,
        color="#155e75",
        label="PDP_Comp / PDP_RSC",
    )
    accuracy_ax.bar(
        accuracy_x + 0.19,
        accuracy_approx,
        0.38,
        color="#f59e0b",
        label="ADP_Comp / ADP_RSC",
    )
    accuracy_ax.axhline(1, color="#991b1b", linestyle="--")
    accuracy_ax.set_yscale("log")
    accuracy_ax.set_xticks(accuracy_x, accuracy_labels)
    accuracy_ax.set_ylabel("baseline error ÷ proposed error")
    accuracy_ax.set_title("Paper-protocol accuracy at ε=2")
    accuracy_ax.legend(frameon=False, ncols=2)
    accuracy_ax.grid(axis="y", which="both", alpha=0.2)
    accuracy_fig
    return


@app.cell
def _(mo):
    mo.md(r"""
    A ratio above one means the proposed method has lower error. Pure DP
    improves by **11.47x–884.01x** in these epsilon-2 cells; approximate DP
    improves by **1.47x–9.49x**. The complete campaign repeats the
    comparison for eight epsilon values, three datasets, three patterns,
    and both privacy regimes.

    ## What is being counted?

    A query selects vertices whose public attribute lies in an interval,
    then asks for the number of edges, 2-stars, or triangles in the induced
    subgraph. A composition baseline filters and counts for every query.
    The proposed method instead projects pattern occurrences into a range
    tree, adds noise once to released tree nodes, and answers later
    intervals by post-processing canonical nodes.
    """)
    return


@app.cell
def _(mo):
    selected_dataset = mo.ui.dropdown(
        options=["CA-Netscience", "Wiki-Squirrel", "WormNet-v3"],
        value="WormNet-v3",
        label="Inspect epsilon-2 means",
    )
    selected_dataset
    return (selected_dataset,)


@app.cell
def _(mo, selected_dataset):
    embedded_means = {
        "CA-Netscience": [
            ["edge", 0.580027, 6.654207, 0.503825, 0.741597],
            ["2-star", 40.235248, 467.965440, 25.250186, 37.706829],
            ["triangle", 290.829430, 3386.851416, 2408.085135, 3928.810545],
        ],
        "Wiki-Squirrel": [
            ["edge", 0.005220, 1.206435, 0.003855, 0.018917],
            ["2-star", 0.074014, 17.130047, 0.131410, 0.646151],
            ["triangle", 0.617721, 142.936833, 0.817817, 4.110057],
        ],
        "WormNet-v3": [
            ["edge", 0.001890, 1.668784, 0.001169, 0.011080],
            ["2-star", 0.115651, 102.236264, 0.033497, 0.318046],
            ["triangle", 1.722583, 1522.760634, 0.512518, 4.720184],
        ],
    }
    means_rows = embedded_means[selected_dataset.value]
    means_markdown = "\n".join(
        f"| {pattern} | {pdp_rsc:.6f} | {pdp_comp:.6f} | "
        f"{adp_rsc:.6f} | {adp_comp:.6f} |"
        for pattern, pdp_rsc, pdp_comp, adp_rsc, adp_comp in means_rows
    )
    mo.md(
        f"""
        | Pattern | PDP_RSC | PDP_Comp | ADP_RSC | ADP_Comp |
        | --- | ---: | ---: | ---: | ---: |
        {means_markdown}

        Values are embedded 20-repeat mean relative errors at epsilon 2. This
        interaction is exploratory; the formal evidence is the checked raw
        JSON produced by the fixed campaign command.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Why the theorem verdicts differ

    | Claim | Verdict | Reason |
    | --- | --- | --- |
    | Pure-DP Algorithms 1–3 | **VERIFIED / HIGH** | A universal analytic certificate proves projection identity, sensitivity, vector Laplace privacy, and maximum-error concentration; exhaustive and independent controls support it. |
    | Approximate-DP Algorithms 4–5 | **FALSIFIED / HIGH** | Algorithm 4 can return a negative value, which Algorithm 5 uses as a Laplace scale. Released NumPy raises `ValueError` on a valid input. |
    | Theorem 1.3 existence | **BLOCKED / LOW** | The named witness is invalid, but a flaw in one construction does not falsify an existential theorem over all algorithms. |
    | Theorem 1.4 lower bound | **BLOCKED / LOW** | The paper-specific reconstruction closes, but a cited partial-discrepancy transfer does not establish the written logarithmic exponent. |
    | Section 5 composite | **BLOCKED / MEDIUM** | Accuracy aligns fully; runtime speedups range from 2.18x to 10,640x, so “3–4 orders” is not uniform on this hardware. |

    The important methodological rule is that evidence must match the
    quantifier. Finite experiments can reproduce an empirical ordering;
    they cannot prove an asymptotic universal theorem. A construction-level
    counterexample can falsify the named algorithm; it cannot automatically
    falsify an existence claim.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Reproducibility

    The formal campaign uses one locked Python 3.12 environment and one
    fixed command:

    ```bash
    uv run --frozen python repro/src/run_campaign.py
    ```

    The full cumulative run used Hugging Face `cpu-upgrade`, no GPU,
    estimated 4 cores and 15–30 minutes, observed 64 logical CPUs, and
    completed the scientific suite in 1,036.093 seconds. Checkers exit
    nonzero on failure; 15 negative controls failed for their intended
    reasons.

    Continue with the
    [illustrated report](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc/blob/master/reports/dprsc-reproduction-2026-07-26/report.md)
    or inspect the
    [repository](https://github.com/MachineLearning-Nerd/icml26-repro-qypbyrxstg-dprsc).
    """)
    return


if __name__ == "__main__":
    app.run()
