# -*- coding: utf-8 -*-
from uuid import uuid4
from typing import List, Optional
from os import getenv
import os
from typing_extensions import Annotated

from fastapi import Depends, FastAPI
from starlette.responses import RedirectResponse

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from .backends import Backend, RedisBackend, MemoryBackend, GCSBackend
from .model import Task, TaskRequest

app = FastAPI()

my_backend: Optional[Backend] = None


def get_backend() -> Backend:
    global my_backend  # pylint: disable=global-statement
    if my_backend is None:
        backend_type = getenv('BACKEND', 'redis')
        if backend_type == 'redis':
            my_backend = RedisBackend()
        elif backend_type == 'gcs':
            my_backend = GCSBackend()
        else:
            my_backend = MemoryBackend()
    return my_backend


@app.get('/')
def redirect_to_tasks() -> None:
    return RedirectResponse(url='/tasks')


@app.get('/tasks')
def get_tasks(backend: Annotated[Backend, Depends(get_backend)]) -> List[Task]:
    keys = backend.keys()

    tasks = []
    for key in keys:
        tasks.append(backend.get(key))
    return tasks

# @app.get('/tasks/{task_id}')
# def get_task(task_id: str,
#              backend: Annotated[Backend, Depends(get_backend)]) -> Task:
#     with tracer.start_as_current_span("get_task"):
#         return backend.get(task_id)

@app.get('/tasks/{task_id}')
def get_task(task_id: str,
             backend: Annotated[Backend, Depends(get_backend)]) -> Task:
    if 'CI' not in os.environ:
        with tracer.start_as_current_span("get_task"):
            return backend.get(task_id)
    else:
        return backend.get(task_id)


@app.put('/tasks/{item_id}')
def update_task(task_id: str,
                request: TaskRequest,
                backend: Annotated[Backend, Depends(get_backend)]) -> None:
    backend.set(task_id, request)


@app.post('/tasks')
def create_task(request: TaskRequest,
                backend: Annotated[Backend, Depends(get_backend)]) -> str:
    task_id = str(uuid4())
    backend.set(task_id, request)
    return task_id

# provider = TracerProvider()
# cloud_trace_exporter = CloudTraceSpanExporter()
# processor = BatchSpanProcessor(cloud_trace_exporter)
# provider.add_span_processor(processor)

# # Sets the global default tracer provider
# trace.set_tracer_provider(provider)

# # Creates a tracer from the global tracer provider
# tracer = trace.get_tracer("my.tracer.name")

# FastAPIInstrumentor.instrument_app(app)

if 'CI' not in os.environ:
    provider = TracerProvider()
    cloud_trace_exporter = CloudTraceSpanExporter()
    processor = BatchSpanProcessor(cloud_trace_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("my.tracer.name")
    FastAPIInstrumentor.instrument_app(app)
