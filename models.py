from typing import Annotated, Optional
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import core_schema

class _ObjectIdPydanticAnnotation:

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler
    ):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern="^[0-9a-fA-F]{24}$"
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(
                        pattern="^[0-9a-fA-F]{24}$"
                    ),
                    core_schema.no_info_plain_validator_function(
                        ObjectId
                    )
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str
            )
        )

PyObjectId = Annotated[
    ObjectId,
    _ObjectIdPydanticAnnotation
]

class ReservaBase(BaseModel):

    nombre_huesped: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    numero_habitacion: int = Field(
        ...,
        gt=0
    )

    noches: int = Field(
        ...,
        gt=0
    )

    confirmada: bool = False

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):

    nombre_huesped: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    numero_habitacion: Optional[int] = Field(
        default=None,
        gt=0
    )

    noches: Optional[int] = Field(
        default=None,
        gt=0
    )

    confirmada: Optional[bool] = None

class ReservaResponse(ReservaBase):

    id: PyObjectId = Field(alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )