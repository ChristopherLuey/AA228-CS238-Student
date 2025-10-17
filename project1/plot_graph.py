"""
Plot Bayesian network structures stored in .gph format using NetworkX.

The .gph files list directed edges as CSV lines: "parent, child".
This script builds a DiGraph, lays it out, and renders the visualization.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Tuple

import matplotlib.pyplot as plt
import networkx as nx


def read_gph(path: Path) -> nx.DiGraph:
    graph = nx.DiGraph()
    with path.open("r") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            parts = [part.strip() for part in stripped.split(",")]
            if len(parts) != 2:
                raise ValueError(f"Malformed line in {path}: {stripped!r}")
            parent, child = parts
            graph.add_edge(parent, child)
    # ensure isolated nodes are included by scanning unique names
    unique_nodes = set()
    with path.open("r") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped:
                continue
            parts = [part.strip() for part in stripped.split(",")]
            unique_nodes.update(parts)
    for node in unique_nodes:
        graph.add_node(node)
    return graph


def hierarchical_layout(graph: nx.DiGraph) -> Dict[str, Tuple[float, float]]:
    if not nx.is_directed_acyclic_graph(graph):
        raise ValueError("Hierarchy layout only valid for DAGs.")
    levels: Dict[str, int] = {}
    for node in nx.topological_sort(graph):
        parents = list(graph.predecessors(node))
        if not parents:
            levels[node] = 0
        else:
            levels[node] = max(levels[parent] + 1 for parent in parents)
    max_level = max(levels.values()) if levels else 0
    nodes_by_level: Dict[int, list[str]] = {lvl: [] for lvl in range(max_level + 1)}
    for node, lvl in levels.items():
        nodes_by_level[lvl].append(node)
    pos: Dict[str, Tuple[float, float]] = {}
    for lvl in range(max_level + 1):
        nodes = nodes_by_level[lvl]
        if not nodes:
            continue
        spacing = 1.0 / max(len(nodes), 1)
        for idx, node in enumerate(nodes):
            pos[node] = (idx * spacing + spacing / 2, -lvl)
    # place isolated nodes (no predecessors and no successors) on top level
    for node in graph.nodes():
        if node not in pos:
            pos[node] = (0.5, 0.0)
    return pos


def choose_layout(graph: nx.DiGraph, kind: str, seed: int) -> Dict[str, Tuple[float, float]]:
    kind = kind.lower()
    if kind == "spring":
        return nx.spring_layout(graph, seed=seed)
    if kind == "kamada_kawai":
        return nx.kamada_kawai_layout(graph)
    if kind == "circular":
        return nx.circular_layout(graph)
    if kind == "shell":
        return nx.shell_layout(graph)
    if kind == "hierarchy":
        try:
            return hierarchical_layout(graph)
        except ValueError:
            # fallback gracefully if cycle detected
            return nx.spring_layout(graph, seed=seed)
    raise ValueError(f"Unknown layout '{kind}'.")


def parse_figsize(text: str) -> Tuple[float, float]:
    parts = text.lower().split("x")
    if len(parts) != 2:
        raise ValueError("Figure size must be formatted as <width>x<height>, e.g. 10x8.")
    try:
        return float(parts[0]), float(parts[1])
    except ValueError as exc:
        raise ValueError("Figure dimensions must be numeric.") from exc


def plot_graph(
    graph: nx.DiGraph,
    layout: str,
    figsize: Tuple[float, float],
    title: str | None,
    node_size: int,
    font_size: int,
    seed: int,
) -> None:
    pos = choose_layout(graph, layout, seed)
    plt.figure(figsize=figsize)
    ax = plt.gca()
    nx.draw_networkx_nodes(graph, pos, node_size=node_size, node_color="#E8F4FD", ax=ax)
    nx.draw_networkx_edges(graph, pos, arrowsize=20, edge_color="#333333", ax=ax)
    nx.draw_networkx_labels(graph, pos, font_size=font_size, font_color="black", ax=ax)
    ax.set_axis_off()
    if title:
        ax.set_title(title)
    plt.tight_layout()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot Bayesian networks from .gph files.")
    parser.add_argument("gph_path", type=Path, help="Path to the .gph file.")
    parser.add_argument(
        "--layout",
        default="hierarchy",
        choices=["hierarchy", "spring", "kamada_kawai", "circular", "shell"],
        help="Graph layout algorithm.",
    )
    parser.add_argument(
        "--figsize",
        default="10x8",
        help="Figure size as WIDTHxHEIGHT (inches).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Figure title.",
    )
    parser.add_argument(
        "--node-size",
        type=int,
        default=1500,
        help="Node size for drawing.",
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=10,
        help="Label font size.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for stochastic layouts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output image path (PNG, PDF, etc.).",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Disable interactive display; useful when saving to file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    graph = read_gph(args.gph_path)
    figsize = parse_figsize(args.figsize)
    title = args.title or args.gph_path.stem
    plot_graph(
        graph,
        layout=args.layout,
        figsize=figsize,
        title=title,
        node_size=args.node_size,
        font_size=args.font_size,
        seed=args.seed,
    )
    if args.output:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300)
        print(f"Saved plot to {output_path}")
    if not args.no_show:
        plt.show()
    plt.close()


if __name__ == "__main__":
    main()

