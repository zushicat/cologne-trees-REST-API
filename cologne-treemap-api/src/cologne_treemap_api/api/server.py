import json
from typing import Any, Callable

from jsonrpc import JSONRPCResponseManager, dispatcher
from jsonrpc.exceptions import JSONRPCDispatchException, JSONRPCServerError
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException

from .exceptions import InternalError
from cologne_treemap_api.treemap import (
    geo_numbers_by_district_number,
    geo_numbers_by_suburb_number,
    geo_genus_numbers_by_suburb_number,
    geo_age_by_suburb_number,
    tree_attr_age_numbers,
    tree_attr_genus_numbers,
    tree_attr_name_german_numbers,
    tree_attr_name_german_numbers,
    tree_geo_name_german_suburb_numbers
)


def http_exception(req: Request, e: HTTPException) -> Response:
    return Response(
        json.dumps({"status": f"ERROR: {e.description}"}).encode(),
        content_type="application/json",
        status=e.code,
    )


def json_rpc_except(func: Callable) -> Callable:
    def func_wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(**kwargs)
        except JSONRPCDispatchException:
            raise
        except Exception as e:
            raise InternalError(f"INTERNAL ERROR: {e}")

    return func_wrapper


@Request.application
def application(request):
    try:
        dispatcher["geo.district_number.numbers"] = json_rpc_except(
            geo_numbers_by_district_number
        )
        dispatcher["geo.suburb_number.numbers"] = json_rpc_except(
            geo_numbers_by_suburb_number
        )
        dispatcher["geo.suburb_number.genus.numbers"] = json_rpc_except(
            geo_genus_numbers_by_suburb_number
        )
        dispatcher["geo.suburb_number.age"] = json_rpc_except(geo_age_by_suburb_number)
        
        dispatcher["tree.attr.age.numbers"] = json_rpc_except(tree_attr_age_numbers)
        dispatcher["tree.attr.genus.numbers"] = json_rpc_except(tree_attr_genus_numbers)
        dispatcher["tree.attr.name_german.numbers"] = json_rpc_except(tree_attr_name_german_numbers)
        
        dispatcher["tree.geo.name_german.suburb.numbers"] = json_rpc_except(tree_geo_name_german_suburb_numbers)
        
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        return Response(response.json, mimetype="application/json")
    except Exception as e:
        return Response(
            json.dumps({"status": f"ERROR: {e}"}).encode(),
            content_type="application/json",
        )
    except HTTPException as e:
        return http_exception(request, e)
