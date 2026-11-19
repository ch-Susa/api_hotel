from contextlib import asynccontextmanager
from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from database import (reservas_collection, verificar_conexion)
from models import (ReservaCreate, ReservaUpdate, ReservaResponse)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await verificar_conexion()
    yield

app = FastAPI(
    title="API de Reservas de Hotel",
    description="Sistema de gestión de reservas de hotel",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def validar_objectid(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="El identificador proporcionado no es válido"
        )

    return ObjectId(id)

@app.get("/")
async def inicio():
    return {
        "mensaje": "API de Reservas de Hotel funcionando"
    }

@app.post(
    "/reservas",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED
)
async def crear_reserva(reserva: ReservaCreate):

    datos = reserva.model_dump()

    # Comprobar si existe una reserva idéntica
    existente = await reservas_collection.find_one(datos)

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Esta reserva ya existe"
        )

    resultado = await reservas_collection.insert_one(datos)

    nueva_reserva = await reservas_collection.find_one(
        {"_id": resultado.inserted_id}
    )

    return nueva_reserva

@app.get(
    "/reservas",
    response_model=list[ReservaResponse]
)
async def listar_reservas():

    cursor = reservas_collection.find()

    reservas = []

    async for documento in cursor:
        reservas.append(documento)

    return reservas

@app.get(
    "/reservas/{id}",
    response_model=ReservaResponse
)
async def obtener_reserva(id: str):

    object_id = validar_objectid(id)

    reserva = await reservas_collection.find_one(
        {"_id": object_id}
    )

    if reserva is None:
        raise HTTPException(
            status_code=404,
            detail="Reserva no encontrada"
        )

    return reserva

@app.put(
    "/reservas/{id}",
    response_model=ReservaResponse
)
async def actualizar_reserva(
    id: str,
    datos: ReservaUpdate
):

    object_id = validar_objectid(id)

    cambios = datos.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="No se proporcionaron datos para actualizar"
        )

    resultado = await reservas_collection.update_one(
        {"_id": object_id},
        {"$set": cambios}
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Reserva no encontrada"
        )

    reserva_actualizada = await reservas_collection.find_one(
        {"_id": object_id}
    )

    return reserva_actualizada

@app.delete("/reservas/{id}")
async def eliminar_reserva(id: str):

    object_id = validar_objectid(id)

    resultado = await reservas_collection.delete_one(
        {"_id": object_id}
    )

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Reserva no encontrada"
        )

    return {
        "mensaje": "Reserva eliminada correctamente"
    }