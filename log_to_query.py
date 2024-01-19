import argparse
import datetime
import re
from dataclasses import dataclass, field

__version__ = "0.0.1"


@dataclass
class Args(object):
    """Args"""

    placeholder_query: str
    params_text: str


class QueryParameterError(Exception):
    """QueryParameterError"""


class NoMatchError(QueryParameterError):
    """NoMatchError"""

    def __init__(self, source_text: str):
        self.source_text = source_text
        super().__init__(f"No match: {source_text}")


@dataclass
class QueryParameter(object):
    """QueryParameter"""

    value_text: str
    type_text: str

    """「'」で値を囲まなければSQLとして成立しない型かどうか"""
    need_quote_type: bool = field(init=False)

    @staticmethod
    def detect(param_text: str):
        """detect"""

        if param_text == "null":
            return QueryParameter("null", "null")

        # e.g. "test(String)" -> "test", "String"
        # e.g. "test(hello)(String)" -> "test(hello)", "String"
        match_obj = re.search("\(\w+\)$", param_text)
        if match_obj is None:
            raise NoMatchError(param_text)

        value_text = param_text[0 : match_obj.span()[0]]
        type_text = match_obj.group(0)[1:-1]  # e.g. (String) -> String
        return QueryParameter(value_text, type_text)

    def __post_init__(self):
        need_quote_types = ["String", "Date", "Time", "Timestamp"]
        self.need_quote_type = self.type_text in need_quote_types


@dataclass
class DetectedQuery(object):
    """QueryLogDetector"""

    placed_query: str
    params: list[QueryParameter]
    query: str  = field(init=False)

    @staticmethod
    def detect(query_log_text: str, param_log_text: str):
        """detect"""
        query_find = re.search("==>[ ]+Preparing:[ ]+", query_log_text)
        placed_query = query_log_text[query_find.span()[1] :]
        param_find = re.search("==>[ ]+Parameters:[ ]+", param_log_text)

        params_text = param_log_text[param_find.span()[1] :]
        # e.g. test(String), 1234(Integer), 5678(Long)

        raw_params = re.split(", +", params_text)
        # e.g. ["test(String)", "1234(Integer)", "5678(Long)" ]

        params: list[QueryParameter] = []
        for raw_param in raw_params:
            params.append(QueryParameter.detect(raw_param))

        return DetectedQuery(placed_query, params)

    def to_quote_text(self, target: str):
        safe_text = target.replace("'", "\\'")
        return f"'{safe_text}'"

    def __post_init__(self):
        self.query = self.placed_query
        for param in self.params:
            if param.need_quote_type:
                self.query = self.query.replace("?", self.to_quote_text(param.value_text), 1)
            else:
                self.query = self.query.replace("?", param.value_text, 1)


def main():
    """Query log(placeholder query + params) to query."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument(
        "placeholder_query",
        type=str,
        help="Placeholder query log. e.g. '... Preparing: UPDATE my_table SET name = ?, value = ? WHERE id = ?'",
    )
    parser.add_argument(
        "params_text",
        type=str,
        help="Parameters log. e.g. '... Parameters: test(String), 1234(Integer), 5678(Long)'",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
        help="Show version and exit",
    )
    args = parser.parse_args()  # type: Args

    local_timezone = datetime.datetime.now().astimezone().tzinfo
    start_datetime = datetime.datetime.now(local_timezone)
    start_datetime_text = start_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    result = DetectedQuery.detect(args.placeholder_query, args.params_text)
    print(result.query)


if __name__ == "__main__":
    main()
