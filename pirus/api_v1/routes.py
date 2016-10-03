#!env/python3
# coding: utf-8


from framework import *
from config import *
from .handlers import *







# Handlers instances
websocket = WebsocketHandler()
website = WebsiteHandler()
runHdl = RunHandler()
pipeHdl = PipelineHandler()

# Config server app
app['websockets'] = []

# On shutdown, close all websockets
app.on_shutdown.append(on_shutdown)




# Routes
app.router.add_route('GET',    "/v1/www", website.home)
app.router.add_route('GET',    "/v1/ws", websocket.get)

app.router.add_route('GET',    "/v1/pipeline", pipeHdl.get)
app.router.add_route('POST',   "/v1/pipeline", pipeHdl.post)
app.router.add_route('DELETE', "/v1/pipeline/{pipe_id}", pipeHdl.delete)
app.router.add_route('GET',    "/v1/pipeline/{pipe_id}", pipeHdl.get_details)
app.router.add_route('GET',    "/v1/pipeline/{pipe_id}/qml", pipeHdl.get_qml)
app.router.add_route('GET',    "/v1/pipeline/{pipe_id}/config", pipeHdl.get_config)

app.router.add_route('GET',    "/v1/run", runHdl.get)
app.router.add_route('POST',   "/v1/run", runHdl.post)
app.router.add_route('GET',    "/v1/run/{run_id}", runHdl.get_status)
app.router.add_route('GET',    "/v1/run/{run_id}/status", runHdl.get_status)
app.router.add_route('GET',    "/v1/run/{run_id}/log", runHdl.get_log)
app.router.add_route('GET',    "/v1/run/{run_id}/err", runHdl.get_err)
app.router.add_route('GET',    "/v1/run/{run_id}/files", runHdl.get_files)
app.router.add_route('GET',    "/v1/run/{run_id}/file/{filename}", runHdl.get_file)

app.router.add_route('GET',    "/v1/run/notify/{run_id}/{complete}", runHdl.up_progress)
app.router.add_route('GET',    "/v1/run/notify/{run_id}/status/{status}", runHdl.up_status)


app.router.add_static('/assets', TEMPLATE_DIR)