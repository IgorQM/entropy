import string
import datetime
from results import Graph, Node, Result, Metadatum, DataReader, DataReaderQuery
from random import choice

from results.impl import NodeTypes

now = datetime.datetime.now


def test_save_single_result(results_connector):
    expected = Result(graph_id=1, node_id=1, user_id='Dan', start_time=now(),
                      end_time=now(),
                      name="this",
                      val='that')
    results_connector.save(expected)
    reader = DataReader(results_connector)
    assert expected == reader.fetch_first(DataReaderQuery(graph_id=1))


def test_save_multiple_results(results_connector):
    expected = [Result(graph_id=1, node_id=x, user_id='Name', start_time=now(),
                       end_time=now(),
                       name="this",
                       val='that') for x in range(10)]
    results_connector.save(expected)
    reader = DataReader(results_connector)
    assert expected == reader.fetch(DataReaderQuery(graph_id=1))


def test_fetch_by_graph_id(results_connector):
    expected = Result(graph_id=100, node_id=1, user_id='Name', start_time=now(),
                      end_time=now(),
                      name="this",
                      val='that')
    results_connector.save(expected)
    reader = DataReader(results_connector)
    assert expected == reader.fetch_first(DataReaderQuery(graph_id=100))


def test_fetch_by_graph_and_node_id(results_connector):
    expected = Result(graph_id=100, node_id=2, user_id='Name', start_time=now(),
                      end_time=now(),
                      name="this",
                      val='that')
    results_connector.save(expected)
    reader = DataReader(results_connector)
    assert expected == reader.fetch_first(DataReaderQuery(graph_id=100, node_id=2))


def test_save_node(results_connector):
    expected = Node(graph_id=100, node_id=2, node_type=NodeTypes.Py, version='1', node_name='me')
    results_connector.save(expected)
    reader = DataReader(results_connector)
    assert expected == reader.fetch_first(DataReaderQuery(table='Nodes', node_id=2))


def test_fetch_result_by_node_name(results_connector):
    node1 = Node(graph_id=1, node_id=1, node_type=NodeTypes.Py, version='1', node_name='test_name')
    node2 = Node(graph_id=1, node_id=2, node_type=NodeTypes.Py, version='1', node_name='test_name2')
    res1 = Result(graph_id=1, node_id=1, user_id='Name', start_time=now(),
                  end_time=now(),
                  name="this",
                  val="that")
    res2 = Result(graph_id=1, node_id=2, user_id='Name', start_time=now(),
                  end_time=now(),
                  name="this",
                  val="that")
    results_connector.save([node1, node2, res1, res2])
    reader = DataReader(results_connector)
    assert res1 == reader.fetch_first(DataReaderQuery(table='Results', node_name='test_name'))


def test_fetch_metadata_by_node_name(results_connector):
    metadat = [Metadatum(graph_id=1, node_id=x, name='val_name', val=str(x)) for x in range(10)]

    node = Node(graph_id=1, node_id=1, node_type=NodeTypes.Py, version='1', node_name='test_name')

    results_connector.save([*metadat, node])
    reader = DataReader(results_connector)
    assert metadat == reader.fetch(DataReaderQuery(table='Metadata', node_name='test_name'))


def test_fetch_result_by_graph_name(results_connector):
    g1 = Graph(graph_id=1, graph_name='test1', graph_script='', graph_dot_repr='')
    g2 = Graph(graph_id=2, graph_name='test2', graph_script='', graph_dot_repr='')
    res1 = [Result(graph_id=1, node_id=x, user_id='User', start_time=now(), end_time=now(), name='a',
                   val='a') for x in range(10)]
    res2 = [Result(graph_id=2, node_id=x, user_id='User', start_time=now(), end_time=now(), name='a',
                   val='a') for x in range(10)]

    results_connector.save([g1, g2, *res1, *res2])

    reader = DataReader(results_connector)
    assert res1 == reader.fetch(DataReaderQuery(graph_name='test1'))


def test_fetch_metadata_by_res_size(results_connector):
    val = ''.join(choice(string.digits + string.ascii_letters) for i in range(int(1e4)))
    res = Result(graph_id=1, node_id=1, user_id='Name', start_time=now(),
                 end_time=now(),
                 name="this",
                 val=val)

    results_connector.save(res)
    reader = DataReader(results_connector)
    assert res == reader.fetch_first(DataReaderQuery(min_size=int(1e4)))