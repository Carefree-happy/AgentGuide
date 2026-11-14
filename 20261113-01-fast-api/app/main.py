import random
from typing import Annotated, Literal
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, AfterValidator, Field

app = FastAPI()

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/create/items/")
async def create_item(item: Item):
    return item

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}

def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None, 
        Query(
            alias="item-query",
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            deprecated=True,
        ),
    ] = None,
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None
    ):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
        results["items"].append({"id": id, "name": item})
    return results

@app.get("/apples/{apple_id}")
async def read_apple(
    apple_id: Annotated[int, Path(title="The ID of the apple to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
    size: Annotated[float, Query(gt=0, lt=10.5)] = None
):
    results = {"apple_id": apple_id}
    if q:
        results.update({"q": q})
    if size:
        results.update({"size": size})
    return results

class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

@app.get("/oranges/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

