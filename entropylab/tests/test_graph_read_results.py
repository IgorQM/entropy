import os

import numpy

from entropylab.api.graph import GraphHelper
from entropylab.graph_experiment import (
    Graph,
    PyNode,
)
from entropylab.results_backend.sqlalchemy.db import SqlAlchemyDB


def a():
    return {"x": 1}


def b():
    return {"y": numpy.array([1, 2, 3])}


def c():
    return {"z": 1.5}


def test_async_graph_single_data_reader():
    try:
        db = SqlAlchemyDB("test_running_db_graph.db")
        a1 = PyNode("a", a, output_vars={"x"})

        b1 = PyNode("b", b, output_vars={"y"})
        c1 = PyNode("c", c, output_vars={"z"})

        g = {a1, b1, c1}

        handle = Graph(None, g, "run_a").run(db)
        handle = Graph(None, g, "run_b").run(db)

        handle.dot_graph()
        handle.results.get_results_from_node("b", "y")
        handle.results.get_debug_record()

        # instead of execute - simulate

        reader = handle.results

        nodes_results = reader.get_results_from_node(node_label="c")
        for node_results in nodes_results:
            print(node_results.results)
            results = list(node_results.results)
            assert len(results) == 1
            assert results[0].label == "z"
            assert results[0].data == 1.5

        nodes_results = reader.get_results_from_node(node_label="b")
        for node_results in nodes_results:
            print(node_results.results)
            results = list(node_results.results)
            assert len(results) == 1
            assert results[0].label == "y"
            assert numpy.array_equal(results[0].data, numpy.array([1, 2, 3]))

    finally:
        print("deleting db")
        os.remove("test_running_db_graph.db")
        pass


def test_async_graph_multi_data_reader():
    try:
        db = SqlAlchemyDB("test_running_db_graph1.db")
        a1 = PyNode("a", a, output_vars={"x"})

        b1 = PyNode("b", b, output_vars={"y"})
        c1 = PyNode("c", c, output_vars={"z"})

        g = {a1, b1, c1}

        handle1 = Graph(None, g, "run_a").run(db)
        handle2 = Graph(None, g, "run_a").run(db)
        reader2 = handle2.results
        exp_id = reader2.get_experiment_info().id
        assert handle2.id == exp_id
        nodes_results = db.get_results_from_node(experiment_id=exp_id, node_label="c")
        for node_results in nodes_results:
            print(node_results.results)
            results = list(node_results.results)
            assert len(results) == 1
            assert results[0].label == "z"
            assert results[0].data == 1.5
    finally:
        print("deleting db")
        os.remove("test_running_db_graph1.db")
        pass
