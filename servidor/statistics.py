from flask import Blueprint, jsonify

from .data_manager import DataManager
from .data_analyser import DataAnalyser


statistics = Blueprint('statistics', __name__)

data_manager = DataManager()
data_analyzer = DataAnalyser()


@statistics.route('/basic-analysis/<int:days_ago>/<string:graph_type>', methods=('GET',))
def home(days_ago, graph_type):
    ticket_data = data_manager.get_data()
    analyzed_ticket_data = data_analyzer.get_basic_analysis(ticket_data, days_ago, graph_type)
    return jsonify(analyzed_ticket_data)


@statistics.route('/raw-data', methods=('GET',))
def raw_data():
    data = data_manager.get_data()
    return data
